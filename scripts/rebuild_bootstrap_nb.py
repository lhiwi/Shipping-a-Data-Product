import nbformat as nbf
from pathlib import Path

nb = nbf.v4.new_notebook()
nb.cells = [
    nbf.v4.new_markdown_cell("# 01 — Bootstrap Telegram Session\nCreate a Telethon session so you don’t have to re‑login every time."),
    nbf.v4.new_code_cell("""import os
from dotenv import load_dotenv
from telethon import TelegramClient

# If this notebook is in notebooks/, .env is one level up
load_dotenv("../.env")

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
session_name = os.getenv("TELEGRAM_SESSION", "telegram_session")

client = TelegramClient(session_name, api_id, api_hash)

# Jupyter supports top-level await
await client.start()   # prompts for phone/code (and 2FA if set)
me = await client.get_me()
print(" Logged in as:", getattr(me, "username", None) or me.id)
await client.disconnect()
print(" Session file saved as:", f"{session_name}.session")"""),
]

out = Path("notebooks/01_bootstrap_session.ipynb")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(nbf.writes(nb), encoding="utf-8")
print("Rebuilt", out)
