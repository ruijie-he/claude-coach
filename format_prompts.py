#!/usr/bin/env python3
"""Print recent prompts in a readable format for claude-coach analysis."""
import json
from pathlib import Path

data_file = Path(__file__).parent / "recent_prompts.json"
with open(data_file) as f:
    prompts = json.load(f)

print(f"Total prompts: {len(prompts)}\n")
for p in prompts:
    text = p["prompt"]
    if len(text) > 400:
        text = text[:400] + "...[truncated]"
    text = text.replace("\n", " ")
    print(f"[{p['timestamp']}] [{p['project']}] {text}")
