select
    cast(stream_id as varchar) as stream_id,
    cast(channel_id as varchar) as channel_id,
    cast(started_at as timestamp) as started_at,
    cast(duration_sec as integer) as duration_sec,
    cast(synthetic_source as varchar) as synthetic_source
from {{ source('raw', 'raw_streams') }}
