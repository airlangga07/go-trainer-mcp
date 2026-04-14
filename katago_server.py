import os
import json
import subprocess
import tempfile
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

KATAGO_PATH = os.getenv("KATAGO_PATH", "katago")
KATAGO_MODEL_PATH = os.getenv("KATAGO_MODEL_PATH", "")
KATAGO_CONFIG_PATH = os.getenv("KATAGO_CONFIG_PATH", "")

mcp = FastMCP("katago")


def _run_katago_analysis(sgf_path: str, max_visits: int) -> list[dict]:
    """
    Run KataGo in analysis mode on an SGF file.
    Returns a list of per-move analysis objects.
    """
    query = {
        "id": "analysis",
        "initialStones": [],
        "moves": [],
        "rules": "tromp-taylor",
        "komi": 6.5,
        "boardXSize": 19,
        "boardYSize": 19,
        "analyzeTurns": [],
        "maxVisits": max_visits,
        "includeOwnership": True,
    }

    # Read SGF and pass it via sgfFile field
    with open(sgf_path, "r", encoding="utf-8") as f:
        sgf_content = f.read()

    query["sgfFile"] = sgf_path

    cmd = [
        KATAGO_PATH, "analysis",
        "-model", KATAGO_MODEL_PATH,
        "-config", KATAGO_CONFIG_PATH,
    ]

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = process.communicate(
        input=json.dumps(query) + "\n",
        timeout=120,
    )

    if process.returncode != 0:
        raise RuntimeError(f"KataGo exited with code {process.returncode}: {stderr}")

    results = []
    for line in stdout.strip().splitlines():
        line = line.strip()
        if line:
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return results


@mcp.tool()
def analyze_sgf(sgf_path: str, max_visits: int = 200) -> dict:
    """
    Analyze an SGF file using KataGo and return move-by-move analysis.
    max_visits controls analysis depth — higher is slower but more accurate.
    Returns win rate, score estimates, and top move suggestions per turn.
    """
    if not os.path.exists(sgf_path):
        return {"error": f"SGF file not found: {sgf_path}"}

    results = _run_katago_analysis(sgf_path, max_visits)

    return {
        "sgf_path": sgf_path,
        "max_visits": max_visits,
        "moves_analyzed": len(results),
        "analysis": results,
    }


@mcp.tool()
def get_move_scores(sgf_path: str, max_visits: int = 100) -> dict:
    """
    Return per-move score deltas for an SGF file using KataGo.
    Score delta is the change in estimated score after each move — large negative
    deltas indicate mistakes. Useful for identifying the worst moves in a game.
    """
    if not os.path.exists(sgf_path):
        return {"error": f"SGF file not found: {sgf_path}"}

    results = _run_katago_analysis(sgf_path, max_visits)

    move_scores = []
    prev_score = None

    for entry in results:
        turn = entry.get("turnNumber", 0)
        root_info = entry.get("rootInfo", {})
        score = root_info.get("scoreLead", None)

        delta = None
        if prev_score is not None and score is not None:
            delta = score - prev_score

        move_scores.append({
            "turn": turn,
            "score_lead": score,
            "score_delta": delta,
            "win_rate": root_info.get("winrate", None),
        })

        prev_score = score

    # Sort by absolute delta to surface biggest mistakes
    mistakes = sorted(
        [m for m in move_scores if m["score_delta"] is not None],
        key=lambda m: abs(m["score_delta"]),
        reverse=True,
    )

    return {
        "sgf_path": sgf_path,
        "move_scores": move_scores,
        "top_mistakes": mistakes[:5],
    }


if __name__ == "__main__":
    mcp.run()
