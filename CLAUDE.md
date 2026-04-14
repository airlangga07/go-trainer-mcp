# CLAUDE.md — go-trainer-mcp

## Purpose
Reusable MCP servers for Go/Baduk applications. Each server exposes domain-specific tools to Claude Code via the Model Context Protocol.

## Servers
- `ogs_server.py` — OGS REST API tools
- `katago_server.py` — KataGo GTP engine tools
- `sgf_server.py` — SGF file management tools

## Development Conventions

### Commits
- One commit per server/milestone — conventional commit format
- `feat:` for new servers or tools, `fix:` for bug fixes, `docs:` for docs only
- Always push after committing

### MCP Tool Design Rules
- Every tool must be **idempotent** — safe to call multiple times with the same args
- Every tool must return **structured JSON** — no plain text responses
- Tools must be **stateless** — no in-memory state between calls; read from env/filesystem each time
- Every tool must have a **clear docstring** — Claude uses it to decide when to call the tool

### Milestone Tracking
Milestones are tracked in the main repo's `ARCHITECTURE.md` under "go-trainer-mcp" section.

## Hard Rules
- **Never commit `.env`** — it contains API keys
- Tools must never write outside of configured directories (`SGF_DIR`, etc.)
