select distinct
    date_trunc('day', message_timestamp)::date as date_key,
    extract(year from message_timestamp)::int  as year,
    extract(month from message_timestamp)::int as month,
    extract(day from message_timestamp)::int   as day
from {{ ref('stg_telegram_messages') }}