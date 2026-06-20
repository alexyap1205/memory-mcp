# sqlite-memory

A lightweight MCP server for long-term memory, backed by SQLite. Stores a short summary index in `MEMORY.md` and full markdown detail in a SQLite database.

## How it works

```
memory/
├── MEMORY.md       ← one-line summaries + IDs, loaded by the agent at session start
└── memories.db     ← full markdown detail, keyed by ID
```

At the start of a session, the agent reads the `memory://index` resource to see all saved memories. It then calls `get_memory` only for the entries it needs — no keyword guessing required.

## Tools

| Tool | Args | Description |
|------|------|-------------|
| `save_memory` | `summary: str`, `content: str` | Save a short summary (for the index) and full markdown detail |
| `get_memory` | `memory_id: int` | Fetch the full markdown detail for a memory |
| `delete_memory` | `memory_id: int` | Remove a memory from both the index and the database |

## Resource

| URI | Description |
|-----|-------------|
| `memory://index` | Full contents of `MEMORY.md` — read this to see all memories |

## Setup

```bash
uv sync
```

## Configuration

By default, memory files are stored in `memory/` at the repo root (resolved relative to `server.py`, not the working directory). Override with the `MEMORY_DIR` environment variable:

```bash
MEMORY_DIR=/custom/path uv run python sqlite_memory/server.py
```

## MCP Configuration

Add to your Claude Code MCP config (`~/.claude/claude_desktop_config.json` or `.claude/settings.json`):

```json
{
  "mcpServers": {
    "memory": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/memory-mcp",
        "run",
        "python",
        "sqlite_memory/server.py"
      ]
    }
  }
}
```

Replace `/path/to/memory-mcp` with the absolute path to this repo. To use a custom memory directory, add an `"env"` key:

```json
{
  "mcpServers": {
    "memory": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/memory-mcp",
        "run",
        "python",
        "sqlite_memory/server.py"
      ],
      "env": {
        "MEMORY_DIR": "/custom/path/to/memory"
      }
    }
  }
}
```

## Example usage

```
# Agent reads memory://index at session start:
# Memory Index
#
# - [1] User prefers uv for Python package management — 2026-06-20
# - [2] Project uses FastMCP for MCP servers — 2026-06-20

# Agent fetches detail for a relevant entry:
get_memory(1)
# → _Saved: 2026-06-20T06:05:15_
# → ## uv
# → Use uv for all Python package management tasks...

# Agent saves a new memory:
save_memory(
    summary="SQLite memory MCP stores index in MEMORY.md",
    content="## Design\n\nIndex is a flat markdown file...",
)
```
