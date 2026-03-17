import os
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_EVENTS = os.getenv("NOTION_DATABASE_EVENTS")
NOTION_DATABASE_JOURNAL = os.getenv("NOTION_DATABASE_JOURNAL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable not set.")
if not NOTION_TOKEN:
    print("Warning: NOTION_TOKEN environment variable not set.")
