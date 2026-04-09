# Claude Code Best Practices

> Consolidated and deduplicated from four sources:
> - [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) (community list)
> - [50 Claude Code Tips](https://getpushtoprod.substack.com/p/50-claude-code-tips-to-get-you-started) (getpushtoprod)
> - [32 Claude Code Tips](https://agenticcoding.substack.com/p/32-claude-code-tips-from-basics-to) (agenticcoding)
> - [Official Anthropic Best Practices](https://code.claude.com/docs/en/best-practices)

---

## 1. Context Management

Context is the primary constraint in Claude Code — performance degrades as the window fills.

- **`/clear` between unrelated tasks.** Mixing topics pollutes context. The "kitchen sink session" (one task, then tangent, then back) is the most common failure pattern.
- **Fresh, condensed context beats large context.** Start new conversations for different topics. A clean session with a better prompt almost always outperforms a long session with accumulated corrections.
- **Use `/compact` proactively.** Don't wait for auto-compaction. Run `/compact Focus on the API changes` with explicit instructions on what to preserve. Compact manually at ~50% context capacity.
- **Customize compaction in CLAUDE.md.** Add instructions like: `"When compacting, always preserve the full list of modified files and any test commands."` This ensures critical context survives.
- **Use subagents for investigation.** When exploring a codebase, Claude reads many files — all consuming context. Delegate with `"Use subagents to investigate X"`. They report summaries back without bloating your main session.
- **Lazy-load context.** Load file details only when needed. Avoid front-loading the whole codebase into a conversation.
- **Scope investigations narrowly.** Asking Claude to "investigate" without boundaries can fill the window with hundreds of irrelevant file reads. Give a target, not an open-ended mandate.
- **Use `/btw` for side questions.** The answer appears in a dismissible overlay and never enters conversation history — ideal for quick lookups that shouldn't grow context.
- **After two failed corrections, reset.** If you've corrected Claude twice on the same issue, context is polluted with failed approaches. Run `/clear` and start fresh with a better prompt.
- **Monitor token usage.** Use `/context` to audit usage. Configure a custom status line to track context fill in real time.
- **`/resume` and `--continue` for multi-session tasks.** Context is saved locally. Use `claude --continue` (most recent) or `claude --resume` (pick from list) to pick up across sessions without re-explaining.

---

## 2. Prompting Style

The quality of Claude's output is directly determined by the precision of your prompts and the verification criteria you provide.

### Give Claude a way to verify its work
This is the single highest-leverage practice. Claude performs dramatically better when it can self-check.

- Provide tests, expected outputs, or screenshots as success criteria.
- For UI changes: `"Take a screenshot of the result and compare it to the original. List differences and fix them."`
- For bugs: `"Write a failing test that reproduces the issue, then fix it."` Not just `"fix the login bug"`.
- For build failures: paste the error and say `"Fix it and verify the build succeeds. Address the root cause, don't suppress the error."`

### Explore → Plan → Implement → Commit
Don't let Claude jump straight to coding. Separate phases produce better results:

1. **Explore** (Plan Mode): Claude reads files, answers questions, makes no changes.
2. **Plan** (Plan Mode): `"What files need to change? Create a plan."` Press `Ctrl+G` to edit the plan before Claude proceeds.
3. **Implement** (Normal Mode): Execute against the plan; verify with tests.
4. **Commit**: `"Commit with a descriptive message and open a PR."`

> Skip planning for small, clear tasks (typo fixes, single-line changes). Planning adds overhead — only use it when scope is uncertain or changes span multiple files.

### Be specific
- **Scope the task:** Not `"add tests for foo.py"` but `"write a test for foo.py covering the edge case where the user is logged out. Avoid mocks."`
- **Point to sources:** `"Look through ExecutionFactory's git history and summarize how its API came to be."`
- **Reference existing patterns:** `"Look at HotDogWidget.php to understand the patterns, then follow them to implement a calendar widget."`
- **Describe symptoms precisely:** Include file location, what "fixed" looks like, and how to verify.

### Provide rich content
- Use `@filename` to reference files directly — Claude reads them before responding.
- Paste screenshots and images inline.
- Pipe data: `cat error.log | claude`
- Give URLs for documentation. Use `/permissions` to allowlist frequently-used domains.
- Tell Claude to fetch context itself using Bash commands or MCP tools.

### Let Claude interview you
For complex features, start with a minimal description and ask Claude to interview you first:

```
I want to build [brief description]. Interview me in detail using the AskUserQuestion tool.
Ask about technical implementation, UI/UX, edge cases, concerns, and tradeoffs.
Keep interviewing until we've covered everything, then write a complete spec to SPEC.md.
```

Then start a fresh session to execute. Clean context, written spec to reference.

### Other prompting tips
- **Recovery strategy:** `"Knowing everything now, scrap the current approach and implement an elegant solution."` Useful after a messy debugging session.
- **Challenge Claude:** Ask it to grill you on your proposed changes before merging. Ask for proof.
- **Goals over steps:** Give constraints and goals rather than prescriptive steps. Don't micromanage the implementation approach.
- **Vague prompts have their place.** `"What would you improve in this file?"` can surface unexpected insights during exploration.
- **Ask codebase questions freely.** Treat Claude like a senior engineer: `"How does logging work?"`, `"Why does this call foo() instead of bar()?"`, `"What edge cases does CustomerOnboardingFlowImpl handle?"`

---

## 3. CLAUDE.md Setup

CLAUDE.md is loaded at the start of every session. It provides persistent context Claude can't infer from code alone.

### Getting started
- Run `/init` to auto-generate a CLAUDE.md from your current project structure.
- Commit CLAUDE.md to git so the whole team benefits. It compounds in value over time.
- Use `CLAUDE.local.md` (add to `.gitignore`) for personal project-specific notes.

### Size and structure
- **Keep it short.** Target under 200 lines. One source recommends ~60 lines as optimal. Bloated files cause Claude to ignore critical rules.
- **For each line, ask:** *"Would removing this cause Claude to make mistakes?"* If not, cut it.
- **If Claude ignores a rule:** the file is too long and the rule is getting lost. Prune.
- **If Claude asks questions answered in CLAUDE.md:** the phrasing is ambiguous. Rewrite.
- Add emphasis (`IMPORTANT`, `YOU MUST`) to improve adherence on critical rules.

### What to include vs. exclude

| Include | Exclude |
|---------|---------|
| Bash commands Claude can't guess | Anything Claude can infer from reading code |
| Code style rules that differ from defaults | Standard conventions Claude already knows |
| Testing instructions and preferred test runners | Detailed API documentation (link instead) |
| Repository etiquette (branch naming, PR conventions) | Information that changes frequently |
| Architectural decisions specific to your project | Long explanations or tutorials |
| Developer environment quirks (required env vars) | File-by-file codebase descriptions |
| Common gotchas and non-obvious behaviors | Self-evident practices like "write clean code" |

### Hierarchy and imports
CLAUDE.md files can be placed at multiple levels — all relevant ones are loaded:

- `~/.claude/CLAUDE.md` — applies to all projects globally
- `./CLAUDE.md` — project root; check into git
- `./CLAUDE.local.md` — personal project overrides; gitignore this
- Parent directories — useful for monorepos
- Child directories — loaded on demand when Claude works in those directories

Import other files with `@path/to/file` syntax:
```markdown
See @README.md for project overview and @package.json for available npm commands.

# Git workflow
@docs/git-instructions.md
```

### Useful sections to include
- **Critical Rules** at the top (highest-priority instructions)
- **Workflow triggers** mapping phrases like `"build the app"` to specific scripts
- **Verification commands**: build, test, lint procedures so Claude can self-check
- **Compaction instructions** to preserve critical state across `/compact`
- Use `.claude/rules/` subdirectory to split large instruction sets

---

## 4. Workflow

### Daily development loop
- **Start features in Plan Mode.** Discuss approach before touching code.
- **Commit early and often.** Commit at least hourly when tasks complete. Git is your safety net.
- **Small, focused PRs.** One feature per PR. Easier to review and revert. (~118 lines at p50 is a good target.)
- **Squash merge for clean linear history.**
- **Use `/rewind` (Esc+Esc) liberally.** Every Claude action creates a checkpoint. You can restore conversation, code, or both. This is not a replacement for git, but use it for fast iteration — try risky things, rewind if they fail.

### Session management
- **Name your sessions:** Use `/rename` to give sessions descriptive labels like `"oauth-migration"` so you can find them later.
- **Resume with context:** `claude --continue` or `claude --resume` — don't re-explain what you've already covered.
- **Use `/fork`** (or clone scripts) to branch conversations at a specific point without losing the original thread.

### Parallel workflows
- **Run multiple Claude instances** across terminals or tmux panes for concurrent tasks.
- **Git worktrees for file isolation.** Use when running parallel instances that touch different parts of the codebase simultaneously.
- **Writer/Reviewer pattern.** Session A implements; Session B reviews from a fresh context (no bias toward code it just wrote). Feed review output back to Session A.
- **Fan out for large migrations.** Have Claude list all files, then loop through them calling `claude -p` in a script with `--allowedTools` to restrict permissions.

### Automation and CI
- **Non-interactive mode:** `claude -p "prompt"` for CI pipelines, pre-commit hooks, scripts.
- **Structured output:** `--output-format json` or `--output-format stream-json` for programmatic parsing.
- **Auto mode:** `--permission-mode auto` for unattended runs — a classifier handles approvals in the background.
- **Hooks for deterministic automation:** Unlike CLAUDE.md instructions (advisory), hooks guarantee execution. Use `PreToolUse` to block dangerous commands, `PostToolUse` for auto-formatting. Ask Claude to write hooks for you.

### Extending Claude
- **Skills** (`.claude/skills/<name>/SKILL.md`): reusable workflows invoked with `/skill-name`. Use `disable-model-invocation: true` for workflows with side effects you want to trigger manually.
- **Subagents** (`.claude/agents/<name>.md`): specialized assistants with their own context, tool allowlists, and models. Feature-specific subagents outperform general role personas.
- **MCP servers:** Connect external tools — Notion, Figma, databases, GitHub — via `claude mcp add`.
- **Plugins:** Browse with `/plugin`. Bundles of skills, hooks, subagents, and MCP configs.
- **CLI tools:** Install `gh`, `aws`, `gcloud` etc. Claude uses them natively. Without `gh`, GitHub API calls hit rate limits.

### Verification and debugging
- Invest in verification: tests, linters, scripts, screenshots — the more automated, the better.
- Use the Claude in Chrome extension for UI validation.
- For stuck issues, screenshot and share directly with Claude.
- Use MCPs for visibility: Playwright, Chrome DevTools.
- Use `/doctor` for installation and configuration diagnostics.
- Use ASCII diagrams for architecture discussions.
- Cross-model QA: have one model review another's implementation.

### Common failure patterns to avoid
| Pattern | Fix |
|---------|-----|
| Kitchen sink session (mixing unrelated tasks) | `/clear` between tasks |
| Correcting the same issue repeatedly | After 2 failures, `/clear` and write a better prompt |
| Over-specified CLAUDE.md | Ruthlessly prune; convert over-specific rules to hooks |
| Trust-then-verify gap (shipping unverified output) | Always provide verification criteria |
| Infinite exploration (no scoped investigation) | Scope narrowly or use subagents |

---

## 5. Model Selection

- **Opus for planning and complex reasoning.** Use for intricate architectural decisions, reviewing plans, and anything requiring deep multi-step reasoning. Use `"ultrathink"` keyword to trigger high-effort reasoning.
- **Sonnet for coding.** Faster and more cost-efficient for implementation tasks.
- **Haiku for simple/fast tasks.** Lightweight queries, quick lookups.
- **Switch models with `/model`.** Use the right model for each phase — plan with Opus, implement with Sonnet.
- **Enable thinking mode for decisions.** Useful when you want reasoning exposed before a conclusion.
- **Subagent model overrides.** Define per-agent models in `.claude/agents/<name>.md` — e.g., pin a security-reviewer subagent to `model: opus` regardless of your session model.
- **On compaction errors with large contexts:** switch to a 1M token model before running `/compact`.
