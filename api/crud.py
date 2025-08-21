from sqlalchemy.orm import Session
from sqlalchemy import text

# Top “products” as frequent terms. Simple example:
def top_terms(db: Session, limit: int = 10) -> list[tuple[str, int]]:
    # naive term extraction: split words from messages; better to precompute in dbt later
    sql = text("""
        with tokens as (
          select lower(unnest(string_to_array(regexp_replace(message_text, '[^a-zA-Z0-9 ]', ' ', 'g'), ' '))) as term
          from analytics.fct_messages
          where message_text is not null and length(message_text) > 0
        )
        select term, count(*) as hits
        from tokens
        where length(term) >= 3
        group by 1
        order by hits desc
        limit :limit
    """)
    rows = db.execute(sql, {"limit": limit}).all()
    return [(r[0], r[1]) for r in rows]

def channel_activity(db: Session, channel: str) -> list[tuple[str, int]]:
    sql = text("""
        select to_char(message_ts::date, 'YYYY-MM-DD') as d, count(*) as messages
        from analytics.fct_messages
        where lower(channel_name) = lower(:channel)
        group by 1
        order by 1 asc
    """)
    return db.execute(sql, {"channel": channel}).all()

def search_messages(db: Session, query: str, limit: int = 50):
    sql = text("""
        select message_id, channel_name, message_ts, substring(coalesce(message_text, ''), 1, 300) as snippet
        from analytics.fct_messages
        where message_text ilike :q
        order by message_ts desc
        limit :limit
    """)
    return db.execute(sql, {"q": f"%{query}%", "limit": limit}).all()
