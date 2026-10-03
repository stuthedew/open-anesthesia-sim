---
id: PL-4ZK8
title: bin/docket concurrent offers a batch containing needs-decision and in-flight items, so a fan-out cannot hand it out as-is
priority: P2
effort: S
status: done
classes: defect
feature: parallel-sessions
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/plan.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, .claude/skills/docket/modes/picking.md, docs/items/PL-7B3G-bin-docket-concurrent-ranks-its-batch-by.md
added: 2026-09-07
closed: 2026-10-03
pr: 1299
payoff: a fan-out can paste the bare batch as it stands, and docket next and docket concurrent offer one startable population
verify: grep -q 'def test_concurrent_batch_offers_only_startable_work' subprojects/docket/tests/test_cli.py && grep -q 'def test_concurrent_names_the_decisions_and_in_flight_work_beneath_the_batch' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket concurrent offers a batch containing needs-decision and in-flight items, so a fan-out cannot hand it out as-is

**What was observed.** A bare `bin/docket concurrent` on 2026-09-07 returned
"A batch that can be worked at once (32 items, best-first)". Of those 32,
`PL-483K` was in flight (marked `[IN FLIGHT]` in the line, so that half is
visible) and at least seven were at `status: needs-decision` — `PL-DXQC`,
`PL-B32L`, `PL-WGXJ`, `PL-JW39`, `PL-KFWL`, `PL-KRS6`, `PL-H1JD` — with
nothing in the batch line saying so.

**Why it matters.** "Can be worked at once" is read as "can be started at
once", and a needs-decision item cannot be started: its next step is the
project owner's answer, which is the same wrong answer `PL-JW39` records
against `docket next`. The consequence lands hardest on the case the command
is best for — a session picking several items to hand to several sessions —
because there the wrong pick is not one session's detour but N of them, and
the batch is exactly what a fan-out would paste. Whether a batch should hide
such items or mark them is the decision: `[IN FLIGHT]` is already the marking
precedent, and hiding would make the count disagree with `docket list`.

**Found while** picking four gate entries to spin up as parallel sessions on
2026-09-07 — the batch could not be used as the answer, so the four were
chosen by reading the 95 open gate entries' front matter by hand.
**Done when.** `bin/docket concurrent`'s bare batch offers only the population
`next` ranks - open, triaged, not `blocked`, not in flight, and not at
`needs-decision` below `P0` - and names the in-flight ids and the decisions
beneath it on the two lines `next` already prints; the choice and its `PL-JW39`
reason are in the command's docstring; and the two tests `verify:` names pin
it. `PL-7B3G` is sequenced behind this, and is re-triaged once this lands,
because the startable axis it planned is built here and gate membership is the
axis that remains. Rewritten 2026-09-30 from the either/or the 2026-09-27
answer settled; Q1 under § "Design round 2026-09-27: recommendations" keeps
both endings and the cost each carried.

**Decision needed.** Should `bin/docket concurrent`'s batch hide `needs-decision` and in-flight items, or mark them the way `[IN FLIGHT]` already marks one?

## Design round 2026-09-27: recommendations

**Re-confirmed against the tree, 2026-09-27.** `cli.cmd_concurrent` still
builds the bare batch from `report.open_items` sorted by `sort_key()`, and
reads no status at all: `concurrency.parallel_batch` drops only an item with
no `touches` and one contending with a pick already made. Measured at 19:54
UTC, the bare batch offered 51 items, and 8 of them cannot be started: 5 at
`needs-decision` (`PL-4ZK8` itself, `PL-6QZP`, `PL-VJFQ`, `PL-QV5Y`,
`PL-TDBT`), 2 `blocked` (`PL-5XG1`, on `PL-V1Y7`; `PL-L8RN`, on `PL-W9P6`) and
1 in flight (`PL-G8TR`, the one row marked). A blocked item reaches the batch
whenever its blocker is not among the picks already made, because the
ordering edge is read only against those. Untriaged items are absent by
accident rather than by rule: none of the 13 declares `touches`. So the
brief's defect stands, wider than filed - the batch has no notion of
startable - and `[IN FLIGHT]` is the only status the line carries.

**What changed since filing, and decides it.** `PL-JW39` (project owner,
2026-09-27, ratified, over keeping the rank and saying so in the reason line)
answered this question for `bin/docket next` this morning: a `needs-decision`
item below `P0` is never offered as a pick, and is named apart beneath the
picks on `_say_decisions`'s line, from the one predicate
`plan.awaits_decision`. Its design round wrote that this item "is the same
question about a different command, and its answer should follow this one:
named, and never offered as startable" (`PL-JW39` § "Design round
2026-09-27: recommendations"). `next` has left in-flight work out of its
picks and named it on `render.format_excluded`'s line ("Excluded, already in
flight: ...") for longer still. The bare batch is the one surface that still
says "can be worked at once" about work no session may start, and it is the
surface a fan-out pastes.

**Q1. Hide `needs-decision` and in-flight items from the batch, or mark them
the way `[IN FLIGHT]` marks one?**
**Recommendation: hide them from the batch and name them beneath it - the
shape `PL-JW39` ratified for `next`, so the two commands offer one
population.** The bare batch draws its candidates from what `plan.recommend`
ranks: open, triaged, not `blocked`, not in flight, and not waiting on the
owner unless `P0` (`plan._startable` with `plan.awaits_decision` removed).
Beneath the batch, the two lines `next` already prints: `render.format_excluded`
for the in-flight ids, each with its hold, and `_say_decisions` with
`NAMED_NOT_OFFERED` for the decisions, oldest first. Nothing is suppressed:
every id the batch drops is in the same block of output, one line lower, and
`bin/docket list`, `gate` and `wave` count them as they did. The cost the
brief priced against hiding - a batch count that disagrees with `list` - was
paid the day the batch became an independent set: 51 of 307 open items were
in it today, and `sequenceable`'s footer already names the 237 a shared file
kept out. Blocked items leave with the others and get no line, as under
`next`: their next step is named by their own `blocked-by`, and a line for
them would be a mechanism `next` has never needed.

*Refused: mark them, the way `[IN FLIGHT]` marks one.* The cheaper edit, and
it fixes legibility rather than the offer. Today's batch would carry eight
marked rows in 51 for a fan-out to filter out by hand, which is the cost the
Done-when names against marking; and `PL-JW39`'s round measured the same
mechanism on `next` - the status already printed in the pick's parenthesis -
as the one that was not protecting, which is why the owner ratified stopping
the offer over saying more in the same place. `[IN FLIGHT]` was the smallest
fix before `next` had `format_excluded`; the precedent is now `next`'s.

*Refused: hide them and say nothing.* The brief's objection holds: the ids
would vanish from the one command a fan-out reads, and a session sitting with
the owner would lose the decisions it could answer. Naming them beneath costs
two lines and reuses two functions.

**Unchanged.** The `concurrent <id>` form's "No declared overlap" list keeps
its `[IN FLIGHT]` flag. There the question is what stands between one item
and each other open item, and a free item that already has a branch is that
answer's most useful row rather than an offer.

**How, for the build thread.** In `subprojects/docket/src/docket/cli.py`,
`cmd_concurrent`'s bare form filters `candidates` through the startable
population and `plan.awaits_decision` before `parallel_batch` - through a
public name in `subprojects/docket/src/docket/plan.py`, since `_startable` is
module-private - then prints `render.format_excluded(flight.ids,
_holdings(args))` where `flight.ids` is non-empty, and
`_say_decisions(plan.awaiting_decision(items, flight.ids), today, limit,
NAMED_NOT_OFFERED)` after the batch's own footer, with `limit` the `--limit`
given or `next`'s default of 3, sharing `cmd_next`'s calls rather than new
strings. The docstring records the choice and the `PL-JW39` reason. Tests in
`subprojects/docket/tests/test_cli.py`: a `needs-decision` item, a `blocked`
item and an in-flight item are absent from the bare batch; the in-flight and
decision ids print beneath it; a `P0` at `needs-decision` stays in; the
`<id>` form's flag is unchanged. Docs: one sentence each in
`subprojects/docket/README.md` § "Concurrency is computed, and honestly
qualified" and `.claude/skills/docket/modes/picking.md`'s `docket concurrent`
block, saying the batch offers startable work only and names the rest beneath
it. `touches:` narrows from `subprojects/docket` to `cli.py`, `plan.py`,
`tests/test_cli.py`, the README and `picking.md` when the build thread claims
it; `S` holds. The fix is a defect in what exists, so `CLAUDE.md`'s generator
pause does not bind it, and at 19:56 UTC `bin/docket generators` marked no
head still generating in any case.

**What this settles beside it.** `PL-7B3G` (`concurrent` cannot be asked for
N startable gate entries that do not collide) is answered by filtering, so by
its own triage note the startable axis is built here and gate membership is
the axis that remains; its re-triage belongs to whoever takes it, after this
lands. Which copy of each item the batch reads - the working tree's, where
`next` reads `origin/main`'s - is `PL-KS01`'s open question, and this
recommendation takes no side on it: it fixes the population, not the copy.

## Answers 2026-09-27

**Answered 2026-09-27: Q1 ratified** (project owner, 2026-09-27, ratified,
over marking `needs-decision` and in-flight items in the batch the way
`[IN FLIGHT]` marks one). `bin/docket concurrent`'s bare batch offers only
the population `next` ranks, and names the in-flight ids and the decisions
beneath it, as § "Design round 2026-09-27: recommendations" specifies. The
thread that builds it sets this item's status and `touches:`.

## Re-confirmed 2026-09-30

**The defect stands, unbuilt, and the item moves to `ready`.**
`cli.cmd_concurrent` still draws the bare batch from `report.open_items`
sorted by `sort_key()` and reads no status; `concurrency.parallel_batch` still
drops only an item with no `touches` and one contending with a pick already
made. Measured at 20:23 UTC on the working tree: the bare batch offered 55
items, and 8 of them cannot be started - 7 at `needs-decision` (`PL-4ZK8`
itself, `PL-08CR`, `PL-3YRT`, `PL-6QZP`, `PL-QV5Y`, `PL-TDBT`, `PL-VJFQ`) and 1
`blocked` (`PL-L8RN`, on `PL-W9P6`) - with `PL-VJFQ` also in flight under a
live claim and marked `[IN FLIGHT]`, the one status the line carries. No test
asserts the mark on a bare-batch row or a `needs-decision` item's presence in
the batch - `test_concurrent_never_certifies_a_pair_as_safe` and
`test_concurrent_refuses_a_limit_below_one` read the footer and the count - so
the build removes no assertion and owes no `falsifies:`.

**Why the status moves here rather than with the build.** The answer was
ratified on 2026-09-27 and is recorded above, but the front matter still read
`needs-decision`, so on 2026-09-30 `bin/docket next` and `next workflow` both
named `PL-4ZK8` first on their "Waiting on a decision" line, 23 days waiting -
a question the owner had answered three days before, which is this item's own
defect turned on itself. Every other item answered on 2026-09-27 moved with
its answer (seven to `blocked`, four closed); this was the one answered item
still carrying the status. At `ready` the `verify:` names the two tests the
build adds, both absent from `subprojects/docket/tests/test_cli.py` today, and
`bin/docket set --verify` ran the command and saw it fail. `touches:` is the
build thread's to narrow, as § "How, for the build thread" says, and is not
narrowed here. The Done-when above was rewritten in the decided form at the
same time.

**Every name § "How, for the build thread" cites still exists as cited.**
`plan._startable` is still module-private, and `plan.awaits_decision`,
`plan.awaiting_decision`, `render.format_excluded`, `cli._say_decisions`,
`cli.NAMED_NOT_OFFERED` and `cli._holdings` carry the signatures the section
calls them with; `next --limit` still defaults to 3 and `concurrent --limit`
to none; `subprojects/docket/README.md` § "Concurrency is computed, and
honestly qualified" and `.claude/skills/docket/modes/picking.md`'s `docket
concurrent` block are still where the one sentence each goes. `PL-JW39` is
`done` (#1171) and `PL-Y1LD` is `done` (#1202, the design round's own pull
request); `PL-7B3G` is still `blocked` on this item; `PL-KS01` is still open.
No open item carries `generator: live` - `PL-MT3R`, the last head, closed on
2026-09-26 - so `CLAUDE.md`'s pause is not in force, and the fix is a defect in
what exists in any case.
