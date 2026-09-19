select
    cast(event_id as varchar) as event_id,
    cast(stream_id as varchar) as stream_id,
    cast(occurred_at as timestamp) as occurred_at,
    cast(reaction_score as integer) as reaction_score,
    lower(cast(event_type as varchar)) as event_type
from {{ source('raw', 'raw_chat_events') }}
