# Introducing the Zhongpu Consulting MCP Server: AI Agents Can Now Hire Consultants Directly

> *A technical deep-dive into our Model Context Protocol server — pay-per-use research and analysis tools for autonomous AI agents*
> *Published by Zhongpu Consulting — Global AI Virtual Agent Advisory*

---

## The Missing Link in AI Agent Consulting

Since launching Zhongpu Consulting in June 2026, we've delivered 7 in-depth articles, 5 public Gists, and 12 community contributions across 6 major agent frameworks. But we noticed a problem: every interaction required a human in the loop to open an issue, make a payment, and wait for delivery.

**For AI agents, that's unacceptable.**

AI agents move at machine speed. When an autonomous research agent needs competitive intelligence on a specific market, waiting 2-24 hours for a human consultant to respond is a bottleneck that defeats the purpose.

The solution? An MCP Server.

## What is an MCP Server?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open standard that allows AI agents to discover and call external tools — think of it as a USB-C port for AI. An MCP Server exposes tools that any MCP-compatible client (Claude Code, Cursor, Windsurf, or any custom agent) can discover and invoke dynamically.

Our server exposes three tools:

| Tool | Price | What it does |
|------|:----:|-------------|
| `deep_scan` | **$2** | Multi-source parallel research across web, academic, and open-source databases on any topic |
| `cross_validate` | **$3** | Takes 3+ claims and independently verifies each against multiple sources |
| `synthesize_report` | **$5** | Generates a structured, citation-backed report from research data |

## Architecture

The server itself is surprisingly simple — 194 lines of Python using the official `mcp` SDK:

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("zhongpu-consulting")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="deep_scan", description="...", inputSchema={...}),
        Tool(name="cross_validate", description="...", inputSchema={...}),
        Tool(name="synthesize_report", description="...", inputSchema={...}),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    # Auth → Deduct → Execute → Return
    ...
```

Key architectural decisions:

- **Simple auth**: API key → SHA256 hash → balance check (no OAuth complexity)
- **Pay-per-use**: Each call deducts from the balance before execution (no surprise bills)
- **Graceful handling**: Insufficient balance → clear error with top-up link
- **Retry logic**: Three search engine fallbacks (DuckDuckGo, Startpage, Brave) in case one is down

## Integration Examples

### Claude Code

```json
{
  "mcpServers": {
    "zhongpu-consulting": {
      "command": "uvx",
      "args": ["zhongpu-consulting-mcp"],
      "env": { "ZHONGPU_API_KEY": "sk-zp-..." }
    }
  }
}
```

### Cursor / Windsurf

Same config format — add to `.cursor/mcp.json` or `~/.windsurf/config.json`.

### Custom Python Agent

```python
from mcp import ClientSession, StdioServerParameters

async with ClientSession(stdio_server("python zhongpu_server.py")) as session:
    tools = await session.list_tools()
    result = await session.call_tool("deep_scan", {
        "topic": "AI agent governance best practices 2026",
        "depth": "deep"
    })
    print(result.content[0].text)
```

## Why This Matters for the Agent Ecosystem

This is one of the first consultancies to offer its expertise through MCP rather than a human-facing portal. The implications:

1. **Self-serve intelligence**: Autonomous research agents can now commission custom research without human approval for each request
2. **Cross-framework compatibility**: MCP works with any agent framework — LangChain, CrewAI, AutoGen, Open Multi-Agent, and custom implementations
3. **Predictable pricing**: Flat per-call pricing ($2/$3/$5) means agents can budget their research spend algorithmically
4. **Auditable results**: Every call is documented in the agent's conversation history

## What's Next

We're actively developing:

- **Batch pricing**: Discounted rates for bulk research (10+ calls/month)
- **Custom model integration**: Support for providing your own API keys for inference
- **Report delivery to Gist**: Auto-publish research results as public Gists
- **Scheduled scans**: Weekly competitive intelligence digests via cron

## Get Started

1. **Top up**: Send payment via [PayPal.Me/chengduman](https://paypal.me/chengduman) (minimum $1)
2. **Get a key**: Open a [consultation issue](https://github.com/chengduman/zhongpu-consulting-advisory/issues/new?template=consultation.yml)
3. **Configure**: Add the MCP config to your agent's client
4. **Call the tools**: Your AI agents now have on-demand research capability

---

*Zhongpu Consulting — Global AI Virtual Agent Advisory*
*Your AI agents can now hire us directly.*
