# Claude Coach

Analyze my recent Claude Code prompts and give me one concrete suggestion to improve.
Track whether I'm actually incorporating past suggestions over time.

> If cloned somewhere other than `~/claude-coach`, set `CLAUDE_COACH_DIR` in your shell profile.

## Steps

1. Extract recent prompts:
   ```bash
   python3 ~/claude-coach/extract_prompts.py 24
   ```

2. Read the extracted prompts:
   Read `~/claude-coach/recent_prompts.json`

3. Read the curated tips:
   Read `~/claude-coach/tips.md`

4. Load past reviews to check for recurring patterns:
   ```bash
   ls ~/claude-coach/reviews/ 2>/dev/null | sort | tail -7
   ```
   Files are named YYYY-MM-DD_HH-MM.md. Read each returned (up to 7). If none exist,
   skip this step.

5. Analyze my prompts against the tips and past reviews. Pick the single most impactful
   suggestion. Check if the same pattern appeared in any past review — if yes, mark it
   RECURRING with the earliest date; if no, mark it NEW. For Progress: only flag a past
   suggestion if today's prompts show it was actively and meaningfully applied.

6. Produce a coaching report in this exact format — keep it tight, no padding:

---

## 🧠 Claude Coach — Daily Review

**Prompts analyzed:** [N] · **Past reviews:** [N or "none"]

---

### ✅ Good: [Short title]

[One sentence: what you did well, with a direct quote.]

---

### 💡 Improve: [Short title] `[NEW]` or `[RECURRING since YYYY-MM-DD]`

[One sentence: what pattern you observed, with a direct quote.]

**Revised:**
```
[Rewritten version of the actual prompt]
```

**Original:**
```
[The original prompt]
```

[One sentence: why it matters.] → *"[Tip name]"* · [Source](url)

---

### 📈 Progress

[Only include if a past suggestion was actively present today AND the prompt shows meaningful
 incorporation of that feedback: "✓ [Pattern] — flagged YYYY-MM-DD, applied today in: [short quote]."
 Omit this section entirely if no past suggestions were genuinely acted on.]

---

7. Save today's review. Write the full report to:
   ```
   ~/claude-coach/reviews/YYYY-MM-DD_HH-MM.md
   ```
   Use today's actual date and current time (24h, e.g. 2026-04-09_14-32.md).
   Confirm the save path to the user in one line.
