select
    candidate.candidate_id,
    candidate.stream_id,
    candidate.start_sec,
    candidate.end_sec,
    candidate.status,
    count(event.event_id) as matching_event_count,
    round(coalesce(avg(event.reaction_score), 0), 2) as avg_reaction_score,
    coalesce(max(event.reaction_score), 0) as max_reaction_score
from {{ ref('stg_clip_candidates') }} as candidate
left join {{ ref('stg_streams') }} as stream
    on candidate.stream_id = stream.stream_id
left join {{ ref('stg_chat_events') }} as event
    on candidate.stream_id = event.stream_id
    and event.occurred_at between
        stream.started_at + candidate.start_sec * interval '1 second'
        and stream.started_at + candidate.end_sec * interval '1 second'
group by
    candidate.candidate_id,
    candidate.stream_id,
    candidate.start_sec,
    candidate.end_sec,
    candidate.status
