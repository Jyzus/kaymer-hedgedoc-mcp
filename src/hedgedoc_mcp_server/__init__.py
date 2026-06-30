import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hedgedoc")

BASE_URL = os.environ.get("HEDGEDOC_URL", "").rstrip("/")
if not BASE_URL:
    raise ValueError("HEDGEDOC_URL environment variable is required (e.g. https://hedgedoc.example.com)")

HEADERS = {
    "User-Agent": "OpenCode-HedgeDoc-MCP/1.0",
}
if token := os.environ.get("HEDGEDOC_TOKEN"):
    HEADERS["Authorization"] = f"Bearer {token}"


@mcp.tool()
async def hedgedoc_create(title: str, content: str) -> str:
    """Create a new HedgeDoc note.

    - title: The title of the note (will be added as level-1 heading)
    - content: The markdown body content
    Returns the note ID and URL.
    """
    full_markdown = f"# {title}\n\n{content}"
    async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
        resp = await client.post(
            f"{BASE_URL}/new",
            headers={**HEADERS, "Content-Type": "text/markdown"},
            content=full_markdown,
        )
        if resp.status_code == 302:
            location = resp.headers.get("location", "")
            note_id = location.rstrip("/").rsplit("/", 1)[-1]
            return json.dumps({
                "note_id": note_id,
                "url": f"{BASE_URL}/{note_id}",
                "status": "created",
            }, indent=2, ensure_ascii=False)
        resp.raise_for_status()
        return f"Created note (status {resp.status_code}): {resp.text[:500]}"


@mcp.tool()
async def hedgedoc_read(note_id: str) -> str:
    """Read the raw markdown content of a HedgeDoc note.

    - note_id: The note ID or alias (the slug from the URL)
    """
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(
            f"{BASE_URL}/{note_id}/download",
            headers=HEADERS,
        )
        resp.raise_for_status()
        return resp.text


@mcp.tool()
async def hedgedoc_info(note_id: str) -> str:
    """Get metadata of a HedgeDoc note (title, description, timestamps).

    - note_id: The note ID or alias (the slug from the URL)
    """
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(
            f"{BASE_URL}/{note_id}/info",
            headers=HEADERS,
        )
        resp.raise_for_status()
        data = resp.json()
        data["url"] = f"{BASE_URL}/{note_id}"
        return json.dumps(data, indent=2, ensure_ascii=False)


@mcp.tool()
async def hedgedoc_create_diagram(
    title: str,
    diagram_type: str,
    diagram_code: str,
    description: str = "",
) -> str:
    """Create a HedgeDoc note with a Mermaid diagram.

    - title: The title of the diagram note
    - diagram_type: The Mermaid diagram type header (e.g. 'graph TD', 'sequenceDiagram', 'flowchart LR')
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
    full_markdown = "\n".join(lines)

    async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
        resp = await client.post(
            f"{BASE_URL}/new",
            headers={**HEADERS, "Content-Type": "text/markdown"},
            content=full_markdown,
        )
        if resp.status_code == 302:
            location = resp.headers.get("location", "")
            note_id = location.rstrip("/").rsplit("/", 1)[-1]
            return json.dumps({
                "note_id": note_id,
                "url": f"{BASE_URL}/{note_id}",
                "status": "created",
            }, indent=2, ensure_ascii=False)
        resp.raise_for_status()
        return f"Created diagram note (status {resp.status_code}): {resp.text[:500]}"


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
