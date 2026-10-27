---
id: PL-8Z38
title: Report to Anthropic that Projects threads on Claude Code 2.1.310 no longer read the repository's .claude/ directory (no project hooks, skills or permission rules), with PL-CR81's Cause paragraph as the evidence
priority: P1
effort: S
status: dropped
classes: infra
feature: projects-trial
touches: docs/items/PL-8Z38-report-to-anthropic-that-projects-threads-on.md, docs/items/PL-CR81-projects-threads-in-the-v0-7-0-project-run.md
added: 2026-10-25
closed: 2026-10-27
reason: Not a fault, so no report is owed. Claude Code's Projects documentation, § 'What threads pick up from your repositories' (https://code.claude.com/docs/en/claude-projects.md, re-read with curl on 2026-10-27), says cloud threads load CLAUDE.md and .claude/rules/ but not .claude/skills/, .mcp.json or .claude/settings.json, so hooks are 'Not run' and permission rules 'Not applied'. That is exactly the 2.1.310 behaviour PL-CR81 measured. PL-X6VN's setup script is the stop-gap that gives threads the hooks.
payoff: the product fault behind PL-CR81 reaches the people who can fix it
verify: grep -qE '^\*\*Reported' docs/items/PL-8Z38-*.md
not-delegable: the report goes from the project owner's account, which no session or worker can use
---

**Problem.** Report to Anthropic that Projects threads on Claude Code 2.1.310 no longer read the repository's .claude/ directory (no project hooks, skills or permission rules), with PL-CR81's Cause paragraph as the evidence

**Reproduced 2026-10-26.** `PL-CR81`'s `**Cause.**` paragraph records that a
thread on Claude Code 2.1.310 listed none of the repository's four skills and
fired no hook. It also records that the thread ran inside the checkout, and
that an earlier thread on 2.1.283 had loaded them. The brief names no report
sent anywhere.

**Why it matters.** No change in this repository can fix `PL-CR81`. Until the
product is fixed, every Projects thread runs without the guards and skills.
The report is the only route to a fix.

**Done when.** The project owner has sent the report, for example through
Claude Code's `/feedback` command or as an issue on Anthropic's Claude Code
repository. This brief then carries a paragraph headed "Reported", in bold,
with the date and a link or reference. A session cannot send it, because it
goes from the owner's account.

**Generator check.** One external behaviour that nothing in the repository
models, the same one `PL-CR81` records. It is a one-off.
