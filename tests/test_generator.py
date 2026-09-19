from __future__ import annotations

import csv

from stream_insight.generator import generate_sample_data

EXPECTED_FILES = {
    "channels.csv",
    "streams.csv",
    "chat_events.csv",
    "clip_candidates.csv",
}


def test_generate_sample_data_is_deterministic(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"

    first_summary = generate_sample_data(first, seed=20260920)
    second_summary = generate_sample_data(second, seed=20260920)

    assert first_summary == second_summary
    assert first_summary.channels == 4
    assert first_summary.streams == 12
    assert first_summary.chat_events == 960
    assert first_summary.clip_candidates == 36
    assert {path.name for path in first.iterdir()} == EXPECTED_FILES
    for name in EXPECTED_FILES:
        assert (first / name).read_bytes() == (second / name).read_bytes()


def test_generated_channels_are_explicitly_synthetic(tmp_path):
    generate_sample_data(tmp_path)

    with (tmp_path / "channels.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert all(row["channel_name"].startswith("Synthetic Channel ") for row in rows)
    assert {row["language"] for row in rows} == {"en", "id", "ja", "multi"}


def test_invalid_fixture_is_generated_only_when_requested(tmp_path):
    generate_sample_data(tmp_path, invalid_case="candidate_interval")

    with (tmp_path / "clip_candidates.csv").open(encoding="utf-8", newline="") as handle:
        first = next(csv.DictReader(handle))

    assert int(first["end_sec"]) <= int(first["start_sec"])
