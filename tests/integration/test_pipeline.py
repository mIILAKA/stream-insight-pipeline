from __future__ import annotations

import duckdb
import pytest

from stream_insight.pipeline import PipelineError, run_demo


@pytest.mark.integration
def test_demo_builds_expected_marts(tmp_path):
    result = run_demo(tmp_path)

    assert result.raw_counts["raw_chat_events"] == 960
    assert result.stream_summary_rows == 12
    assert result.clip_candidate_rows == 36
    with duckdb.connect(str(result.database_path), read_only=True) as connection:
        top_priority = connection.execute(
            "select min(priority_rank) from analytics_marts.mart_clip_candidates"
        ).fetchone()[0]
    assert top_priority == 1


@pytest.mark.integration
def test_dbt_rejects_invalid_candidate_interval(tmp_path):
    with pytest.raises(PipelineError, match="dbt build failed"):
        run_demo(tmp_path, invalid_case="candidate_interval")
