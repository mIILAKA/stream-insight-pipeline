with stream_totals as (
    select
        stream_id,
        count(*) as chat_event_count,
        round(avg(reaction_score), 2) as avg_reaction_score
    from {{ ref('stg_chat_events') }}
    group by stream_id
),
ranked_minutes as (
    select
        stream_id,
        minute_bucket,
        avg_reaction_score as peak_minute_score,
        row_number() over (
            partition by stream_id
            order by avg_reaction_score desc, minute_bucket
        ) as minute_rank
    from {{ ref('int_chat_by_minute') }}
)
select
    stream.stream_id,
    stream.channel_id,
    channel.channel_name,
    channel.language,
    stream.started_at,
    stream.duration_sec,
    totals.chat_event_count,
    totals.avg_reaction_score,
    peak.minute_bucket as peak_minute,
    peak.peak_minute_score
from {{ ref('stg_streams') }} as stream
inner join {{ ref('stg_channels') }} as channel
    on stream.channel_id = channel.channel_id
left join stream_totals as totals
    on stream.stream_id = totals.stream_id
left join ranked_minutes as peak
    on stream.stream_id = peak.stream_id
    and peak.minute_rank = 1
