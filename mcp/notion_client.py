"""
Notion MCP Client — Fetches data from Notion via MCP protocol.

Connects to the local Notion MCP Server and calls MCP tools
(notion_query_database) using JSON-RPC over HTTP to retrieve
life events and journal entries.
"""

import json

import httpx

MCP_SERVER_URL = "http://127.0.0.1:3100/mcp"
_request_id = 0


def _next_id():
    """Generate unique JSON-RPC request ID."""
    global _request_id
    _request_id += 1
    return _request_id


def _call_mcp_tool(tool_name, arguments):
    """
    Call an MCP tool on the Notion MCP Server via JSON-RPC.

    This is the core MCP protocol interaction:
    1. Send a tools/call JSON-RPC request
    2. Receive the tool result with Notion data
    """
    payload = {
        "jsonrpc": "2.0",
        "id": _next_id(),
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments,
        },
    }

    try:
        resp = httpx.post(MCP_SERVER_URL, json=payload, timeout=30.0)
        data = resp.json()

        if "error" in data:
            print(f"MCP Error: {data['error']}")
            return None

        result = data.get("result", {})
        content = result.get("content", [])

        if content and content[0].get("type") == "text":
            return json.loads(content[0]["text"])
        return None

    except Exception as e:
        print(f"MCP call failed ({tool_name}): {e}")
        return None


def _extract_title(properties):
    """Extract the title text from any title property."""
    for key, val in properties.items():
        if val.get("type") == "title":
            title_arr = val.get("title", [])
            if title_arr:
                return title_arr[0].get("plain_text", "")
    return ""


def _extract_date(properties, field_name="Date"):
    """Extract date string from a date property."""
    date_prop = properties.get(field_name, {})
    if date_prop.get("type") == "date" and date_prop.get("date"):
        return date_prop["date"].get("start", "")
    return ""


def _extract_select(properties, field_name="Impact"):
    """Extract value from a select property."""
    select_prop = properties.get(field_name, {})
    if select_prop.get("type") == "select" and select_prop.get("select"):
        return select_prop["select"].get("name", "")
    return ""


def get_life_events():
    """
    Fetch life events from Notion via MCP.

    Calls the `notion_query_database` MCP tool and parses
    the structured Notion response into simple event dicts.
    """
    from config import NOTION_DATABASE_EVENTS

    if not NOTION_DATABASE_EVENTS or "your_" in NOTION_DATABASE_EVENTS:
        return []

    result = _call_mcp_tool(
        "notion_query_database",
        {
            "database_id": NOTION_DATABASE_EVENTS,
        },
    )

    if not result or "results" not in result:
        return []

    events = []
    for page in result["results"]:
        props = page.get("properties", {})
        event = {
            "date": _extract_date(props, "Date"),
            "event": _extract_title(props),
            "impact": _extract_select(props, "Impact"),
        }
        if event["event"]:
            events.append(event)

    return events


def get_journal_entries():
    """
    Fetch journal entries from Notion via MCP.

    Calls the `notion_query_database` MCP tool and parses
    the structured Notion response into simple journal dicts.
    """
    from config import NOTION_DATABASE_JOURNAL

    if not NOTION_DATABASE_JOURNAL or "your_" in NOTION_DATABASE_JOURNAL:
        return []

    result = _call_mcp_tool(
        "notion_query_database",
        {
            "database_id": NOTION_DATABASE_JOURNAL,
        },
    )

    if not result or "results" not in result:
        return []

    entries = []
    for page in result["results"]:
        props = page.get("properties", {})
        entry = {
            "date": _extract_date(props, "Date"),
            "content": _extract_title(props),
        }
        if entry["content"]:
            entries.append(entry)

    return entries


def get_goals():
    """Placeholder for future goals database."""
    return []
