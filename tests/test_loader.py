from __future__ import annotations

import csv

import duckdb
import pytest

from stream_insight.generator import generate_sample_data
from stream_insight.loader import DataContractError, load_raw_data


def test_load_raw_data_is_idempotent(tmp_path):
    data_dir = tmp_path / "data"
    database = tmp_path / "stream_insight.duckdb"
    generate_sample_data(data_dir)

    first = load_raw_data(data_dir, database)
    second = load_raw_data(data_dir, database)

    assert (
        first
        == second
        == {
            "raw_channels": 4,
            "raw_streams": 12,
            "raw_chat_events": 960,
            "raw_clip_candidates": 36,
        }
    )
    with duckdb.connect(str(database), read_only=True) as connection:
        assert connection.execute("select count(*) from raw_chat_events").fetchone()[0] == 960


def test_load_raw_data_rejects_missing_required_column(tmp_path):
    data_dir = tmp_path / "data"
    generate_sample_data(data_dir)
    path = data_dir / "channels.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["channel_id", "channel_name"],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    with pytest.raises(DataContractError, match="language"):
        load_raw_data(data_dir, tmp_path / "broken.duckdb")
