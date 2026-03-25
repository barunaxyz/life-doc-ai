---
title: "Life Doc AI: Transforming Notion Journals into Cinematic Documentaries"
published: false
tags: devchallenge, notionchallenge, mcp, ai
---

*This is a submission for the [Notion MCP Challenge](https://dev.to/challenges/notion-2026-03-04)*

## What I Built
**Life Doc AI** is a Python-based intelligent web application that transforms your Notion workspace—specifically your Life Events and Journal Entries—into a beautifully structured, cinematic documentary of your personal journey. 

Instead of looking at raw text or Kanban boards, Life Doc AI uses the **Notion Model Context Protocol (MCP)** to securely fetch your milestones and reflections, and relies on an AI Agent (powered by OpenAI GPT-4o with robust rule-based fallbacks) to process them. The result is a Premium Streamlit UI that presents:
- 📜 **The Story of You**: An AI-crafted, dramatic narrative of your life.
- ⏳ **Chronological Timeline**: Analyzing the dots and connecting your journey.
- 📚 **Era Chapters**: Automatically grouping your life into meaningful, thematic chapters.
- 💡 **Psychological Insights**: Extracting hidden patterns, your most active years, and measuring your resilience.

## Video Demo
<!-- INSERT YOUR YOUTUBE OR LOOM VIDEO LINK HERE -->
*(Please record a quick 1-2 minute video showing you clicking "Generate My Life Documentary" and the resulting UI!)*

## Show us the code
Here is the complete open-source repository on GitHub!
{% github barunaxyz/life-doc-ai %}

## How I Used Notion MCP
The **Notion MCP** was the absolute core of this project, bridging the gap between my private workspace and my AI generation engine securely.

I built a custom Python MCP Server (`mcp/mcp_server.py`) that wraps the Notion REST API and exposes tools like `notion_query_database` over a JSON-RPC HTTP transport layer. 
When the user clicks "Generate", the Streamlit UI (acting as the MCP Client) fires a remote procedure call to the local server. The MCP Server negotiates with Notion, retrieves the `Life Events` and `Journal Entries` databases, and returns a clean, structured JSON payload.

### The Developer Journey
This project represents the culmination of my recent developer journey. A few weeks ago, I was figuring out static web portfolios. That evolved into mastering containerized `FastAPI` backends, and eventually wrestling with complex NLP text preprocessing errors. 

When the Notion MCP Challenge was announced, I realized I could combine all those skills:
- The backend architecture knowledge helped me build a robust, thread-safe Python MCP Server.
- The NLP experience allowed me to craft intelligent prompts and structured LLM parsing.
- The web development skills helped me design a "Glassmorphism" Dark Theme Premium UI in Streamlit (`.streamlit/config.toml`).

**Life Doc AI** doesn't just read data; it understands it. The Notion MCP unlocked the ability to treat Notion not just as a note-taking app, but as the *engine of a person's life story*.

<!-- Thanks for participating! -->
