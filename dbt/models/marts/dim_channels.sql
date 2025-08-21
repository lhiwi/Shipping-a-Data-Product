{{ config(materialized='table') }}

with stg as (
  select
    channel_name,
    message_ts
  from {{ ref('stg_telegram_messages') }}
  where channel_name is not null
)

select
  lower(channel_name)        as channel_key,
  channel_name,
  min(message_ts)            as first_seen_at,
  max(message_ts)            as last_seen_at,
  count(*)                   as message_count
from stg
group by 1,2
