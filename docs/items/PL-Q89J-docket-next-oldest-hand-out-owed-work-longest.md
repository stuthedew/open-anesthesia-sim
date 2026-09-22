---
id: PL-Q89J
title: docket next --oldest: hand out owed work longest-waiting first, so low-priority items that newer work keeps outranking stop starving
priority: P2
effort: M
status: ready
classes: infra
feature: debt-aging
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/config.py, subprojects/docket/README.md, subprojects/docket/tests/test_plan.py, subprojects/docket/tests/test_cli.py, .claude/skills/docket/SKILL.md, .claude/skills/docket/modes/picking.md, docket.toml
added: 2026-09-22
payoff: an owed item that newer, higher-ranked work keeps outranking surfaces on request, instead of waiting until nobody remembers why it was filed
verify: grep -q 'def test_oldest_hands_out_the_longest_waiting_owed_work_first' subprojects/docket/tests/test_plan.py
---

**Problem.** `docket next` ranks by the plan: `P0`, then a live generator, then
what the current step places (today, Gate 2's frozen list), then band, then
feature progress. Every term favours work that is newer, more urgent or more
central, so an owed item that is none of those waits indefinitely while newer
work keeps arriving above it. That is *starvation*, and nothing in docket
surfaces it.

Measured 2026-09-22 against `origin/main` at `c128173a` (the store, not git
history; every open item carries a required `added:` date):

- 280 of the 292 startable items are owed work. Only 12 are classed `feature`
  or `planning`, because feature intent lives in `ROADMAP.md`, not the queue.
- 138 of the 280 are on Gate 2 and are handed out first. The other 142 sit on
  no gate, mostly classed `docs`, `infra`, `test`, `ux`; 50 are over 14 days
  old. No gate will ever hold them, because `plan.is_debt` counts only
  `debt_classes` and `needs-decision`.
- The five oldest open items were added 2026-08-24, the project's first week.
  `docket next` ranks them 143rd to 217th of 292. It reaches none of them
  before Gate 2 clears, and after that v0.6.0's own `Required scope` comes
  first.
- `PL-027` (confirm the slider write-back on a live Flet client) is one of
  them. Its own brief has said since 2026-09-10 that the Qt port may have
  mooted it, and it is still open.

Class-listed debt is not the at-risk set: no item `plan.is_debt` accepts is
older than three days without being on the gate.

**Why it matters.** The project owner's definition (2026-09-22): debt is what
we marked as needing cleanup, that is not pressing, so we moved on, and so it
is at risk of being forgotten as new work keeps accumulating. They asked for a
way to pick that work: "what is next debt". `ROADMAP.md` § "The debt gate"
states the cost: "Deferred debt is not kept; it is paid for twice or silently
dropped." The gate protects the class-listed half. This item protects the
rest.

**Design (project owner, 2026-09-22, ratified - chosen over a `--debt` filter
on the roadmap's class list in the plan's order, which would have returned
exactly what `docket next` returns today).**

- **Order: longest-waiting first, by `added:`.** This is *aging*, the standard
  remedy for starvation in priority scheduling. Pure age order is its extreme
  form, and the simplest to audit. `P0` stays on top: a hotfix never waits
  behind an old doc fix. Ties go by band, then id. Age is `--today` minus
  `added`, so no git read is needed, a bare checkout answers, and tests pin
  the date.
- **Population: startable owed work.** Take `plan._startable`'s set (open,
  triaged, not `blocked`, not in flight) and drop every item classed in a new
  `new_work_classes` setting, defaulting to `feature` and `planning`. That is
  `ROADMAP.md` § "What counts"'s "An item classed `feature` or `planning` is
  **not** debt". A `needs-decision` item is owed whatever its classes, but
  its next step is the owner's answer, not a session's work. So list those
  on a separate line, oldest first, rather than ranking them. Otherwise one
  unanswered decision would hold the top of the list forever (`PL-JW39` is
  the same hazard in `next` itself).
- **The flag is `--oldest`, not `--debt`.** `docket gate` and the roadmap
  already use "debt" for the narrower class list the gate holds. Reusing the
  word for the wider set would make two commands disagree about what debt
  is. The skill maps "what is next debt" to this flag.
- **It filters and reorders only under the flag.** `docket next` without it
  is unchanged. It composes with the lane argument and `--effort` (`docket
  next product --oldest --effort S`), the lane filtering first, as `recommend`
  already does.
- **Output.** Each pick uses `Recommendation.describe()`, plus its age
  ("added 2026-08-24, 29 days waiting") and the placement sentence that
  `recommend` already writes, so an off-gate pick says so. The last line names
  the plan's own pick: "The plan's own pick is PL-XXXX (P2, on the debt gate):
  `docket next`." That mirrors the lane footer in `_say_answer_lane`, so a
  session is never handed off-gate work silently (`picking.md`: "Recommending
  off-gate work is allowed, and is never silent about being off-gate").

**Done when.** `docket next --oldest` prints the longest-waiting startable owed
items with their ages, `P0` first. `needs-decision` items are listed apart.
`feature`/`planning` items and in-flight work are excluded. The plan's own
pick is named last. It composes with a lane and `--effort`, and bare `docket
next` output is byte-identical to before. The README's "What it does" block
and a short section beside "Choosing is answered, not browsed" say what it is
for. `.claude/skills/docket/SKILL.md`'s picking row and `modes/picking.md`
route "what is next debt" and "what have we forgotten" to it. Tests cover:
age order; the `P0` floor; exclusion of new work and in-flight items; the
separate `needs-decision` line; lane composition; unchanged plain `next`.
