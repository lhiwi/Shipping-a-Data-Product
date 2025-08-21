import os, requests, pandas as pd, numpy as np, streamlit as st
import matplotlib.pyplot as plt

API = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Telegram Analytics – Finance-ready View", layout="wide")
st.title("Telegram Analytics – Finance-ready View")

# ---- Tabs: Overview / Explainability / Reliability ----
tab_overview, tab_explain, tab_reliability = st.tabs(["Overview", "Explainability", "Reliability & Audit"])

# -------------------- OVERVIEW TAB --------------------
with tab_overview:
    colA, colB = st.columns([2, 1])
    with colB:
        limit = st.number_input("Top terms limit", min_value=5, max_value=100, value=24, step=1)

    st.caption("Top frequently mentioned terms (from analytics.fct_messages)")
    try:
        r = requests.get(f"{API}/api/reports/top-products", params={"limit": limit}, timeout=30)
        terms = pd.DataFrame(r.json()) if r.ok else pd.DataFrame(columns=["term", "hits"])
    except Exception as e:
        terms = pd.DataFrame(columns=["term", "hits"])
        st.warning(f"API error fetching top terms: {e}")

    if not terms.empty:
        terms = terms.dropna().astype({"hits": int})
        st.bar_chart(terms.set_index("term")["hits"])
    else:
        st.info("No data available for top terms yet.")

    st.divider()

    # Channel activity
    ch = st.text_input("Channel (e.g., lobelia4cosmetics)", "lobelia4cosmetics")
    st.caption("Daily messages for a specific channel")
    try:
        r = requests.get(f"{API}/api/channels/{ch}/activity", timeout=30)
        activity = pd.DataFrame(r.json()) if r.ok else pd.DataFrame(columns=["date", "messages"])
    except Exception as e:
        activity = pd.DataFrame(columns=["date", "messages"])
        st.warning(f"API error fetching activity: {e}")

    if not activity.empty:
        activity["date"] = pd.to_datetime(activity["date"])
        activity = activity.sort_values("date")
        st.line_chart(activity.set_index("date")["messages"])
    else:
        st.info("No channel activity found (try another channel).")

# -------------------- EXPLAINABILITY TAB --------------------
with tab_explain:
    st.subheader("How the pipeline works (data lineage)")

    st.graphviz_chart("""
        digraph G {
          rankdir=LR;
          node [shape=box, style=rounded];

          T [label="Telegram Channels"];
          I [label="Ingestion (Telethon)\\nsrc/ingestion/scrape.py"];
          R [label="Raw Data Lake\\n(JSON, images)"];
          L [label="Loader\\nsrc/warehouse/load_raw.py"];
          P [label="Postgres\\n(raw schema)"];
          D [label="dbt Models\\n(staging + marts)"];
          Y [label="YOLOv8 Enrichment\\nsrc/enrichment/yolo.py"];
          A [label="FastAPI\\n/api/*"];
          S [label="Streamlit\\nDashboard"];

          T -> I -> R -> L -> P -> D -> A -> S;
          R -> Y -> P;
        }
    """)

    st.markdown("""
    **Why these insights?**  
    We derive the “top terms” directly from `analytics.fct_messages` using SQL tokenization.  
    This is intentionally simple and transparent: no hidden ML models—just aggregations your stakeholders can verify.  
    YOLO detections, when present, link visual content (e.g., packaging, items) to message IDs, improving confidence in trends.
    """)

    # Lightweight "feature transparency": show the most frequent words now (same as top terms).
    if not terms.empty:
        st.subheader("Feature transparency: which terms drive the chart?")
        top_k = min(10, len(terms))
        st.table(terms.head(top_k).rename(columns={"term": "token", "hits": "frequency"}))
    else:
        st.info("Run ingestion + dbt to populate messages first.")

# -------------------- RELIABILITY & AUDIT TAB --------------------
with tab_reliability:
    st.subheader("Pipeline health & reliability (live metrics)")

    # Ingestion metrics
    col1, col2, col3 = st.columns(3)
    try:
        r = requests.get(f"{API}/api/metrics/ingestion", timeout=30)
        m_ing = r.json() if r.ok else {}
    except Exception as e:
        m_ing = {}
        st.warning(f"API error fetching ingestion metrics: {e}")

    total_messages = int(m_ing.get("total_messages", 0) or 0)
    last_ts = m_ing.get("last_message_ts")
    col1.metric("Total messages", f"{total_messages:,}")
    col2.metric("Last message timestamp", last_ts if last_ts else "N/A")
    if m_ing.get("messages_by_channel"):
        top_ch = max(m_ing["messages_by_channel"], key=lambda x: x["count"])
        col3.metric("Top channel (by volume)", f"{top_ch['channel']} ({top_ch['count']:,})")
    else:
        col3.metric("Top channel (by volume)", "N/A")

    # Messages/day (last 14 days)
    st.caption("Messages per day (last 14 days)")
    if m_ing.get("messages_per_day_14d"):
        df = pd.DataFrame(m_ing["messages_per_day_14d"])
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        st.line_chart(df.set_index("date")["count"])
    else:
        st.info("No daily message history available yet.")

    st.divider()

    # Detections metrics
    st.subheader("YOLO detections health")
    try:
        r = requests.get(f"{API}/api/metrics/detections", timeout=30)
        m_det = r.json() if r.ok else {}
    except Exception as e:
        m_det = {}
        st.warning(f"API error fetching detections metrics: {e}")

    if not m_det or not m_det.get("has_table"):
        st.info("No detection table yet. Run enrichment to populate `raw.image_detections`.")
    else:
        colA, colB = st.columns(2)
        colA.metric("Total detections", f"{int(m_det.get('total_detections', 0)):,}")

        # Confidence histogram
        conf = pd.DataFrame(m_det.get("conf_hist", []))
        if not conf.empty:
            conf = conf.sort_values("bucket")
            conf["bucket_mid"] = conf["bucket"] / 10.0  # 1..10 → 0.1..1.0
            st.caption("YOLO confidence distribution (higher = more certain)")
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.bar(conf["bucket_mid"], conf["count"], width=0.07)
            ax.set_xlabel("Confidence (bins)")
            ax.set_ylabel("Detections")
            st.pyplot(fig)
        else:
            st.info("No detections found for confidence chart.")

        # Top classes
        topc = pd.DataFrame(m_det.get("top_classes", []))
        if not topc.empty:
            st.caption("Most frequently detected classes")
            st.bar_chart(topc.set_index("class")["count"])
        else:
            st.info("No top classes to show yet.")
