---
id: PL-ZKT8
title: Run Claude Code's /claude-api prompt-audit over the resident instructions and the docket skill against Opus 5.5, and bring its proposed diff to the owner hunk by hunk
priority: P2
effort: M
status: ready
classes: session-cost
feature: model-evidence
touches: CLAUDE.md, .claude/rules, .claude/skills/docket
added: 2026-10-17
payoff: instructions written for older models stop costing tool rounds and accuracy on Opus 5.5, with every change approved by the owner
verify: grep -q '^## Audit result' docs/items/PL-ZKT8-run-claude-code-s-claude-api-prompt-audit-over.md
---

**Problem.** Run Claude Code's /claude-api prompt-audit over the resident instructions and the docket skill against Opus 5.5, and bring its proposed diff to the owner hunk by hunk

**Why it matters.** Anthropic's "Optimizing for cost and intelligence" page
says to audit prompts "against the model you run now, and again whenever you
change models"
(https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence,
§ "Audit prompts against the current model"). The owner moved this project's
hard work to Opus 5.5 on 2026-10-14. The page measured two kinds of stale
text. A newer model follows over-instruction such as "verify twice" or a
mandatory step-by-step procedure too literally, which adds tool rounds and
cost. Contradictions and retired settings cost accuracy. "The same patterns
tend to appear in tool descriptions and skills."

The resident set (`CLAUDE.md` and the three unscoped rules) measured 84,789
characters on 2026-10-17. Cached reads of it cost little, so the payoff is in
behaviour rather than size. The installed Claude Code (2.1.302) carries
`prompt-audit [<path>]`. The owner agreed to run it on 2026-10-17 (ratified,
in session_016Hv97dHUS9f4zXzkt2bU2E).

**How.** Run it in a fresh session from the repository root, over `CLAUDE.md`,
`.claude/rules/` and `.claude/skills/docket/`. Bring the proposed diff to the
owner hunk by hunk, with what the audit left alone. Many of these rules are
ones the owner specified, so a hunk that changes one needs a compelling
argument, and the session says so beside it. Apply only the hunks the owner
approves, each routed by `CLAUDE.md`'s rule for behaviour changes.

**Done when.** The audit's findings and the owner's answer to each are
recorded below under `## Audit result`, and the approved hunks are merged.

**Generator check.** Not a member of a head: one audit, prompted by one model change.
