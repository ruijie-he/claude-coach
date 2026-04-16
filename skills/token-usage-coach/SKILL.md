---
name: token-usage-coach
description: Analyze Claude Code session token usage and generate actionable efficiency feedback with cache hit rate, input:output ratio, and per-session pattern detection. Use when users ask for token audits, prompt efficiency analysis, Claude usage waste detection, or coaching on reducing token cost.
---

# Token Usage Coach

Help a developer understand how efficiently they use AI through token consumption patterns across recent Claude Code sessions.

Do not alarm or shame. Surface non-obvious patterns that give the user leverage over how they structure work.

> **Permissions note:** This workflow requires two shell executions (one `node` command to read session data, one to measure this skill's own cost) plus one file write.

## Step 1: Collect session list

Call `list_sessions` to get all available sessions. Record each session's ID, title, and date.

Focus on sessions from the last 14 days. If fewer than 5 sessions exist in that window, include older sessions to ensure a meaningful sample.

## Step 2: Extract token usage from raw session files

The session transcript tool does not expose token usage. Read token usage from local Claude Code JSONL files.

Run one bash command with all target session IDs to avoid repeated prompts:

```bash
node -e "
const fs = require('fs');
const path = require('path');
const home = process.env.HOME || process.env.USERPROFILE;
const projectsDir = path.join(home, '.claude', 'projects');
const sessionIds = [/* paste comma-separated quoted IDs here */];

const results = {};
const subdirs = fs.readdirSync(projectsDir);
for (const sub of subdirs) {
  for (const id of sessionIds) {
    const file = path.join(projectsDir, sub, id + '.jsonl');
    if (!fs.existsSync(file)) continue;
    const lines = fs.readFileSync(file, 'utf8').trim().split('\n');
    const seen = new Set();
    let t = { input: 0, output: 0, cache_creation: 0, cache_read: 0, turns: 0 };
    for (const line of lines) {
      try {
        const obj = JSON.parse(line);
        const u = obj?.message?.usage;
        if (!u || !obj.uuid || seen.has(obj.uuid)) continue;
        seen.add(obj.uuid);
        t.input += u.input_tokens || 0;
        t.output += u.output_tokens || 0;
        t.cache_creation += u.cache_creation_input_tokens || 0;
        t.cache_read += u.cache_read_input_tokens || 0;
        t.turns++;
      } catch {}
    }
    results[id] = t;
  }
}
console.log(JSON.stringify(results, null, 2));
"
```

If a session ID is not found, leave it as unavailable and continue.

## Step 3: Compute derived metrics per session

For each session with usage data, compute:

- **Total tokens** = `input + cache_creation + cache_read + output`
- **Cache hit rate** = `cache_read / (input + cache_creation + cache_read) * 100`
- **Input-to-output ratio** = `(input + cache_creation + cache_read) / output`
- **Cache write ratio** = `cache_creation / (input + cache_creation + cache_read) * 100`

Then compute the same metrics across all sessions combined as the baseline.

## Step 4: Identify patterns worth surfacing

Look for these signals:

- **Expensive re-prompting:** `cache_hit_rate < 20%` and more than 3 turns.
- **Context bloat:** `input_to_output_ratio > 15:1`.
- **Short high-cost sessions:** fewer than 4 turns with high total token count.
- **Good patterns:** cache hit rate above 60%, or high output relative to input.

## Step 5: Generate the report

Create `reflection-notes/` if missing, then write:

`reflection-notes/[YYYY-MM-DD]-token-coach.md`

Use today's date and this structure:

```markdown
# Token Usage Report — [date]

## How to read this report

**Cache hit rate** measures how much of the context Claude read was already stored from a previous turn in the same session, versus freshly sent. When you send a message, Claude receives the full conversation history — your CLAUDE.md, the system prompt, every prior message. On the first turn, all of that gets processed (and cached) for the first time. On subsequent turns in the same session, Claude can read it from cache instead of reprocessing it. Cache reads cost roughly 10× less than fresh input tokens.

A **high cache hit rate** (above 50%) means your sessions are long enough and consistent enough that Claude is compounding on earlier context rather than rebuilding it from scratch. A **low cache hit rate** (below 20%) usually means one of three things: you're starting a new session for every task instead of continuing an existing one; your prompts change structure dramatically between turns; or your sessions are so short there's nothing to reuse.

**How to improve your cache hit rate:**
- Continue work within a single session rather than opening a new one for each task
- Keep your CLAUDE.md stable — every edit invalidates the cache for that file
- Batch related questions into one session rather than spreading them across several
- Avoid pasting large file contents that change between turns; reference file paths instead

**Input:output ratio** is the total tokens sent in (fresh + cached) divided by tokens generated. A 5:1 ratio is typical. Above 15:1 suggests you're sending a lot of context relative to what you're getting back — often a sign of context bloat or short exploratory sessions that were abandoned.

---

## Session snapshot

| Session | Date | Turns | Total tokens | Cache hit % | Input:Output |
|---------|------|-------|-------------|-------------|--------------|
[One row per session. Use the session title from list_sessions, or the JSONL slug if title unavailable. Round token counts to nearest 100. Round ratios to 1 decimal place.]

**Combined average cache hit rate:** [x%]
**Combined average input:output ratio:** [x:1]

---

## What the numbers suggest

[Write 2–3 paragraphs with interpretation, not number restatement. Name sessions, ratios, and likely causes.]

---

## Where tokens are working well

[Name 1–2 specific efficient patterns. If none, state baseline is reasonable or call out broad inefficiency briefly.]

---

## Suggested changes (pick one to try first)

[Give exactly 2–3 numbered suggestions, ranked by impact. Each suggestion must be 2–4 sentences: what to do, which sessions prompted it, and why it helps mechanically.]

---

## What this doesn't tell you

Token efficiency is not the same as outcome quality. A short, cheap session that unblocked a hard decision is worth more than a long, efficient one that produced mediocre output. Use these numbers to catch waste — not to optimise for their own sake.
```

## Step 6: Report the cost of this run

Before presenting output, run extraction for the current session ID:

```bash
node -e "
const fs = require('fs');
const path = require('path');
const home = process.env.HOME || process.env.USERPROFILE;
const projectsDir = path.join(home, '.claude', 'projects');
const sessionId = '<YOUR_CURRENT_SESSION_ID>';

const seen = new Set();
let t = { input: 0, output: 0, cache_creation: 0, cache_read: 0, turns: 0 };
const subdirs = fs.readdirSync(projectsDir);
for (const sub of subdirs) {
  const file = path.join(projectsDir, sub, sessionId + '.jsonl');
  if (!fs.existsSync(file)) continue;
  const lines = fs.readFileSync(file, 'utf8').trim().split('\n');
  for (const line of lines) {
    try {
      const obj = JSON.parse(line);
      const u = obj?.message?.usage;
      if (!u || !obj.uuid || seen.has(obj.uuid)) continue;
      seen.add(obj.uuid);
      t.input += u.input_tokens || 0;
      t.output += u.output_tokens || 0;
      t.cache_creation += u.cache_creation_input_tokens || 0;
      t.cache_read += u.cache_read_input_tokens || 0;
      t.turns++;
    } catch {}
  }
}
const total = t.input + t.cache_creation + t.cache_read + t.output;
console.log('This run: ' + total.toLocaleString() + ' tokens total (' +
  t.input + ' input / ' + t.cache_creation + ' cache write / ' +
  t.cache_read + ' cache read / ' + t.output + ' output)');
"
```

This captures usage up to script execution time. Final session total will be slightly higher after the closing response.

Include this run cost as a footer line in the report file and in spoken summary.

## Step 7: Present output

After writing the report file:

1. Share a `computer://` link to the file.
2. Give a 2–3 sentence summary with:
   - The single most actionable pattern.
   - What to do differently in the next session.
   - How many tokens this run cost.

Keep delivery direct and non-apologetic.
