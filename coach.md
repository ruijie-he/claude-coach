# Claude Coach

Analyze my recent Claude Code prompts and give me one concrete suggestion to improve.
Track whether I'm actually incorporating past suggestions over time.

## Steps

1. Extract recent prompts:
   ```bash
   python3 ~/claude-coach/extract_prompts.py 24
   ```

2. Read the extracted prompts:
   Read `~/claude-coach/recent_prompts.json`

3. Read the curated tips:
   Read `~/claude-coach/tips.md`

4. Load past reviews to check for recurring patterns. Run:
   ```bash
   ls ~/claude-coach/reviews/ 2>/dev/null | sort | tail -7
   ```
   Then read each of the past review files returned (up to 7). If no past reviews exist,
   skip this step.

5. Analyze my prompts against the tips and past reviews. Pick the single most impactful
   suggestion. Check if the same pattern appeared in any past review — if yes, mark it
   RECURRING with the earliest date; if no, mark it NEW. Also identify any patterns flagged
   before but absent today (genuine improvement).

6. Produce a coaching report in this exact format — keep it tight, no padding:

---

## 🧠 Claude Coach — Daily Review

**Prompts analyzed:** [N] · **Past reviews:** [N or "none"]

---

### ✅ [One specific thing you did well today — one sentence, quote the prompt]

---

### 💡 [Short title] `[NEW]` or `[RECURRING since YYYY-MM-DD]`

[One sentence: what pattern you observed, with a direct quote.]

**Revised:**
```
[Rewritten version of the actual prompt]
```
**Original:**
```
[The original prompt]
```

[One sentence: why it matters.]

---

### 📈 Progress

[Only include if a past suggestion is absent today: "✓ [Pattern] — flagged YYYY-MM-DD, not seen today."
 Omit this section entirely if nothing to report.]

---

7. Save today's review. Write the full report to:
   ```
   ~/claude-coach/reviews/YYYY-MM-DD.md
   ```
   Use today's actual date. Overwrite if a file for today already exists.
   Confirm the save path to the user in one line.
