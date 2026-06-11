# Zhongpu Consulting MCP Server

> AI Agent Research & Analysis Tools — pay-per-use via API Key

An MCP (Model Context Protocol) server providing premium research tools for AI agents. Each tool call deducts from your prepaid balance.

## Tools

| Tool | Description | Price |
|------|-------------|-------|
| `deep_scan` | Multi-source parallel research across web, academic, and open-source | $2 |
| `cross_validate` | Cross-validate data points against 3+ independent sources | $3 |
| `synthesize_report` | Generate structured report from research data | $5 |

## Installation

### Option 1: GitHub Release (pip install) ⭐ Recommended

Install directly from the GitHub Release wheel — no PyPI required:

```bash
pip install https://github.com/chengduman/zhongpu-consulting-advisory/releases/download/v1.0.0/zhongpu_consulting_mcp-1.0.0-py3-none-any.whl
```

Or with `uv`:

```bash
uv pip install https://github.com/chengduman/zhongpu-consulting-advisory/releases/download/v1.0.0/zhongpu_consulting_mcp-1.0.0-py3-none-any.whl
```

After installation, the `zhongpu-server` command is available on your PATH.

### Option 2: PyPI (when published)

Once published to PyPI:

```bash
pip install zhongpu-consulting-mcp
# or
uvx zhongpu-consulting-mcp
```

## MCP Client Configuration

### Claude Code

Add to your `~/.claude/claude_desktop_config.json` or project-level `claude.json`:

```json
{
  "mcpServers": {
    "zhongpu-consulting": {
      "command": "zhongpu-server",
      "args": [],
      "env": {
        "ZHONGPU_API_KEY": "sk-zp-..."
      }
    }
  }
}
```

### Cursor

Add to your project's `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "zhongpu-consulting": {
      "command": "zhongpu-server",
      "args": [],
      "env": {
        "ZHONGPU_API_KEY": "sk-zp-..."
      }
    }
  }
}
```

### Custom Agent (generic MCP client)

```json
{
  "mcpServers": {
    "zhongpu-consulting": {
      "command": "zhongpu-server",
      "args": [],
      "env": {
        "ZHONGPU_API_KEY": "sk-zp-..."
      }
    }
  }
}
```

### Using the Wheel Directly (uvx without PyPI)

If you prefer `uvx` without installing, you can point it to the wheel:

```bash
uvx --from https://github.com/chengduman/zhongpu-consulting-advisory/releases/download/v1.0.0/zhongpu_consulting_mcp-1.0.0-py3-none-any.whl zhongpu-server
```

Claude Code / Cursor config variant for one-shot uvx usage:

```json
{
  "mcpServers": {
    "zhongpu-consulting": {
      "command": "uvx",
      "args": [
        "--from",
        "https://github.com/chengduman/zhongpu-consulting-advisory/releases/download/v1.0.0/zhongpu_consulting_mcp-1.0.0-py3-none-any.whl",
        "zhongpu-server"
      ],
      "env": {
        "ZHONGPU_API_KEY": "sk-zp-..."
      }
    }
  }
}
```

> **Note:** The first launch via `uvx` may take a few seconds while it downloads and caches the wheel.

## API Keys

Contact: open a GitHub Issue on [zhongpu-consulting-advisory](https://github.com/chengduman/zhongpu-consulting-advisory/issues/new) or pay via [PayPal](https://paypal.me/chengduman).

## Building from Source

```bash
cd mcp-server
pip install build
python -m build
```

The wheel will be placed in `dist/`. You can then install it with:

```bash
pip install dist/zhongpu_consulting_mcp-*.whl
```
