# Zhongpu Consulting MCP Server

> AI Agent Research & Analysis Tools — pay-per-use via API Key

## Tools

| Tool | Description | Price |
|------|-------------|-------|
| `deep_scan` | Multi-source parallel research across web, academic, and open-source | $2 |
| `cross_validate` | Cross-validate data points against 3+ independent sources | $3 |
| `synthesize_report` | Generate structured report from research data | $5 |

## Quick Start

```json
// MCP client config (Claude Code / Cursor / etc.)
{
  "mcpServers": {
    "zhongpu-consulting": {
      "command": "uvx",
      "args": ["zhongpu-consulting-mcp"],
      "env": {
        "ZHONGPU_API_KEY": "sk-zp-..."
      }
    }
  }
}
```

## API Keys

Contact: open a GitHub Issue on [zhongpu-consulting-advisory](https://github.com/chengduman/zhongpu-consulting-advisory/issues/new) or pay via [PayPal](https://paypal.me/chengduman).
