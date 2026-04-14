# go-trainer-mcp

Reusable MCP (Model Context Protocol) servers for Go/Baduk applications. Built for use with [go-trainer-ai](https://github.com/airlangga07/claude-personal-go-trainer) but usable in any Claude-powered Go/Baduk project.

## Servers

| Server | File | Description |
|---|---|---|
| `ogs` | `ogs_server.py` | OGS (Online-Go.com) REST API — list games, download SGF files |
| `katago` | `katago_server.py` | KataGo AI engine via GTP — analyze SGF files, get move scores |
| `sgf` | `sgf_server.py` | SGF file management — read, write, generate problem files |

## Requirements

- Python 3.11+
- KataGo installed locally (for `katago_server`)

## Installation

```bash
git clone https://github.com/airlangga07/go-trainer-mcp.git
cd go-trainer-mcp
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
```

## Connecting to Claude Code

Add to your project's `.claude/settings.json`:

```json
{
  "mcpServers": {
    "ogs": {
      "command": "python",
      "args": ["/path/to/go-trainer-mcp/ogs_server.py"]
    },
    "katago": {
      "command": "python",
      "args": ["/path/to/go-trainer-mcp/katago_server.py"]
    },
    "sgf": {
      "command": "python",
      "args": ["/path/to/go-trainer-mcp/sgf_server.py"]
    }
  }
}
```

## Architecture

See [go-trainer-ai ARCHITECTURE.md](https://github.com/airlangga07/claude-personal-go-trainer/blob/main/ARCHITECTURE.md) for the full system design.
