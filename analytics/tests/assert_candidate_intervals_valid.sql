select *
from {{ ref('stg_clip_candidates') }}
where start_sec < 0
   or end_sec <= start_sec
