select event.*
from {{ ref('stg_chat_events') }} as event
inner join {{ ref('stg_streams') }} as stream
    on event.stream_id = stream.stream_id
where event.occurred_at < stream.started_at
   or event.occurred_at >= stream.started_at + stream.duration_sec * interval '1 second'
