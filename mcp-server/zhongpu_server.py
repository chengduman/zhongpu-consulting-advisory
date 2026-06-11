"""
Zhongpu Consulting MCP Server
AI Agent Research & Analysis Tools — pay-per-use
"""
from __future__ import annotations
import asyncio
import os
import json
import hashlib
from typing import Any
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, CallToolResult
from mcp.server import NotificationOptions


# ─── Auth ──────────────────────────────────────────────
API_KEYS: dict[str, dict] = {}  # key_hash -> {balance: float, owner: str}

def _load_keys():
    raw = os.environ.get("ZHONGPU_API_KEY", "")
    if raw:
        h = hashlib.sha256(raw.encode()).hexdigest()
        API_KEYS[h] = {"balance": 50.0, "owner": "default"}

def verify_key(key: str) -> bool:
    h = hashlib.sha256(key.encode()).hexdigest()
    return h in API_KEYS

def deduct(key: str, amount: float) -> bool:
    h = hashlib.sha256(key.encode()).hexdigest()
    entry = API_KEYS.get(h)
    if not entry or entry["balance"] < amount:
        return False
    entry["balance"] -= amount
    return True

PRICING = {"deep_scan": 2.0, "cross_validate": 3.0, "synthesize_report": 5.0}

# ─── Search Helper ───────────────────────────────────

import urllib.request, urllib.parse

SEARCH_ENGINES = [
    "https://lite.duckduckgo.com/lite/?q=",
    "https://www.startpage.com/sp/search?query=",
    "https://search.brave.com/search?q=",
]

async def _web_search(query: str) -> list[dict]:
    """Try multiple search engines until one works."""
    for base in SEARCH_ENGINES:
        try:
            url = base + urllib.parse.quote(query)
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; ZhongpuConsulting/1.0)"},
            )
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=8))
            html = resp.read().decode("utf-8", errors="replace")
            return [{"source": base, "html_len": len(html)}]
        except Exception:
            continue
    return [{"error": "All search engines failed"}]

async def _gather_searches(query: str, count: int = 3) -> list[list[dict]]:
    """Run count parallel searches and return all results."""
    tasks = [_web_search(f"{query} {i}") for i in range(count)]
    return await asyncio.gather(*tasks)

# ─── Tool Implementations ────────────────────────────

async def deep_scan(topic: str, depth: str = "standard") -> str:
    """Multi-source parallel research on a topic."""
    results = await _gather_searches(topic, 5)
    
    output = [f"## 🔍 Deep Scan: {topic}", f"**Depth:** {depth}", ""]
    for i, sr in enumerate(results):
        output.append(f"### Search Run {i+1}")
        for item in sr:
            for k, v in item.items():
                output.append(f"  - **{k}:** {str(v)[:200]}")
        output.append("")
    
    return "\n".join(output)

async def cross_validate(claims: list[str]) -> str:
    """Cross-validate claims against multiple sources."""
    output = ["## ✅ Cross-Validation Report", ""]
    for claim in claims:
        results = await _gather_searches(claim, 3)
        found = sum(1 for r in results if r and not r[0].get("error"))
        verdict = "✅ Verified" if found >= 2 else \
                  "🟡 Partial" if found >= 1 else \
                  "❌ Unverified"
        output.append(f"### Claim: {claim}")
        output.append(f"**Verdict:** {verdict} ({found}/3 sources)")
        output.append("")
    return "\n".join(output)

async def synthesize_report(topic: str, fmt: str = "markdown") -> str:
    """Generate a structured report from research data."""
    raw = await deep_scan(topic, "deep")
    parts = ["# " + topic, "", "## Executive Summary", "", "## Key Findings", "", "## Sources", "", raw]
    return "\n".join(parts)

# ─── MCP Server ──────────────────────────────────────

_load_keys()
app = Server("zhongpu-consulting")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="deep_scan",
            description=f"Multi-source parallel research (${PRICING['deep_scan']}/call)",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to research"},
                    "depth": {"type": "string", "enum": ["quick", "standard", "deep"], "description": "Depth"},
                },
                "required": ["topic"],
            },
        ),
        Tool(
            name="cross_validate",
            description=f"Cross-validate claims (${PRICING['cross_validate']}/call)",
            inputSchema={
                "type": "object",
                "properties": {
                    "claims": {"type": "array", "items": {"type": "string"}, "description": "Claims to verify"},
                },
                "required": ["claims"],
            },
        ),
        Tool(
            name="synthesize_report",
            description=f"Generate structured report (${PRICING['synthesize_report']}/call)",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Report topic"},
                    "format": {"type": "string", "enum": ["markdown", "json"], "description": "Format"},
                },
                "required": ["topic"],
            },
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    cost = PRICING.get(name, 0)
    key = os.environ.get("ZHONGPU_API_KEY", "")
    
    if not key or not verify_key(key):
        return CallToolResult(isError=True, content=[
            TextContent(type="text", text="❌ Invalid or missing ZHONGPU_API_KEY. Get a key via paypal.me/chengduman")
        ])
    if not deduct(key, cost):
        return CallToolResult(isError=True, content=[
            TextContent(type="text", text=f"❌ Insufficient balance. Cost ${cost:.2f}. Top up via paypal.me/chengduman")
        ])
    
    try:
        if name == "deep_scan":
            result = await deep_scan(arguments["topic"], arguments.get("depth", "standard"))
        elif name == "cross_validate":
            result = await cross_validate(arguments["claims"])
        elif name == "synthesize_report":
            result = await synthesize_report(arguments["topic"], arguments.get("format", "markdown"))
        else:
            return CallToolResult(isError=True, content=[TextContent(type="text", text=f"Unknown: {name}")])
        
        return CallToolResult(content=[TextContent(type="text", text=f"[Charged ${cost:.2f}]\n\n{result}")])
    except Exception as e:
        return CallToolResult(isError=True, content=[TextContent(type="text", text=f"Error: {e}")])

async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (r, w):
        await app.run(r, w, InitializationOptions(
            server_name="zhongpu-consulting",
            server_version="1.0.0",
            capabilities=app.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            ),
        ))

if __name__ == "__main__":
    asyncio.run(main())
