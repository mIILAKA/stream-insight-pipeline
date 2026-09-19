from __future__ import annotations

import argparse
from pathlib import Path

from stream_insight.pipeline import PipelineError, run_demo


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synthetic livestream analytics pipeline")
    subcommands = parser.add_subparsers(dest="command", required=True)
    demo = subcommands.add_parser("demo", help="run generation, loading, dbt, and exports")
    demo.add_argument("--work-dir", type=Path, default=Path("build/demo"))
    demo.add_argument(
        "--invalid-case",
        choices=["candidate_interval"],
        help="inject a known defect to prove that quality tests fail",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        result = run_demo(args.work_dir, invalid_case=args.invalid_case)
    except PipelineError as error:
        print(error)
        return 1

    print("Pipeline completed")
    print(f"Database: {result.database_path}")
    print(f"Raw rows: {sum(result.raw_counts.values())}")
    print(f"Stream summaries: {result.stream_summary_rows}")
    print(f"Clip candidates: {result.clip_candidate_rows}")
    print(f"Examples: {result.examples_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
