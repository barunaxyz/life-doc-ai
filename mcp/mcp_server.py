"""
Notion MCP Server — Exposes Notion API as MCP tools.

This is a lightweight MCP server that wraps the Notion REST API into
MCP-compatible tools. It runs on Streamable HTTP transport so the
Streamlit app (MCP Client) can call tools over HTTP.

Tools exposed:
  - notion_search: Search across workspace
  - notion_query_database: Query a database with optional filters
  - notion_retrieve_page: Get page content
  - notion_retrieve_database: Get database schema
"""

import json
import uuid
import threading
import requests as req
from http.server import HTTPServer, BaseHTTPRequestHandler

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# ── MCP Tool Definitions ────────────────────────────────────
TOOLS = [
    {
        "name": "notion_search",
        "description": "Search across pages and databases in the Notion workspace.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query text"},
                "filter_object": {
                    "type": "string",
                    "enum": ["page", "database"],
                    "description": "Filter by object type",
                },
            },
        },
    },
    {
        "name": "notion_query_database",
        "description": "Query a Notion database and return its entries.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "database_id": {"type": "string", "description": "The database ID to query"},
            },
            "required": ["database_id"],
        },
    },
    {
        "name": "notion_retrieve_page",
        "description": "Retrieve a Notion page by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "The page ID to retrieve"},
            },
            "required": ["page_id"],
        },
    },
    {
        "name": "notion_retrieve_database",
        "description": "Retrieve a Notion database schema by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "database_id": {"type": "string", "description": "The database ID to retrieve"},
            },
            "required": ["database_id"],
        },
    },
]

# ── Tool Execution ──────────────────────────────────────────

def _notion_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def execute_tool(tool_name, arguments, notion_token):
    """Execute a Notion MCP tool and return the result."""
    headers = _notion_headers(notion_token)

    try:
        if tool_name == "notion_search":
            body = {}
            if arguments.get("query"):
                body["query"] = arguments["query"]
            if arguments.get("filter_object"):
                body["filter"] = {"property": "object", "value": arguments["filter_object"]}
            resp = req.post(f"{NOTION_API}/search", headers=headers, json=body)

        elif tool_name == "notion_query_database":
            db_id = arguments["database_id"]
            resp = req.post(f"{NOTION_API}/databases/{db_id}/query", headers=headers, json={})

        elif tool_name == "notion_retrieve_page":
            page_id = arguments["page_id"]
            resp = req.get(f"{NOTION_API}/pages/{page_id}", headers=headers)

        elif tool_name == "notion_retrieve_database":
            db_id = arguments["database_id"]
            resp = req.get(f"{NOTION_API}/databases/{db_id}", headers=headers)

        else:
            return {"error": f"Unknown tool: {tool_name}"}

        if resp.status_code >= 400:
            return {"error": f"Notion API error {resp.status_code}: {resp.json().get('message', '')}"}

        return resp.json()

    except Exception as e:
        return {"error": str(e)}


# ── JSON-RPC MCP Handler ────────────────────────────────────

class MCPHandler(BaseHTTPRequestHandler):
    """HTTP handler implementing MCP Streamable HTTP transport (JSON-RPC)."""

    notion_token = None

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_POST(self):
        if self.path != "/mcp":
            self.send_error(404)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        method = request.get("method", "")
        req_id = request.get("id")
        params = request.get("params", {})

        # Handle MCP methods
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "notion-mcp-server-py", "version": "1.0.0"},
            }
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            tool_result = execute_tool(tool_name, arguments, self.notion_token)
            result = {
                "content": [{"type": "text", "text": json.dumps(tool_result, default=str)}],
                "isError": "error" in tool_result,
            }
        elif method == "notifications/initialized":
            # Notification, no response needed
            self.send_response(204)
            self.end_headers()
            return
        else:
            result = None
            error = {"code": -32601, "message": f"Method not found: {method}"}

        # Send JSON-RPC response
        response = {"jsonrpc": "2.0", "id": req_id}
        if method not in ("notifications/initialized",):
            if "error" in dir() and error:
                response["error"] = error
            else:
                response["result"] = result

        response_body = json.dumps(response).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response_body))
        self.end_headers()
        self.wfile.write(response_body)


# ── Server Management ───────────────────────────────────────

_server = None
_thread = None


def start_mcp_server(notion_token, port=3100):
    """Start the MCP server in a background thread."""
    global _server, _thread

    if _server is not None:
        return port  # Already running

    MCPHandler.notion_token = notion_token

    _server = HTTPServer(("127.0.0.1", port), MCPHandler)
    _thread = threading.Thread(target=_server.serve_forever, daemon=True)
    _thread.start()
    print(f"🟢 Notion MCP Server running at http://127.0.0.1:{port}/mcp")
    return port


def stop_mcp_server():
    """Stop the MCP server."""
    global _server, _thread
    if _server:
        _server.shutdown()
        _server = None
        _thread = None
        print("🔴 Notion MCP Server stopped")


def is_server_running():
    """Check if the MCP server is running."""
    return _server is not None
