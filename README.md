# HedgeDoc MCP Server

[MCP](https://modelcontextprotocol.io/) server for **HedgeDoc 1.x** — the open-source collaborative markdown editor.
Create notes and Mermaid diagrams from OpenCode and other MCP-compatible AI agents.

> **Note:** This is built for HedgeDoc **1.x** (formerly CodiMD).
> It uses the [HedgeDoc 1.x API](https://docs.hedgedoc.org/dev/api/), which differs from HedgeDoc 2.

## Tools

| Tool | Description |
|---|---|
| `hedgedoc_create_blank` | Create a blank note with the instance's default template |
| `hedgedoc_create` | Create a new note with a random ID |
| `hedgedoc_create_with_alias` | Create a new note with a custom URL alias (requires [FreeURL mode](https://docs.hedgedoc.org/references/url-scheme/#freeurl-mode)) |
| `hedgedoc_create_diagram` | Create a note with a [Mermaid](https://mermaid.js.org/) diagram |
| `hedgedoc_read` | Read the raw markdown content of a note |
| `hedgedoc_info` | Get note metadata (title, description, timestamps, viewcount) |
| `hedgedoc_list_revisions` | List all available revisions of a note |
| `hedgedoc_get_revision` | Get the full content of a specific revision |
| `hedgedoc_publish_url` | Get the published (read-only) URL of a note |
| `hedgedoc_slide_url` | Get the slide presentation URL of a note |
| `hedgedoc_status` | Get the current status of the HedgeDoc instance |

## Usage

```bash
export HEDGEDOC_URL="https://hedgedoc.your-instance.com"
uvx hedgedoc-mcp-server stdio
```

HedgeDoc 1.x does **not** use API tokens for note operations. Authentication is handled via
session cookies (browser) or instance configuration
([see Production Ready guide](https://docs.hedgedoc.org/guides/production-ready/)).

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

### Requirements

| Requirement | Notes |
|---|---|
| HedgeDoc 1.x instance | Tested on 1.x. Not compatible with HedgeDoc 2. |
| Python 3.11+ | |
| `uv` (recommended) | Or `pip install hedgedoc-mcp-server` |

## API Endpoints Used

This server uses the following [HedgeDoc 1.x API](https://docs.hedgedoc.org/dev/api/) endpoints:

| Method | Endpoint | Used by |
|---|---|---|
| `GET` | `/new` | Create a blank note |
| `POST` | `/new` | Create a note (random ID) |
| `POST` | `/new/{alias}` | Create a note (custom alias) |
| `GET` | `/{id}/download` | Read raw markdown |
| `GET` | `/{id}/info` | Read metadata |
| `GET` | `/{id}/revision` | List revisions |
| `GET` | `/{id}/revision/{rev}` | Get specific revision |
| `GET` | `/{id}/publish` | Published URL |
| `GET` | `/{id}/slide` | Slide URL |
| `GET` | `/status` | Instance status |

For more details, see the [official API docs](https://docs.hedgedoc.org/dev/api/).

## Instance Configuration

Your HedgeDoc administrator may need to configure these settings:

| Setting | Impact | Docs |
|---|---|---|
| `CMD_ALLOW_ANONYMOUS=true` | Allows note creation without login | [Users and Privileges](https://docs.hedgedoc.org/configuration/#users-and-privileges) |
| `CMD_ALLOW_FREEURL=true` | Enables custom URL aliases | [Users and Privileges](https://docs.hedgedoc.org/configuration/#users-and-privileges) |
| `CMD_RATE_LIMIT_NEW_NOTES=20` | Max new notes per 5 minutes (default: 20) | [Web Security](https://docs.hedgedoc.org/configuration/#web-security-aspects) |
| `CMD_DOCUMENT_MAX_LENGTH=100000` | Max note length in chars (default: 100k) | [HedgeDoc basics](https://docs.hedgedoc.org/configuration/#hedgedoc-basics) |
| `CMD_DISABLE_NOTE_CREATION=false` | If true, no notes can be created | [Users and Privileges](https://docs.hedgedoc.org/configuration/#users-and-privileges) |

## Development

```bash
git clone https://github.com/Jyzus/kaymer-hedgedoc-mcp
cd kaymer-hedgedoc-mcp
uv venv && uv pip install -e .
HEDGEDOC_URL="https://hedgedoc.your-instance.com" uv run hedgedoc-mcp-server
```

## License

MIT
