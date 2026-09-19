select candidate.*
from {{ ref('stg_clip_candidates') }} as candidate
inner join {{ ref('stg_streams') }} as stream
    on candidate.stream_id = stream.stream_id
where candidate.end_sec > stream.duration_sec
