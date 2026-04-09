# Claude Coach

Analyze my recent Claude Code prompts and give me concrete suggestions to improve.
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

5. Analyze my prompts against the tips and past reviews. For each suggestion:
   - Check if the same pattern appeared in any past review file
   - If yes, mark it RECURRING and note the earliest date it was flagged
   - If no, mark it NEW
   Also identify any patterns that were flagged in past reviews but are NOT present today —
   those represent genuine improvement.

6. Produce a coaching report in this exact format:

---

## 🧠 Claude Coach — Daily Review

**Prompts analyzed:** [N]
**Period:** Last 24 hours
**Past reviews loaded:** [N reviews, date range, or "none — first run"]

---

### 💡 Suggestion 1: [Short title] `[NEW]` or `[RECURRING since YYYY-MM-DD]`

**Pattern observed:** [What you noticed — be specific, quote the actual prompt]

**Why it matters:** [One sentence on the impact]

**Revised prompt:**
```
[Concrete rewritten version of one of my actual prompts]
```

**Original prompt:**
```
[The original prompt you're improving]
```

---

### 💡 Suggestion 2: [Short title] `[NEW]` or `[RECURRING since YYYY-MM-DD]`

[Same format]

---

### 💡 Suggestion 3: [Short title] `[NEW]` or `[RECURRING since YYYY-MM-DD]`

[Same format]

---

### ✅ What you're doing well

[1-2 things observed that are already good practice — be specific]

---

### 📈 Progress since last review

[If past reviews exist: list any patterns that were flagged before but not observed today.
 Format: "✓ [Pattern name] — last flagged YYYY-MM-DD, not seen today."
 If no improvement observed or no past reviews: omit this section entirely.]

---

Keep suggestions actionable and grounded in my actual prompts. Do not give generic
advice — every suggestion must reference something I actually typed today.
If fewer than 3 meaningful improvements exist, give fewer. Quality over quantity.

7. Save today's review. Write the full report (everything from the "## 🧠 Claude Coach"
   header to the end) to:
   ```
   ~/claude-coach/reviews/YYYY-MM-DD.md
   ```
   Use today's actual date. If a file for today already exists, overwrite it.
   After saving, confirm the path to the user.
