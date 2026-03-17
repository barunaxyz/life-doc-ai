# 🎬 Life Doc AI

> Transform your Notion journals and life events into an AI-crafted cinematic documentary of your personal journey.

**Life Doc AI** connects to your Notion workspace via the **Model Context Protocol (MCP)**, reads your life events and journal entries, and generates a beautiful documentary narrative — complete with timeline, chapters, and psychological insights.

## ✨ Features

- 🔌 **Notion MCP Integration** — Communicates with Notion through MCP protocol (JSON-RPC over HTTP)
- 📖 **Life Events Timeline** — Chronological visualization of your milestones
- 📚 **Auto-Generated Chapters** — Groups your life into meaningful eras
- 💡 **Psychological Insights** — Analyzes patterns, most active years, and impact metrics
- 📜 **AI Narrative** — Crafts a cinematic story from your data (via OpenAI GPT-4 or built-in generator)
- 🎨 **Premium UI** — Dark theme with glassmorphism, gradient accents, and smooth animations

## 🏗️ Architecture

```
┌───────────────────┐     MCP Protocol     ┌──────────────────────┐     Notion API    ┌─────────┐
│  Streamlit App    │ ◄──────────────────► │  Python MCP Server   │ ◄──────────────► │  Notion │
│  (MCP Client)     │    JSON-RPC / HTTP   │  (mcp_server.py)     │                  │  Cloud  │
└───────────────────┘                      └──────────────────────┘                  └─────────┘
```

### How MCP Works in This Project

1. **MCP Server** (`mcp/mcp_server.py`) starts as a background HTTP server on port 3100
2. It exposes 4 MCP tools: `notion_search`, `notion_query_database`, `notion_retrieve_page`, `notion_retrieve_database`
3. **MCP Client** (`mcp/notion_client.py`) sends JSON-RPC `tools/call` requests to the server
4. The server executes the tool against the Notion API and returns results via MCP protocol
5. The **Documentary Agent** processes the data and generates the narrative

## 📁 Project Structure

```
life-doc-ai/
├── app.py                          # Streamlit UI (auto-starts MCP server)
├── config.py                       # Environment variable loader
├── requirements.txt
│
├── mcp/
│   ├── mcp_server.py              # 🔌 Notion MCP Server (JSON-RPC / HTTP)
│   ├── notion_client.py           # 📡 MCP Client (calls tools via JSON-RPC)
│   └── mcp_tools.py               # Tool wrappers for the agent
│
├── agent/
│   ├── documentary_agent.py       # 🧠 Main AI agent (LLM + fallback generators)
│   └── prompts.py                 # System prompts for GPT-4
│
├── services/
│   ├── timeline_service.py        # Timeline data processing
│   ├── chapter_service.py         # Chapter grouping logic
│   └── insight_service.py         # Insight extraction
│
├── utils/
│   └── formatter.py               # HTML formatters for UI cards
│
├── setup_notion.py                # 🛠️ Script to auto-create Notion databases + sample data
└── data/
    └── sample_output.json         # Example output structure
```

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/life-doc-ai.git
cd life-doc-ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up Notion

**Option A: Automatic setup (recommended)**
1. Create a Notion Integration at https://www.notion.so/my-integrations
2. Create a page in Notion and connect your integration to it
3. Run the setup script:
```bash
python setup_notion.py
```
This will automatically create databases, add sample data, and update your `.env` file.

**Option B: Manual setup**
1. Create two databases in Notion: "Life Events" and "Journal Entries"
2. Copy your integration token and database IDs
3. Create a `.env` file:
```env
NOTION_TOKEN=ntn_your_token
NOTION_DATABASE_EVENTS=your_events_db_id
NOTION_DATABASE_JOURNAL=your_journal_db_id
OPENAI_API_KEY=your_openai_key  # Optional
```

### 4. Run the app
```bash
streamlit run app.py
```

## 🔧 How It Uses Notion MCP

This project implements the **Model Context Protocol (MCP)** with:

- **Custom Python MCP Server** that wraps the Notion REST API as MCP tools
- **MCP Client** that communicates via JSON-RPC 2.0 over HTTP transport
- **MCP tool calls**: `notion_query_database` for fetching events & journals

The MCP server automatically starts when the Streamlit app loads, creating a seamless bridge between your Notion workspace and the AI documentary generator.

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.
