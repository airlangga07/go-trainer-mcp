import os
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

OGS_API_BASE = "https://online-go.com/api/v1"
OGS_API_KEY = os.getenv("OGS_API_KEY")
SGF_DIR = os.getenv("SGF_DIR", ".")

mcp = FastMCP("ogs")


def _headers() -> dict:
    return {"Authorization": f"Bearer {OGS_API_KEY}"}


@mcp.tool()
def get_ogs_games(username: str, limit: int = 20) -> dict:
    """
    Fetch a list of recent games for a player from OGS.
    Returns a list of game objects with id, players, result, and date.
    """
    url = f"{OGS_API_BASE}/players/{username}/games/"
    params = {"page_size": limit}

    with httpx.Client() as client:
        response = client.get(url, headers=_headers(), params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

    games = []
    for game in data.get("results", []):
        games.append({
            "ogs_id": str(game["id"]),
            "player_black": game["players"]["black"]["username"],
            "player_white": game["players"]["white"]["username"],
            "result": game.get("outcome", ""),
            "winner": game.get("winner", ""),
            "game_date": game.get("ended", ""),
            "width": game.get("width", 19),
            "height": game.get("height", 19),
        })

    return {"games": games, "total": data.get("count", len(games))}


@mcp.tool()
def download_sgf(ogs_game_id: str, dest_path: str = "") -> dict:
    """
    Download the SGF file for a given OGS game ID and save it locally.
    If dest_path is not provided, saves to SGF_DIR/{ogs_game_id}.sgf.
    Returns the path where the file was saved.
    """
    if not dest_path:
        dest_path = os.path.join(SGF_DIR, f"{ogs_game_id}.sgf")

    url = f"{OGS_API_BASE}/games/{ogs_game_id}/sgf/"

    with httpx.Client() as client:
        response = client.get(url, headers=_headers(), timeout=15)
        response.raise_for_status()
        sgf_content = response.text

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(sgf_content)

    return {"ogs_game_id": ogs_game_id, "sgf_path": dest_path, "size_bytes": len(sgf_content.encode())}


@mcp.tool()
def get_game_details(ogs_game_id: str) -> dict:
    """
    Fetch full metadata for a specific OGS game by its ID.
    Returns game details including players, result, moves count, and board size.
    """
    url = f"{OGS_API_BASE}/games/{ogs_game_id}/"

    with httpx.Client() as client:
        response = client.get(url, headers=_headers(), timeout=15)
        response.raise_for_status()
        game = response.json()

    return {
        "ogs_id": str(game["id"]),
        "player_black": game["players"]["black"]["username"],
        "player_white": game["players"]["white"]["username"],
        "result": game.get("outcome", ""),
        "winner": game.get("winner", ""),
        "game_date": game.get("ended", ""),
        "moves": game.get("moves", []),
        "width": game.get("width", 19),
        "height": game.get("height", 19),
        "handicap": game.get("handicap", 0),
        "komi": game.get("komi", 6.5),
        "ranked": game.get("ranked", False),
    }


if __name__ == "__main__":
    mcp.run()
