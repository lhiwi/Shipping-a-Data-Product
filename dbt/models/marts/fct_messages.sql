with m as (
  select * from {{ ref('stg_telegram_messages') }}
), dc as (
  select channel_name, channel_key from {{ ref('dim_channels') }}
)
select
  m.message_id,
  dc.channel_key,
  date_trunc('day', m.message_timestamp)::date as date_key,
  length(m.message_text) as message_length,
  m.has_image,
  m.image_path
from m
left join dc using (channel_name)