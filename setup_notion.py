"""
Notion Setup Script for Life Doc AI
------------------------------------
Uses direct Notion REST API calls for reliability.
This script will:
1. Create a "Life Events" database with Event, Date, Impact properties
2. Create a "Journal Entries" database with Entry, Date properties
3. Populate both with sample data
4. Update .env automatically
"""

import os
import sys
import requests
import json

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# ── Sample Life Events ──────────────────────────────────────
SAMPLE_EVENTS = [
    {"event": "Started learning programming",    "date": "2021-03-10", "impact": "High"},
    {"event": "Built first website",             "date": "2021-08-15", "impact": "Medium"},
    {"event": "Learned Python & Data Science",   "date": "2022-01-20", "impact": "High"},
    {"event": "First freelance project",         "date": "2022-06-05", "impact": "Medium"},
    {"event": "Started learning AI/ML",          "date": "2023-01-15", "impact": "High"},
    {"event": "Built first AI project",          "date": "2023-07-10", "impact": "High"},
    {"event": "Won a hackathon",                 "date": "2024-02-28", "impact": "High"},
    {"event": "Started university research",     "date": "2024-05-01", "impact": "High"},
    {"event": "Published first tech article",    "date": "2024-09-12", "impact": "Medium"},
    {"event": "Explored metagenomics & biotech", "date": "2025-02-20", "impact": "Medium"},
]

SAMPLE_JOURNALS = [
    {"content": "Today I decided to learn programming. I feel excited and a bit nervous, but I know this is the right path for me.", "date": "2021-03-10"},
    {"content": "Just finished my first website! It's simple, but I'm proud of it. The feeling of creating something from nothing is amazing.", "date": "2021-08-15"},
    {"content": "Python is incredible. Data science opens up so many possibilities. I spent the whole weekend exploring pandas and matplotlib.", "date": "2022-01-20"},
    {"content": "Got my first client! The project is challenging but I'm learning so much. Real-world problems are different from tutorials.", "date": "2022-06-05"},
    {"content": "AI is the future. I've been diving deep into machine learning and neural networks. The math is hard but fascinating.", "date": "2023-01-15"},
    {"content": "My AI project actually works! It can classify images with 95% accuracy. This is the most rewarding thing I've ever built.", "date": "2023-07-10"},
    {"content": "We won the hackathon! 48 hours of intense coding, but our AI-powered solution impressed the judges.", "date": "2024-02-28"},
    {"content": "Starting research at the university. The academic world is different from self-learning but equally exciting.", "date": "2024-05-01"},
    {"content": "Published my first article about AI applications. Getting positive feedback from the community feels great.", "date": "2024-09-12"},
    {"content": "Metagenomics is fascinating — combining biology with computational analysis could change the world.", "date": "2025-02-20"},
    {"content": "Looking back at my journey, I've come so far. From a total beginner to building AI systems. Grateful for every struggle.", "date": "2025-03-15"},
]


def api_call(method, endpoint, token, data=None):
    """Make a Notion API call."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    url = f"{NOTION_API}{endpoint}"
    if method == "GET":
        resp = requests.get(url, headers=headers)
    elif method == "POST":
        resp = requests.post(url, headers=headers, json=data)
    elif method == "PATCH":
        resp = requests.patch(url, headers=headers, json=data)

    if resp.status_code >= 400:
        raise Exception(f"API Error {resp.status_code}: {resp.json().get('message', resp.text[:300])}")
    return resp.json()


def main():
    print("=" * 55)
    print("  🎬  Life Doc AI — Notion Setup Script")
    print("=" * 55)
    print()

    # ── Get token ───────────────────────────────────────────
    token = input("Paste your Notion Integration Token: ").strip()
    if not token:
        print("❌ Token is required. Exiting.")
        sys.exit(1)

    # ── Find pages ──────────────────────────────────────────
    print("\n🔍 Searching for available pages...")
    try:
        search_result = api_call("POST", "/search", token, {
            "filter": {"property": "object", "value": "page"}
        })
        results = search_result.get("results", [])
    except Exception as e:
        print(f"❌ Error connecting to Notion: {e}")
        sys.exit(1)

    if not results:
        print("❌ No pages found. Please:")
        print("   1. Open Notion → Create a new page")
        print("   2. Click ⋯ → Connections → Add your integration")
        print("   3. Re-run this script")
        sys.exit(1)

    # Show available pages
    print(f"\n📄 Found {len(results)} page(s) with access:\n")
    pages = []
    for i, page in enumerate(results[:10]):
        title = "Untitled"
        props = page.get("properties", {})
        for key, val in props.items():
            if val.get("type") == "title":
                title_arr = val.get("title", [])
                if title_arr:
                    title = title_arr[0].get("plain_text", "Untitled")
                    break
        pages.append((page["id"], title))
        print(f"   [{i+1}] {title}")

    print()
    choice = input(f"Select a parent page (1-{len(pages)}) or press Enter for [{pages[0][1]}]: ").strip()
    if choice and choice.isdigit() and 1 <= int(choice) <= len(pages):
        parent_id = pages[int(choice)-1][0]
        parent_title = pages[int(choice)-1][1]
    else:
        parent_id = pages[0][0]
        parent_title = pages[0][1]

    print(f"\n✅ Using parent page: {parent_title}")

    # ── Create Life Events Database ─────────────────────────
    print("\n📋 Creating 'Life Events' database...")
    events_db = api_call("POST", "/databases", token, {
        "parent": {"type": "page_id", "page_id": parent_id},
        "title": [{"type": "text", "text": {"content": "Life Events"}}],
        "properties": {
            "Event": {"title": {}},
            "Date": {"date": {}},
            "Impact": {
                "select": {
                    "options": [
                        {"name": "High", "color": "red"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "green"},
                    ]
                }
            },
        },
    })
    events_db_id = events_db["id"]

    # Verify actual property names
    actual_props = events_db.get("properties", {})
    prop_names = {v.get("type"): k for k, v in actual_props.items()}
    ev_title = prop_names.get("title", "Event")
    ev_date = prop_names.get("date", "Date")
    ev_select = prop_names.get("select", "Impact")

    print(f"   ✅ Created! ID: {events_db_id}")
    print(f"   📌 Properties: title='{ev_title}', date='{ev_date}', select='{ev_select}'")

    # ── Populate Events ─────────────────────────────────────
    print("   📝 Adding sample events...")
    success = 0
    for ev in SAMPLE_EVENTS:
        try:
            api_call("POST", "/pages", token, {
                "parent": {"database_id": events_db_id},
                "properties": {
                    ev_title: {"title": [{"text": {"content": ev["event"]}}]},
                    ev_date: {"date": {"start": ev["date"]}},
                    ev_select: {"select": {"name": ev["impact"]}},
                },
            })
            success += 1
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    print(f"   ✅ Added {success}/{len(SAMPLE_EVENTS)} events")

    # ── Create Journal Database ─────────────────────────────
    print("\n📓 Creating 'Journal Entries' database...")
    journal_db = api_call("POST", "/databases", token, {
        "parent": {"type": "page_id", "page_id": parent_id},
        "title": [{"type": "text", "text": {"content": "Journal Entries"}}],
        "properties": {
            "Entry": {"title": {}},
            "Date": {"date": {}},
        },
    })
    journal_db_id = journal_db["id"]

    actual_props_j = journal_db.get("properties", {})
    prop_names_j = {v.get("type"): k for k, v in actual_props_j.items()}
    j_title = prop_names_j.get("title", "Entry")
    j_date = prop_names_j.get("date", "Date")

    print(f"   ✅ Created! ID: {journal_db_id}")
    print(f"   📌 Properties: title='{j_title}', date='{j_date}'")

    # ── Populate Journal ────────────────────────────────────
    print("   📝 Adding sample journal entries...")
    success = 0
    for entry in SAMPLE_JOURNALS:
        try:
            api_call("POST", "/pages", token, {
                "parent": {"database_id": journal_db_id},
                "properties": {
                    j_title: {"title": [{"text": {"content": entry["content"]}}]},
                    j_date: {"date": {"start": entry["date"]}},
                },
            })
            success += 1
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    print(f"   ✅ Added {success}/{len(SAMPLE_JOURNALS)} entries")

    # ── Write .env ──────────────────────────────────────────
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    openai_key = ""
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    openai_key = line.strip().split("=", 1)[1]

    with open(env_path, "w") as f:
        f.write(f"NOTION_TOKEN={token}\n")
        f.write(f"NOTION_DATABASE_EVENTS={events_db_id}\n")
        f.write(f"NOTION_DATABASE_JOURNAL={journal_db_id}\n")
        f.write(f"OPENAI_API_KEY={openai_key or 'your_openai_api_key_here'}\n")

    print("\n" + "=" * 55)
    print("  🎉  SETUP COMPLETE!")
    print("=" * 55)
    print()
    print(f"✅ .env updated: {env_path}")
    print()
    print("Next steps:")
    print("   1. (Optional) Add OpenAI API key in .env")
    print("   2. Restart Streamlit: streamlit run app.py")
    print("   3. Click 'Generate My Life Documentary'! 🎬")
    print()


if __name__ == "__main__":
    main()
