from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

def get_top_products(db: Session, limit: int = 10) -> List[dict]:
    sql = text(
        """

        with tokens as (
          select unnest(string_to_array(lower(message_text), ' ')) as token
          from analytics.fct_messages f
          join analytics.dim_channels c on f.channel_key = c.channel_key
        )
        select token as product, count(*) as mentions
        from tokens
        where token ~ '^[a-z]+' and length(token) > 3
        group by token
        order by mentions desc
        limit :limit
        """

    )
    rows = db.execute(sql, {"limit": limit}).mappings().all()
    return [dict(r) for r in rows]

def get_channel_activity(db: Session, channel_name: str) -> List[dict]:
    sql = text(
        """

        select date_trunc('day', m.message_timestamp) as day, count(*) as messages
        from analytics.fct_messages f
        join analytics.dim_channels c on f.channel_key = c.channel_key
        join staging.stg_telegram_messages m on m.message_id = f.message_id
        where c.channel_name = :channel_name
        group by 1
        order by 1
        """

    )
    rows = db.execute(sql, {"channel_name": channel_name}).mappings().all()
    return [dict(r) for r in rows]

def search_messages(db: Session, query: str) -> List[dict]:
    sql = text(
        """

        select m.message_id, c.channel_name, m.message_text, m.message_timestamp, m.has_image, m.image_path
        from staging.stg_telegram_messages m
        join analytics.dim_channels c on c.channel_name = m.channel_name
        where m.message_text ilike :q
        order by m.message_timestamp desc
        limit 200
        """

    )
    rows = db.execute(sql, {"q": f"%{query}%"}).mappings().all()
    return [dict(r) for r in rows]