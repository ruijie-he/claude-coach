# claude-coach

A daily coaching loop for Claude Code. Analyzes your recent prompts, surfaces patterns, and tracks whether you're actually incorporating suggestions over time.

## How it works

Run `/coach` in any Claude Code session. It will:

1. Extract your prompts from the last 24 hours across all Claude Code projects
2. Compare them against a curated set of best practices
3. Load your past review files to detect **recurring** vs **new** patterns
4. Produce a report with concrete rewrites of your actual prompts
5. Save the report to `~/claude-coach/reviews/YYYY-MM-DD.md`

Each suggestion is tagged `[NEW]` or `[RECURRING since YYYY-MM-DD]`. If the same pattern keeps appearing, you know the habit hasn't stuck yet. Improvements (patterns flagged before but absent today) are called out in a **Progress** section.

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/ruijie-he/claude-coach.git ~/claude-coach
```

### 2. Install the slash command

```bash
cp ~/claude-coach/coach.md ~/.claude/commands/coach.md
```

### 3. Create your reviews folder

```bash
mkdir -p ~/claude-coach/reviews
```

This folder is gitignored — reviews are personal and stay on your machine.

### 4. Run it

Open Claude Code in any project and type:

```
/coach
```

## Files

| File | Purpose |
|------|---------|
| `coach.md` | The `/coach` slash command — install to `~/.claude/commands/` |
| `extract_prompts.py` | Reads `~/.claude/projects/**/*.jsonl` and extracts your prompts |
| `tips.md` | Curated best practices (context management, prompting, CLAUDE.md, workflow, model selection) |
| `reviews/` | Your daily reports — gitignored, personal to each user |

## Requirements

- [Claude Code](https://claude.ai/code) CLI installed
- Python 3.9+
- No external dependencies
