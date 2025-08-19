select distinct
    channel_name,
    md5(channel_name) as channel_key
from {{ ref('stg_telegram_messages') }}