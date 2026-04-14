import os
import glob
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import sgfmill.sgf as sgf_lib
import sgfmill.boards as boards

load_dotenv()

SGF_DIR = os.getenv("SGF_DIR", ".")

mcp = FastMCP("sgf")


@mcp.tool()
def read_sgf(sgf_path: str) -> dict:
    """
    Parse an SGF file and return structured game data.
    Returns board size, players, moves sequence, and game result.
    """
    if not os.path.exists(sgf_path):
        return {"error": f"SGF file not found: {sgf_path}"}

    with open(sgf_path, "rb") as f:
        game = sgf_lib.Sgf_game.from_bytes(f.read())

    root = game.get_root()
    size = game.get_size()

    moves = []
    for node in game.main_sequence_iter():
        color, point = node.get_move()
        if color and point:
            col, row = point
            moves.append({
                "color": "black" if color == "b" else "white",
                "col": col,
                "row": row,
            })

    return {
        "sgf_path": sgf_path,
        "board_size": size,
        "player_black": root.get("PB") or "",
        "player_white": root.get("PW") or "",
        "result": root.get("RE") or "",
        "komi": root.get("KM") or 6.5,
        "date": root.get("DT") or "",
        "total_moves": len(moves),
        "moves": moves,
    }


@mcp.tool()
def generate_problem_sgf(
    moves: list[dict],
    description: str,
    weakness_tag: str,
    dest_path: str = "",
) -> dict:
    """
    Generate an SGF problem file from a sequence of moves.
    moves: list of {"color": "black"|"white", "col": int, "row": int}
    description: human-readable problem description (stored as SGF comment)
    weakness_tag: category of weakness e.g. "joseki", "endgame", "life_and_death"
    dest_path: where to save the file; defaults to SGF_DIR/problems/{weakness_tag}_{timestamp}.sgf
    Returns the path to the generated SGF file.
    """
    if not dest_path:
        import time
        timestamp = int(time.time())
        problems_dir = os.path.join(SGF_DIR, "problems")
        os.makedirs(problems_dir, exist_ok=True)
        dest_path = os.path.join(problems_dir, f"{weakness_tag}_{timestamp}.sgf")

    game = sgf_lib.Sgf_game(size=19)
    root = game.get_root()
    root.set("GN", description)
    root.set("C", f"Weakness: {weakness_tag}\n\n{description}")
    root.set("GC", weakness_tag)

    node = root
    for move in moves:
        color = "b" if move["color"] == "black" else "w"
        point = (move["col"], move["row"])
        new_node = node.new_child()
        new_node.set_move(color, point)
        node = new_node

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(game.serialise())

    return {
        "sgf_path": dest_path,
        "description": description,
        "weakness_tag": weakness_tag,
        "total_moves": len(moves),
    }


@mcp.tool()
def list_sgf_files(directory: str = "", pattern: str = "*.sgf") -> dict:
    """
    List SGF files in a directory.
    Defaults to SGF_DIR if no directory is specified.
    Returns file paths sorted by modification time (newest first).
    """
    search_dir = directory or SGF_DIR
    if not os.path.exists(search_dir):
        return {"error": f"Directory not found: {search_dir}", "files": []}

    files = glob.glob(os.path.join(search_dir, "**", pattern), recursive=True)
    files.sort(key=os.path.getmtime, reverse=True)

    return {
        "directory": search_dir,
        "total": len(files),
        "files": [
            {
                "path": f,
                "filename": os.path.basename(f),
                "size_bytes": os.path.getsize(f),
                "modified": os.path.getmtime(f),
            }
            for f in files
        ],
    }


if __name__ == "__main__":
    mcp.run()
