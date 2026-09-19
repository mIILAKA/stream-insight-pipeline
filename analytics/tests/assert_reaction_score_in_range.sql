select *
from {{ ref('stg_chat_events') }}
where reaction_score < 0
   or reaction_score > 100
