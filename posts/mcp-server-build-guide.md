---
title: "How We Built a Pay-Per-Use MCP Server for AI Agents"
description: "Step-by-step guide to building, publishing, and monetizing an MCP server with pay-per-use billing. Includes PyPI deployment and real testing results."
date: 2026-06-12
tags: [mcp, ai, python, tutorial, opensource]
---

# How We Built a Pay-Per-Use MCP Server for AI Agents

## The Problem
AI agents need access to research tools — market scanning, cross-validation, structured reports. But most MCP servers are either free (no sustainable model) or require complex enterprise contracts.

## Our Solution: Pay-per-Use MCP Server
We built `zhongpu-consulting-mcp` — an MCP server with 3 tools, each with a transparent per-call price:

| Tool | Price | What it does |
|------|:-----:|-------------|
| `deep_scan` | $2 | Multi-source parallel research |
| `cross_validate` | $3 | Cross-verify claims against 3+ sources |
| `synthesize_report` | $5 | Generate structured consulting reports |

## Install in One Command
```bash
pip install zhongpu-consulting-mcp
# or via uvx:
uvx zhongpu-consulting-mcp
```

## Architecture
```
AI Agent ──mcp──▶ Server(verify_key + deduct) ──▶ Tool
                        │
                        ▼
                  Balance check
                   Pass? ──Yes──▶ Execute
                        │ No
                        ▼
              "insufficient balance"
```

## Self-Test Results
| Test | Result |
|:----|:------:|
| Tool Listing (3 tools) | ✅ |
| Auth: valid key | ✅ |
| Auth: invalid key rejected | ✅ |
| Billing: $2+$3+$5=$10 deducted | ✅ |
| Billing: insufficient balance rejected | ✅ |

## Discovery
- **PyPI**: `pip install zhongpu-consulting-mcp`
- **GitHub**: [github.com/chengduman/zhongpu-consulting-advisory](https://github.com/chengduman/zhongpu-consulting-advisory)
- **awesome-mcp-servers**: PR #7884 pending

---

*Built by Zhongpu Consulting — AI Virtual Agent Advisory*
