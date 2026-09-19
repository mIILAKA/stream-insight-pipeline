select
    candidate.candidate_id,
    candidate.stream_id,
    stream.channel_id,
    candidate.start_sec,
    candidate.end_sec,
    candidate.end_sec - candidate.start_sec as duration_sec,
    candidate.status,
    candidate.matching_event_count,
    candidate.avg_reaction_score,
    candidate.max_reaction_score,
    case
        when candidate.end_sec > candidate.start_sec
            and candidate.start_sec >= 0
            and candidate.end_sec <= stream.duration_sec
            then 'valid'
        else 'invalid'
    end as quality_status,
    row_number() over (
        partition by candidate.stream_id
        order by
            candidate.avg_reaction_score desc,
            candidate.matching_event_count desc,
            candidate.candidate_id
    ) as priority_rank
from {{ ref('int_candidate_scores') }} as candidate
inner join {{ ref('stg_streams') }} as stream
    on candidate.stream_id = stream.stream_id
