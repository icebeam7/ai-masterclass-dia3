"""Local didactic MCP tool log; safe metadata only, not a production trace collector."""
import json
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path("results/mcp_calls.jsonl")

def record_call(tool: str, metadata: dict, status: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Redactamos argumentos: registro solo nombres, longitudes, estatus; sin consultas ni contenido.
    event = {"time": datetime.now(timezone.utc).isoformat(), "tool": tool,
             "input_length": sum(len(str(v)) for v in metadata.values()), "status": status}
    with LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")

def latest_calls(limit: int = 20) -> list[dict]:
    if not LOG_PATH.exists():
        return []
    return [json.loads(line) for line in LOG_PATH.read_text(encoding="utf-8").splitlines()[-limit:] if line.strip()]
