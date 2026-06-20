#!/usr/bin/env python3
import sqlite3
import os
import re
from datetime import datetime
from fastmcp import FastMCP

mcp = FastMCP("Python Memory Server")

BASE_DIR = os.environ.get(
    "MEMORY_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory")
)
MEMORY_DIR = BASE_DIR
DB_PATH = os.path.join(MEMORY_DIR, "memories.db")
INDEX_PATH = os.path.join(MEMORY_DIR, "MEMORY.md")


def init():
    os.makedirs(MEMORY_DIR, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

    if not os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, "w") as f:
            f.write("# Memory Index\n\n")


init()


@mcp.resource("memory://index")
def get_index() -> str:
    """The full memory index. Read this at the start of a session to see all
    saved memories and their IDs before deciding which to fetch in full."""
    with open(INDEX_PATH, "r") as f:
        return f.read()


@mcp.tool()
def save_memory(summary: str, content: str) -> str:
    """
    Save an important fact, user preference, workflow rule, or project decision.
    Provide a short summary (one line, for the index) and a full markdown entry
    with details.
    """
    created_at = datetime.utcnow().isoformat()

    # Insert to DB first to get the auto-generated ID
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO memory_details (content, created_at) VALUES (?, ?)",
            (content, created_at)
        )
        memory_id = cursor.lastrowid
        conn.commit()

    # Append index entry to MEMORY.md
    date_str = created_at[:10]
    with open(INDEX_PATH, "a") as f:
        f.write(f"- [{memory_id}] {summary} — _{date_str}_\n")

    return f"Saved memory [{memory_id}]: '{summary}'"


@mcp.tool()
def get_memory(memory_id: int) -> str:
    """
    Retrieve the full markdown detail of a memory by its ID. Use after reading
    MEMORY.md to identify which memory to fetch.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT content, created_at FROM memory_details WHERE id = ?",
            (memory_id,)
        )
        result = cursor.fetchone()

    if not result:
        return f"Memory with ID {memory_id} not found."

    content, created_at = result
    return f"_Saved: {created_at}_\n\n{content}"


@mcp.tool()
def delete_memory(memory_id: int) -> str:
    """
    Delete a memory by ID. Removes the index entry from MEMORY.md and the
    detail from the database.
    """
    with open(INDEX_PATH, "r") as f:
        lines = f.readlines()

    pattern = re.compile(rf"^- \[{memory_id}\] .+\n?$")
    new_lines = [l for l in lines if not pattern.match(l)]

    if len(new_lines) == len(lines):
        return f"Memory [{memory_id}] not found in index."

    # Update MEMORY.md before DB so a crash leaves no dangling index entry
    with open(INDEX_PATH, "w") as f:
        f.writelines(new_lines)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM memory_details WHERE id = ?", (memory_id,))
        conn.commit()

    return f"Deleted memory [{memory_id}]."


if __name__ == "__main__":
    mcp.run()
