from __future__ import annotations

import csv
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import duckdb

from stream_insight.generator import generate_sample_data
from stream_insight.loader import load_raw_data


class PipelineError(RuntimeError):
    """Raised when a pipeline stage cannot complete."""


@dataclass(frozen=True)
class DemoResult:
    database_path: Path
    raw_counts: dict[str, int]
    stream_summary_rows: int
    clip_candidate_rows: int
    examples_dir: Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _run_dbt_build(database_path: Path, work_dir: Path) -> None:
    dbt_executable = shutil.which("dbt")
    if not dbt_executable:
        raise PipelineError("dbt executable was not found; run `uv sync --all-groups`")

    root = _project_root()
    env = os.environ.copy()
    env["STREAM_INSIGHT_DB_PATH"] = str(database_path.resolve())
    command = [
        dbt_executable,
        "build",
        "--project-dir",
        str(root / "analytics"),
        "--profiles-dir",
        str(root / "analytics"),
        "--target-path",
        str((work_dir / "dbt_target").resolve()),
    ]
    completed = subprocess.run(
        command,
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        details = "\n".join((completed.stdout + completed.stderr).splitlines()[-30:])
        raise PipelineError(f"dbt build failed (exit {completed.returncode})\n{details}")


def _export_query(connection: duckdb.DuckDBPyConnection, query: str, path: Path) -> None:
    cursor = connection.execute(query)
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def run_demo(
    work_dir: Path | str = Path("build/demo"),
    *,
    invalid_case: str | None = None,
) -> DemoResult:
    """Run generation, raw loading, dbt transformations, tests, and example export."""
    work = Path(work_dir)
    data_dir = work / "data"
    database_path = work / "stream_insight.duckdb"
    examples_dir = work / "examples"
    examples_dir.mkdir(parents=True, exist_ok=True)

    generate_sample_data(data_dir, invalid_case=invalid_case)
    raw_counts = load_raw_data(data_dir, database_path)
    _run_dbt_build(database_path, work)

    with duckdb.connect(str(database_path)) as connection:
        stream_summary_rows = connection.execute(
            "select count(*) from analytics_marts.mart_stream_summary"
        ).fetchone()[0]
        clip_candidate_rows = connection.execute(
            "select count(*) from analytics_marts.mart_clip_candidates"
        ).fetchone()[0]
        _export_query(
            connection,
            "select * from analytics_marts.mart_stream_summary order by started_at limit 5",
            examples_dir / "stream_summary.csv",
        )
        _export_query(
            connection,
            """
            select * from analytics_marts.mart_clip_candidates
            order by stream_id, priority_rank
            limit 10
            """,
            examples_dir / "clip_candidates.csv",
        )

    return DemoResult(
        database_path=database_path.resolve(),
        raw_counts=raw_counts,
        stream_summary_rows=stream_summary_rows,
        clip_candidate_rows=clip_candidate_rows,
        examples_dir=examples_dir.resolve(),
    )
