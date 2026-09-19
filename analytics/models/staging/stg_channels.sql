select
    cast(channel_id as varchar) as channel_id,
    cast(channel_name as varchar) as channel_name,
    lower(cast(language as varchar)) as language
from {{ source('raw', 'raw_channels') }}
