# HedgeDoc MCP Server

MCP server for [HedgeDoc](https://hedgedoc.org/) — create collaborative markdown notes with Mermaid diagrams from OpenCode and other MCP-compatible AI agents.

## Tools

| Tool | Description |
|---|---|
| `hedgedoc_create` | Create a new note with markdown content |
| `hedgedoc_read` | Read the raw markdown content of a note |
| `hedgedoc_info` | Get note metadata (title, description, timestamps) |
| `hedgedoc_create_diagram` | Create a note with a Mermaid diagram |

## Usage

```bash
export HEDGEDOC_URL="https://hedgedoc.your-instance.com"
# Optional: export HEDGEDOC_TOKEN="your-api-token"

uvx hedgedoc-mcp-server stdio
```

### OpenCode config

```jsonc
{
  "mcp": {
    "hedgedoc": {
      "type": "local",
      "enabled": true,
      "command": ["uvx", "hedgedoc-mcp-server", "stdio"],
      "environment": {
        "HEDGEDOC_URL": "https://hedgedoc.your-instance.com"
      }
    }
  }
}
```

## Requirements

- HedgeDoc 1.x instance
- Python 3.11+
- `uv` (recommended) or pip
