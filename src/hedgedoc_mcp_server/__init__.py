import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hedgedoc")

BASE_URL = os.environ.get("HEDGEDOC_URL", "").rstrip("/")
if not BASE_URL:
    raise ValueError("HEDGEDOC_URL environment variable is required (e.g. https://hedgedoc.example.com)")


def _error_message(resp: httpx.Response) -> str:
    status = resp.status_code
    if status == 403:
        return (
            f"403 Forbidden — HedgeDoc rejected the request."
            f" The instance may require authentication or have note creation disabled"
            f" (CMD_DISABLE_NOTE_CREATION)."
        )
    if status == 413:
        return (
            f"413 Content Too Large — Note exceeds maximum length"
            f" (default: 100 000 chars, configurable via CMD_DOCUMENT_MAX_LENGTH)."
        )
    if status == 429:
        return (
            f"429 Too Many Requests — HedgeDoc rate limit hit."
            f" Default is 20 new notes per 5 minutes per user"
            f" (configurable via CMD_RATE_LIMIT_NEW_NOTES)."
        )
    return f"HTTP {status}: {resp.text[:300]}"


async def _create_note(content: str, alias: str | None = None) -> str:
    headers = {"Content-Type": "text/markdown", "User-Agent": "hedgedoc-mcp-server/1.0"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
        if alias:
            resp = await client.post(
                f"{BASE_URL}/new/{alias}",
                headers=headers,
                content=content,
            )
        else:
            resp = await client.post(
                f"{BASE_URL}/new",
                headers=headers,
                content=content,
            )
        if resp.status_code == 302:
            location = resp.headers.get("location", "")
            note_id = location.rstrip("/").rsplit("/", 1)[-1]
            return json.dumps({
                "note_id": note_id,
                "url": f"{BASE_URL}/{note_id}",
                "status": "created",
            }, indent=2, ensure_ascii=False)
        return json.dumps({
            "error": _error_message(resp),
            "status": resp.status_code,
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def hedgedoc_create(title: str, content: str) -> str:
    """Create a new HedgeDoc note with a random ID.

    - title: The title of the note (will be added as level-1 heading)
    - content: The markdown body content
    Returns the note ID and URL.
    Note: HedgeDoc 1.x does not use API tokens. This tool works
    anonymously if the instance allows it (CMD_ALLOW_ANONYMOUS).
    """
    return await _create_note(f"# {title}\n\n{content}")


@mcp.tool()
async def hedgedoc_create_with_alias(alias: str, title: str, content: str) -> str:
    """Create a new HedgeDoc note with a custom URL alias.

    Requires HedgeDoc's FreeURL mode to be enabled on the instance
    (CMD_ALLOW_FREEURL=true).

    - alias: The custom URL slug (e.g. 'my-diagram')
    - title: The title of the note (will be added as level-1 heading)
    - content: The markdown body content
    Returns the note ID and URL.
    """
    return await _create_note(f"# {title}\n\n{content}", alias)


@mcp.tool()
async def hedgedoc_read(note_id: str) -> str:
    """Read the raw markdown content of a HedgeDoc note.

    - note_id: The note ID or alias (the slug from the URL)
    """
    headers = {"User-Agent": "hedgedoc-mcp-server/1.0"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(
            f"{BASE_URL}/{note_id}/download",
            headers=headers,
        )
        if resp.is_success:
            return resp.text
        return json.dumps({
            "error": _error_message(resp),
            "status": resp.status_code,
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def hedgedoc_info(note_id: str) -> str:
    """Get metadata of a HedgeDoc note (title, description, timestamps).

    - note_id: The note ID or alias (the slug from the URL)
    """
    headers = {"User-Agent": "hedgedoc-mcp-server/1.0"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(
            f"{BASE_URL}/{note_id}/info",
            headers=headers,
        )
        if resp.is_success:
            data = resp.json()
            data["url"] = f"{BASE_URL}/{note_id}"
            return json.dumps(data, indent=2, ensure_ascii=False)
        return json.dumps({
            "error": _error_message(resp),
            "status": resp.status_code,
        }, indent=2, ensure_ascii=False)


@mcp.tool()
async def hedgedoc_create_diagram(
    title: str,
    diagram_type: str,
    diagram_code: str,
    description: str = "",
) -> str:
    """Create a HedgeDoc note with a Mermaid diagram.

    HedgeDoc 1.x renders Mermaid natively in the editor.

    - title: The title of the diagram note
    - diagram_type: The Mermaid diagram type (e.g. 'graph TD', 'sequenceDiagram', 'flowchart LR', 'classDiagram', 'gantt', 'pie')
    - diagram_code: The Mermaid diagram body (without the type header)
    - description: Optional explanatory text before the diagram
    Returns the note ID and URL.
    """
    lines = [f"# {title}"]
    if description:
        lines.append("")
        lines.append(description)
    lines.append("")
    lines.append("```mermaid")
    lines.append(diagram_type)
    lines.append(diagram_code)
    lines.append("```")
    return await _create_note("\n".join(lines))


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
