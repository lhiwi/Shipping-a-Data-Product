{{ config(materialized='table') }}

with limits as (
  select
    coalesce(min(message_date), current_date) as min_d,
    coalesce(max(message_date), current_date) as max_d
  from {{ ref('stg_telegram_messages') }}
),
series as (
  select generate_series(min_d, max_d, interval '1 day')::date as d
  from limits
)
select
  d as date_key,
  extract(isodow from d)::int    as iso_dow,
  to_char(d, 'Day')              as day_name,
  extract(week from d)::int      as iso_week,
  extract(month from d)::int     as month_num,
  to_char(d, 'Mon')              as month_name,
  extract(year from d)::int      as year
from series
