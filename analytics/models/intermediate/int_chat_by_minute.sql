select
    stream_id,
    date_trunc('minute', occurred_at) as minute_bucket,
    count(*) as chat_event_count,
    round(avg(reaction_score), 2) as avg_reaction_score,
    max(reaction_score) as max_reaction_score
from {{ ref('stg_chat_events') }}
group by stream_id, date_trunc('minute', occurred_at)
