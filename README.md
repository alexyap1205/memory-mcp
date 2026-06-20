# memory-mcp

A collection of MCP servers for long-term agent memory, each backed by a different storage backend.

## Packages

| Package | Backend | Description |
|---------|---------|-------------|
| [`sqlite-memory`](sqlite_memory/README.md) | SQLite + Markdown | Lightweight local memory with a `MEMORY.md` index and SQLite detail store |

## Design philosophy

Each package follows the same pattern:

- **Index** — a fast, lightweight summary store the agent loads at session start
- **Detail** — full markdown content fetched on demand by ID
- **Three tools** — `save_memory`, `get_memory`, `delete_memory`
- **One resource** — `memory://<backend>/index` for loading the full index

This keeps context usage low: the agent sees all memory summaries upfront and only fetches the full detail for entries it needs.

## Structure

```
memory-mcp/
├── sqlite_memory/       ← SQLite + MEMORY.md backend
│   ├── server.py
│   ├── pyproject.toml
│   └── README.md
├── pyproject.toml       ← uv workspace root
├── LICENSE
└── README.md
```

## Adding a new package

1. Create a new directory (e.g. `postgres_memory/`)
2. Add `pyproject.toml` and `server.py` following the same tool/resource interface
3. Register it in the workspace root `pyproject.toml`:

```toml
[tool.uv.workspace]
members = ["sqlite_memory", "postgres_memory"]
```

4. Run `uv sync`

## License

MIT — see [LICENSE](LICENSE). Free to use, modify, and distribute with attribution.
