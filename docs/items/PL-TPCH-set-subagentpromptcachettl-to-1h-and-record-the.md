---
id: PL-TPCH
title: Set subagentPromptCacheTtl to 1h and record the effort-per-standard decision in the two carriers that can act on it
priority: P2
effort: S
status: done
classes: session-cost
feature: owner-decisions-2026-09-19
milestone: v0.4.29
touches: .claude/settings.json, docs/maintainer.md, .claude/rules/apparatus-standard.md
added: 2026-09-19
closed: 2026-09-19
verify: grep -qF '"subagentPromptCacheTtl": "1h"' .claude/settings.json && grep -qF 'Match effort to the standard the work is held to' docs/maintainer.md && grep -qF 'Effort follows this standard too' .claude/rules/apparatus-standard.md
---

**Problem.** Two cost levers were unset, and neither had a carrier.

**The cache TTL.** On a Max subscription the main conversation defaults to a
1-hour prompt cache but subagents, workflows and background tasks default to 5
minutes, and `subagentPromptCacheTtl` was not set anywhere — no
`.claude/settings.local.json`, no user-level settings file. `CLAUDE.md` tells
every session to delegate broad codebase search to exploration subagents, so
this is the project's own hot path. A subagent whose turns fall more than five
minutes apart — routine when several queue behind the concurrency cap, or when
one runs a slow command — re-pays its whole prefix at full input price instead of
the 0.1x cache-read rate.

Not free, and the trade is recorded rather than assumed: a 1-hour cache write
costs 2x base input against 1.25x for 5 minutes, and pays back after two cache
reads. The subagents this project runs make tens of tool calls each, so they
clear that many times over. Worth stating that the docs do **not** say whether
cache tokens count toward the five-hour usage window at full weight or at the
discounted rate, so the size of the win is unestablished; its direction is not.

**Effort.** Every one of seven concurrent sessions on 2026-09-19 ran at
`max`, including one whose whole task was renaming seven item files. Claude
Code's documented default is `high`. Lower effort produces fewer and more
consolidated tool calls, so it cuts the turn count as well as the output tokens,
and since every turn re-reads the whole conversation those multiply.

**Why it needed two carriers rather than one.** A session cannot change its own
effort level — there is no tool for it — so half of this is only ever the
owner's, and a rule a session cannot act on still costs every session the context
to read it. That half is in `docs/maintainer.md`, which exists for exactly that.
The half a session *can* act on is the effort of the subagents and workflow
agents it spawns, and that went in `.claude/rules/apparatus-standard.md`, which
is path-scoped to the apparatus and so loads only when a session is doing the
work it governs. Net resident growth: zero.

**Done when.** `subagentPromptCacheTtl` is `1h` in `.claude/settings.json`; the
effort split is recorded as `(project owner, 2026-09-19, ratified)` naming what
it was chosen over in both carriers; and neither addition touched the resident
set.
