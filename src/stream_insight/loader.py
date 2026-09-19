from __future__ import annotations

import csv
from pathlib import Path

import duckdb


class DataContractError(ValueError):
    """Raised when an input file does not satisfy the raw data contract."""


TABLES = {
    "raw_channels": (
        "channels.csv",
        ["channel_id", "channel_name", "language"],
    ),
    "raw_streams": (
        "streams.csv",
        ["stream_id", "channel_id", "started_at", "duration_sec", "synthetic_source"],
    ),
    "raw_chat_events": (
        "chat_events.csv",
        ["event_id", "stream_id", "occurred_at", "reaction_score", "event_type"],
    ),
    "raw_clip_candidates": (
        "clip_candidates.csv",
        ["candidate_id", "stream_id", "start_sec", "end_sec", "status"],
    ),
}


def _validate_headers(data_dir: Path) -> None:
    for _, (filename, required_columns) in TABLES.items():
        path = data_dir / filename
        if not path.is_file():
            raise DataContractError(f"missing input file: {filename}")
        with path.open(encoding="utf-8-sig", newline="") as handle:
            columns = csv.DictReader(handle).fieldnames or []
        missing = sorted(set(required_columns) - set(columns))
        if missing:
            raise DataContractError(f"{filename} is missing required columns: {', '.join(missing)}")


def load_raw_data(data_dir: Path | str, database_path: Path | str) -> dict[str, int]:
    """Replace raw tables atomically so repeated loads do not duplicate rows."""
    source = Path(data_dir)
    database = Path(database_path)
    _validate_headers(source)
    database.parent.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    with duckdb.connect(str(database)) as connection:
        connection.execute("begin transaction")
        try:
            for table_name, (filename, _) in TABLES.items():
                csv_path = (source / filename).resolve().as_posix().replace("'", "''")
                connection.execute(
                    f"""
                    create or replace table {table_name} as
                    select * from read_csv(
                        '{csv_path}',
                        header = true,
                        auto_detect = true,
                        sample_size = -1
                    )
                    """
                )
                counts[table_name] = connection.execute(
                    f"select count(*) from {table_name}"
                ).fetchone()[0]
            connection.execute("commit")
        except Exception:
            connection.execute("rollback")
            raise

    return counts
