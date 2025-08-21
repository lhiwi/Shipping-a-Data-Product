{{ config(materialized='table') }}

with stg as (
  select * from {{ ref('stg_telegram_messages') }}
),
dc as (
  select * from {{ ref('dim_channels') }}
)
select
  s.message_id,
  d.date_key,
  c.channel_key,
  s.channel_name,
  s.message_ts,
  s.message_text,
  s.has_image,
  s.image_path,
  -- basic derived metrics
  length(coalesce(s.message_text,'')) as message_length
from stg s
left join {{ ref('dim_dates') }} d on d.date_key = s.message_date
left join dc c on c.channel_name = s.channel_name
