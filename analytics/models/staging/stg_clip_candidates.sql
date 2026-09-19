select
    cast(candidate_id as varchar) as candidate_id,
    cast(stream_id as varchar) as stream_id,
    cast(start_sec as integer) as start_sec,
    cast(end_sec as integer) as end_sec,
    lower(cast(status as varchar)) as status
from {{ source('raw', 'raw_clip_candidates') }}
