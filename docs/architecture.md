# Architecture

## Goal

Show a complete analytical data path rather than a collection of unrelated scripts. Each layer has one responsibility and can be inspected in DuckDB.

## Stages

1. `generator.py` creates four deterministic CSV files. A local random-number generator is seeded without changing global random state.
2. `loader.py` checks file and column contracts, then replaces all raw tables in one transaction. Replacement makes reruns idempotent.
3. dbt staging models cast raw values into explicit types and normalize categorical text.
4. intermediate models calculate minute-level reactions and candidate-level event scores.
5. marts produce one stream summary and one ranked candidate table for downstream users.
6. generic and singular tests turn source assumptions and domain rules into executable checks.
7. `pipeline.py` exports small result samples so reviewers can inspect outputs without a DuckDB client.

## Failure boundaries

| Failure | Owner | Behavior |
|---|---|---|
| Missing file or required column | Python ingestion | Stop before changing the database |
| Duplicate or NULL identifiers | dbt generic tests | Build fails with the affected model/test |
| Orphan foreign key | dbt relationships tests | Build fails |
| Invalid clip interval | dbt singular test | Build fails |
| Score outside 0–100 | dbt singular test | Build fails |
| Event outside stream time | dbt singular test | Build fails |

## Schemas

- `main.raw_*`: exact ingested source shape inferred from CSV
- `analytics_staging.*`: typed and normalized records
- `analytics_intermediate.*`: reusable analytical calculations
- `analytics_marts.*`: tables intended for review or downstream consumption

## Reproducibility

- Input randomness is fixed by an explicit seed.
- `uv.lock` fixes resolved Python dependencies.
- raw tables use `create or replace` inside a transaction.
- CI regenerates every input and database from an empty runner.
- generated files and databases are ignored by Git.
