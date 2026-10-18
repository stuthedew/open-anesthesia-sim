---
id: PL-MR2V
title: CLAUDE.md's ideation mode must stay cheap with no detours, but rule 14 runs a refresh before every reply's closing block; decide whether an ideation reply is exempt (PL-ZKT8 audit flag B11)
priority: P3
effort: S
status: done
classes: docs
feature: decision-ownership
milestone: v0.5.28
touches: .claude/rules/instruction-writing.md
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-10-18
closed: 2026-10-18
pr: 1545
payoff: an ideation reply still refreshes before its closing block, so cheap ideation never repeats a stale state
verify: grep -qF 'An ideation reply runs it too' .claude/rules/instruction-writing.md
---

**Problem.** CLAUDE.md's ideation mode must stay cheap with no detours, but rule 14 runs a refresh before every reply's closing block; decide whether an ideation reply is exempt (PL-ZKT8 audit flag B11)

**Why it matters.** `CLAUDE.md` says ideation must stay cheap and read nothing
new, and rule 14 of `.claude/rules/instruction-writing.md` runs `bin/docket
flight` and `bin/docket stranded` before every closing block. A session in
ideation mode can read either one as overriding the other. The `PL-ZKT8`
prompt audit flagged it as B11 and left it for a decision.

**Decided 2026-10-18** (a session's call under rule 14: keeping the rule the
owner specified is the only option that does not reopen it). An ideation reply
is not exempt. The refresh is the owner's specified rule (2026-09-19, "every
time"), so exempting ideation would reopen it, which needs a compelling
argument and the owner's word. None exists here: the two commands cost a few
hundred tokens and read no document, and ideation's "read nothing" is about
documents and detours. So the fix says so in the refresh bullet, and changes
no behavior.

**Done when.** Rule 14's refresh bullet says an ideation reply runs it too, and
why that is not a detour.
