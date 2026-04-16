# Token Usage Coach

Analyze my recent Claude Code sessions and coach me on token efficiency (cache usage, context bloat, and session structure).

> If cloned somewhere other than `~/claude-coach`, set `CLAUDE_COACH_DIR` in your shell profile and use that path for report output.

## Steps

1. Collect sessions:
   - Call `list_sessions` and capture ID, title, and date.
   - Prioritize sessions from the last 14 days.
   - If fewer than 5 sessions exist in that window, include older sessions to reach at least 5.

2. Extract token usage from local Claude JSONL files in one command:
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

   If a session ID is missing, mark it unavailable and continue.

3. Compute metrics for each session and combined baseline:
   - `total_tokens = input + cache_creation + cache_read + output`
   - `cache_hit_rate = cache_read / (input + cache_creation + cache_read) * 100`
   - `input_to_output = (input + cache_creation + cache_read) / output`
   - `cache_write_ratio = cache_creation / (input + cache_creation + cache_read) * 100`

4. Surface patterns:
   - **Expensive re-prompting:** `cache_hit_rate < 20%` and `turns > 3`
   - **Context bloat:** `input_to_output > 15:1`
   - **Short high-cost sessions:** `turns < 4` with high total tokens
   - **Good patterns:** cache hit > 60% or high output relative to input

5. Write report to:
   ```
   ~/claude-coach/reflection-notes/YYYY-MM-DD-token-coach.md
   ```

   Create `~/claude-coach/reflection-notes/` if it does not exist.

   Use this exact structure:

---

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

[Write 2–3 paragraphs with interpretation (not restating numbers). Name sessions, ratios, and likely causes.]

---

## Where tokens are working well

[Name 1–2 specific efficient patterns. If none, say so briefly and move on.]

---

## Suggested changes (pick one to try first)

[Give exactly 2–3 numbered suggestions ranked by impact. Each suggestion is 2–4 sentences: what to do, which sessions prompted it, and why it helps mechanically.]

---

## What this doesn't tell you

Token efficiency is not the same as outcome quality. A short, cheap session that unblocked a hard decision is worth more than a long, efficient one that produced mediocre output. Use these numbers to catch waste — not to optimise for their own sake.

---

6. Measure this run's own cost before final reply:
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

   Add this run cost as a footer line in the saved report and in your spoken summary.

7. Present output:
   - Share a `computer://` link to the saved report.
   - Give a direct 2–3 sentence summary: most actionable pattern, what to do in the next session, and run token cost.
   - Keep tone factual and non-judgmental.
