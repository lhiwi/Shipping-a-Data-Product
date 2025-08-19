with src as (
    select * from {{ source('raw','telegram_messages') }}
)
select
    cast(id as bigint)           as message_id,
    cast(channel_name as text)   as channel_name,
    cast(message_text as text)   as message_text,
    cast(message_date as timestamp) as message_timestamp,
    cast(has_image as boolean)   as has_image,
    cast(image_path as text)     as image_path
from src