import os, requests, pandas as pd, streamlit as st

API = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Telegram Analytics", layout="wide")
st.title("Telegram Analytics – Finance-ready View")

col1, col2 = st.columns([2,1])
with col2:
    limit = st.number_input("Top terms limit", 5, 100, 20)
with col1:
    st.caption("Top frequently mentioned terms (from fct_messages)")

# Top terms
r = requests.get(f"{API}/api/reports/top-products", params={"limit": limit})
terms = pd.DataFrame(r.json()) if r.ok else pd.DataFrame(columns=["term", "hits"])
st.bar_chart(terms.set_index("term")["hits"]) if not terms.empty else st.info("No data")

st.divider()

# Channel activity
channel = st.text_input("Channel (e.g., lobelia4cosmetics)", "lobelia4cosmetics")
r = requests.get(f"{API}/api/channels/{channel}/activity")
activity = pd.DataFrame(r.json()) if r.ok else pd.DataFrame(columns=["date", "messages"])
if not activity.empty:
    activity["date"] = pd.to_datetime(activity["date"])
    activity = activity.sort_values("date")
    st.line_chart(activity.set_index("date")["messages"])
else:
    st.info("No channel activity found.")

st.divider()

# Search
q = st.text_input("Search messages", "paracetamol")
r = requests.get(f"{API}/api/search/messages", params={"query": q, "limit": 50})
msgs = pd.DataFrame(r.json()) if r.ok else pd.DataFrame()
st.dataframe(msgs) if not msgs.empty else st.info("No results for your query.")
