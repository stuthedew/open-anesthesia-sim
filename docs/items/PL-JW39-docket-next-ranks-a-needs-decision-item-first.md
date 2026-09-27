---
id: PL-JW39
title: docket next ranks a needs-decision item first, so every fresh session opens on work whose next step is the owner's answer
priority: P2
effort: S
status: needs-decision
classes: session-cost, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-06
---

**Problem.** `bin/docket next` sorts on band, roadmap placement and feature
progress, and does not consider `status`. So a `needs-decision` item outranks
every `ready` one below it and is offered as the thing to work on now.
Observed 2026-09-06: `PL-6Q8N` (the reference adult's eleven physiologic
parameters have no primary source at all) was moved `ready` to
`needs-decision` because its next step is the project owner's answer, and
`next` went on returning it as suggestion 1 of 3.

The status word is printed in the line - `(M, needs-decision, science-tagged)`
- so a session that reads it carefully is not misled. That is the whole of the
protection, and it sits inside a parenthesis alongside effort and class.

**Why it matters.** `next` is what a fresh session runs first, and its top
answer is the one that gets started. An item whose next step is a decision
cannot be worked by a session at all: the honest outcome is to read the brief,
find the open question and stop, which is a session's opening spent for
nothing. The queue holds 13 P1 items, so the cost is not that there was
nothing else to do.

**Not obviously a bug, which is why this is a question rather than a fix.** A
`needs-decision` item is a question for the project owner, and `bin/docket
gate` counting it is how the question reaches them; suppressing it from `next`
entirely could bury exactly the items that most need attention, and a session
running *with* the owner present can productively work one by answering it.
The defect, if there is one, is the unconditional first place rather than the
inclusion.

**Where.** `subprojects/docket/` - the ranking in the `next` command, and
whatever `docket next`'s output line does to make status legible.

**Done when.** Either `next` stops ranking a `needs-decision` item above
startable work, or it says in its reason line that the item's next step is a
decision rather than code - and the choice between those is recorded.

**Decision needed.** Does `bin/docket next` stop ranking a `needs-decision`
item above startable work, or does it keep the ranking and say in its reason
line that the item's next step is a decision rather than code? Suppressing such
items entirely is the third option and the brief argues against it: `bin/docket
gate` counts them precisely so the question reaches the project owner, and a
session running with the owner present can work one by answering it.

## Design round 2026-09-27: recommendations

**Re-confirmed against the tree, 2026-09-27.** `plan.recommend`'s `rank()`
still orders on hotfix, generator tier, roadmap placement, band, feature
progress, effort and id, and `plan._startable` unseats only `untriaged` and
`blocked`, so a `needs-decision` item holds whatever rank its band gives it.
The line it prints now reads `(S, needs-decision, open design decision - use
your strongest model)`, which is the brief's parenthesis made longer, not a
change to the offer. No `P0` or `P1` item is at `needs-decision` today, which
is the only reason the top three of `bin/docket next` are startable; 42 open
items are, and in `next --limit 5` on 2026-09-27 picks 4 and 5 (`PL-CWD4`,
`PL-B396`) are decisions. The session-start digest's `Top:` line is read from
the same `recommend` call (`render`), so whatever `next` offers first, the
digest opens with.

**What changed since filing, and decides it.** `PL-Q89J` (project owner,
2026-09-22, ratified) built `docket next --oldest` and settled this question
for that mode: a `needs-decision` item "is owed whatever its classes, but its
next step is the owner's answer, not a session's work", so
`plan.longest_waiting` lists them on a separate line, oldest first, and never
ranks them - citing this item as "the same hazard in `next` itself". Bare
`next` was left byte-identical as scope discipline for that item, not as a
finding that ranking them is right, and `cli._say_decisions` already prints
the line. The Projects trial now routes every `needs-decision` item to a
design thread before any code (project instructions, "Design first"), so a
`next` that offers one as a pick hands a code session the one kind of item
the workflow says a code session may not start;
`.claude/skills/docket/modes/triage.md` records the same trap under
`PL-4T90` ("the status looks like an invitation and `bin/docket next` ranks
it").

**Q1. Stop ranking, or keep the rank and say so in the reason line?**
**Recommendation: stop ranking, and name them apart - the `--oldest` shape,
applied to `next` itself.** `recommend` drops a `needs-decision` item from the
ranked picks unless it is `P0` (the floor `longest_waiting` already keeps: a
hotfix tops the list whatever its status), and `next` prints
`_say_decisions`'s line beneath the picks - oldest first, cut to `--limit`
with the rest counted, "not ranked above" with the reason. The digest's
`Top:` line follows without a change of its own. Nothing is suppressed, which
is the brief's objection to the third option and this round's: the ids stay
in the same block of output, `bin/docket gate` and `wave` go on counting
them, and a session sitting with the owner reads them one line lower. What
is given up is band order among the decisions themselves - age instead of
band - and `P0` is exempt, so nothing a hotfix needs is lost.

*Refused: keep the rank and say in the reason line that the next step is a
decision.* The cheaper edit, and it fixes legibility rather than the offer.
The brief's own hazard is that "an item whose next step is a decision cannot
be worked by a session at all", and a sentence under pick 1 leaves pick 1,
the digest's `Top:` and every fresh session's first line pointing at work no
code session may start. The parenthesis already says it; a longer sentence
in the same place is the mechanism the brief measured as not protecting.

**How, for the build thread.** Hoist `longest_waiting`'s local `deciding()`
predicate to module level in `subprojects/docket/src/docket/plan.py`, so
`recommend`, `longest_waiting` and `set_aside` read one rule: `set_aside`
counts what a lane dropped from `_startable`'s population, and a decision
named on its own line must not also be counted as set aside, or the lane
footer and the decisions line stop summing to the startable set. `cmd_next`
in `cli.py` computes the lane-narrowed decisions the way `_next_oldest` does
and calls `_say_decisions` after the picks. Tests in
`subprojects/docket/tests/test_plan.py` (a `P1` at `needs-decision` is absent
from `recommend`'s picks and a `P0` is not; the order of `ready` items is
unchanged) and `subprojects/docket/tests/test_cli.py` (the line prints under
bare `next`, cut to `--limit`; the digest's `Top:` never names a
`needs-decision` item). Three sentences of documentation become history and
move with it: `subprojects/docket/README.md`'s "Decisions apart" bullet,
which scopes the line to `--oldest`; `.claude/skills/docket/modes/picking.md`'s
`--oldest` sentence; and `modes/triage.md`'s "`bin/docket next` ranks it".
`touches:` grows by `plan.py`, `tests/test_plan.py`, the README and the two
mode files when the build thread claims it; `S` holds.

**What this settles beside it.** `PL-4ZK8` (should `bin/docket concurrent`'s
batch hide `needs-decision` and in-flight items, or mark them the way `[IN
FLIGHT]` does) is the same question about a different command, and its
answer should follow this one: named, and never offered as startable.
