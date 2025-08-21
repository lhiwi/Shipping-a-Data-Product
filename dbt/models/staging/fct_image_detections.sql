{{ config(materialized='table') }}

with det as (
  select * from {{ ref('stg_image_detections') }}
),
msg as (
  select * from {{ ref('stg_telegram_messages') }}
)
select
  d.detection_id,
  d.message_id,
  m.channel_name,
  m.message_ts,
  d.class_name,
  d.confidence,
  d.image_path,
  date_trunc('day', m.message_ts)::date as message_date
from det d
left join msg m on m.message_id = d.message_id
