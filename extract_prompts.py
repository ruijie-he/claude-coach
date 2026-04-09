
#!/usr/bin/env python3
"""Extract your Claude Code prompts from the last N hours."""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude" / "projects"
HOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 24


def extract_prompts(hours: int) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    prompts = []

    for project_dir in CLAUDE_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        for jsonl_file in project_dir.glob("*.jsonl"):
            with open(jsonl_file) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Filter by time
                    ts = entry.get("timestamp")
                    if not ts:
                        continue
                    entry_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    if entry_time < cutoff:
                        continue

                    # Extract human messages only
                    msg = entry.get("message", {})
                    if msg.get("role") not in ("human", "user"):
                        continue

                    content = msg.get("content", "")
                    # content can be a string or list of blocks
                    if isinstance(content, list):
                        text = " ".join(
                            b.get("text", "") for b in content
                            if isinstance(b, dict) and b.get("type") == "text"
                        )
                    else:
                        text = str(content)

                    text = text.strip()
                    if not text:
                        continue

                    prompts.append({
                        "timestamp": ts,
                        "project": project_dir.name,
                        "prompt": text,
                    })

    # Sort chronologically
    prompts.sort(key=lambda x: x["timestamp"])
    return prompts


def main():
    prompts = extract_prompts(HOURS)
    if not prompts:
        print(f"No prompts found in the last {HOURS} hours.")
        return

    print(f"Found {len(prompts)} prompts from the last {HOURS} hours:\n")
    for i, p in enumerate(prompts, 1):
        print(f"--- Prompt {i} [{p['timestamp']}] (project: {p['project']}) ---")
        # Truncate very long prompts for display
        preview = p["prompt"][:500] + "..." if len(p["prompt"]) > 500 else p["prompt"]
        print(preview)
        print()

    # Also write to a temp file for the skill to read
    out_path = Path.home() / "claude-coach" / "recent_prompts.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(prompts, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
