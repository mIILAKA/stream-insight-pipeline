# Data Dictionary

## channels

| Column | Type after staging | Description |
|---|---|---|
| channel_id | varchar | Synthetic key beginning with `syn_ch_` |
| channel_name | varchar | Explicitly fictional display name |
| language | varchar | `en`, `id`, `ja`, or `multi` |

## streams

| Column | Type after staging | Description |
|---|---|---|
| stream_id | varchar | Synthetic stream key |
| channel_id | varchar | Foreign key to channels |
| started_at | timestamp | Fictional stream start time |
| duration_sec | integer | Stream duration in seconds |
| synthetic_source | varchar | Always `generated` |

## chat_events

| Column | Type after staging | Description |
|---|---|---|
| event_id | varchar | Synthetic event key |
| stream_id | varchar | Foreign key to streams |
| occurred_at | timestamp | Event time within the stream |
| reaction_score | integer | Synthetic 0–100 reaction score |
| event_type | varchar | `message`, `reaction`, or `membership` |

## clip_candidates

| Column | Type after staging | Description |
|---|---|---|
| candidate_id | varchar | Synthetic candidate key |
| stream_id | varchar | Foreign key to streams |
| start_sec | integer | Candidate start from stream origin |
| end_sec | integer | Candidate end from stream origin |
| status | varchar | Human-review workflow state |
