from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GenerationSummary:
    channels: int
    streams: int
    chat_events: int
    clip_candidates: int


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _iso_z(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_sample_data(
    output_dir: Path | str,
    *,
    seed: int = 20260920,
    invalid_case: str | None = None,
) -> GenerationSummary:
    """Generate deterministic, entirely fictional livestream data."""
    if invalid_case not in {None, "candidate_interval"}:
        raise ValueError(f"unsupported invalid_case: {invalid_case}")

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)

    languages = ["en", "id", "ja", "multi"]
    channels = [
        {
            "channel_id": f"syn_ch_{index:03d}",
            "channel_name": f"Synthetic Channel {index:02d}",
            "language": language,
        }
        for index, language in enumerate(languages, start=1)
    ]

    base_time = datetime(2026, 1, 1, 10, 0, tzinfo=UTC)
    streams: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    statuses = ["new", "reviewed", "approved", "rejected"]

    for stream_index in range(1, 13):
        stream_id = f"syn_stream_{stream_index:03d}"
        channel = channels[(stream_index - 1) % len(channels)]
        started_at = base_time + timedelta(days=stream_index - 1, hours=stream_index % 5)
        duration_sec = rng.randrange(2_700, 5_401, 300)
        streams.append(
            {
                "stream_id": stream_id,
                "channel_id": channel["channel_id"],
                "started_at": _iso_z(started_at),
                "duration_sec": duration_sec,
                "synthetic_source": "generated",
            }
        )

        stream_candidates: list[tuple[int, int]] = []
        for candidate_number, fraction in enumerate((0.2, 0.5, 0.75), start=1):
            start_sec = int(duration_sec * fraction) + rng.randint(-45, 45)
            clip_duration = rng.randrange(60, 181, 30)
            end_sec = min(start_sec + clip_duration, duration_sec)
            stream_candidates.append((start_sec, end_sec))
            candidates.append(
                {
                    "candidate_id": f"syn_candidate_{stream_index:03d}_{candidate_number}",
                    "stream_id": stream_id,
                    "start_sec": start_sec,
                    "end_sec": end_sec,
                    "status": statuses[(stream_index + candidate_number) % len(statuses)],
                }
            )

        offsets = sorted(rng.sample(range(duration_sec), 80))
        for event_number, offset_sec in enumerate(offsets, start=1):
            in_candidate = any(start <= offset_sec <= end for start, end in stream_candidates)
            base_score = rng.randint(8, 58)
            reaction_score = min(
                100, base_score + rng.randint(25, 42) if in_candidate else base_score
            )
            events.append(
                {
                    "event_id": f"syn_event_{stream_index:03d}_{event_number:03d}",
                    "stream_id": stream_id,
                    "occurred_at": _iso_z(started_at + timedelta(seconds=offset_sec)),
                    "reaction_score": reaction_score,
                    "event_type": rng.choice(["message", "reaction", "membership"]),
                }
            )

    if invalid_case == "candidate_interval":
        candidates[0]["end_sec"] = candidates[0]["start_sec"]

    _write_csv(
        output / "channels.csv",
        ["channel_id", "channel_name", "language"],
        channels,
    )
    _write_csv(
        output / "streams.csv",
        ["stream_id", "channel_id", "started_at", "duration_sec", "synthetic_source"],
        streams,
    )
    _write_csv(
        output / "chat_events.csv",
        ["event_id", "stream_id", "occurred_at", "reaction_score", "event_type"],
        events,
    )
    _write_csv(
        output / "clip_candidates.csv",
        ["candidate_id", "stream_id", "start_sec", "end_sec", "status"],
        candidates,
    )

    return GenerationSummary(
        channels=len(channels),
        streams=len(streams),
        chat_events=len(events),
        clip_candidates=len(candidates),
    )
