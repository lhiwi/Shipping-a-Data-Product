with src as (
  select *
  from {{ source('raw', 'telegram_messages') }}
)
select
  id::bigint           as message_id,
  channel_name::text   as channel_name,
  message_text::text   as message_text,
  cast(message_date as timestamp) as message_ts,
  date_trunc('day', cast(message_date as timestamp))::date as message_date,
  coalesce(has_image, false) as has_image,
  image_path::text     as image_path
from src
