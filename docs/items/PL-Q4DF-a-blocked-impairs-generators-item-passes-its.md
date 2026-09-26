---
id: PL-Q4DF
title: A blocked impairs-generators item passes its rank to nothing and nothing names it: generator_blockers lifts only a root-cause head's blockers, so a machinery defect waiting on another item drops off the generator tier silently
priority: P2
effort: M
status: done
classes: defect
feature: generator-identification
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/README.md, subprojects/docket/tests/test_plan.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; recorded as a generator head by the 2026-09-25 triage pass
added: 2026-09-24
closed: 2026-09-26
payoff: A generator or machinery defect that cannot start yet is either ranked through the work it waits on or named as unranked, and no command calls an item ranked while next is not offering it
verify: grep -q 'def test_a_blocked_impairs_generators_item' subprojects/docket/tests/test_plan.py && grep -q 'def test_an_untriaged_generator_tier_item' subprojects/docket/tests/test_cli.py
root-cause-of: PL-BBT8, PL-QFWF, PL-4RK2
generator: spent - every reader now takes where a tier item's rank stands from plan.tier_standings, so a status no reader handled reaches all of them at once instead of one per fix
misread: Whether a generator-tier item holds its rank now, passes it to its blockers, or ranks nowhere
impairs-generators: plan.generator_blockers and plan.unranked_generators ask only ranks_as_generator, so a blocked impairs-generators item's rank reaches nothing and nothing names it; render._outside_clusters, render._verdict_phrase and cmd_show's placement line call an untriaged or blocked tier item ranked
---

**Problem.** A blocked impairs-generators item passes its rank to nothing and nothing names it: generator_blockers lifts only a root-cause head's blockers, so a machinery defect waiting on another item drops off the generator tier silently

Found 2026-09-24 while fixing `PL-4RK2` (a blocked live generator head's rank
is lost or misstated). `plan.generator_blockers` hands a blocked item's tier
rank to its open blockers only when the item is a root-cause head
(`ranks_as_generator`). The tier's other entrance, a sound
`impairs-generators:`, gets no such pass. A machinery defect at `blocked`
therefore ranks nothing, its blockers rank on their bands, and
`plan.unranked_generators` does not name it either, because it reads heads
alone. `PL-4RK2` fixed only what `docket show` says about it: the line now
reads "blocked, so ranked nowhere until it can start" instead of "ranked on the
generator tier".
`docket generators` still says it ranks: `render._outside_clusters` counts every
open sound `impairs-generators:` item as "ranks on the generator tier", printing
`(blocked)` beside the id in the same sentence.

**Not a refiling of `PL-4RK2`.** `docket new` matched this capture to that item
on shared paths. It is the sibling entrance to the tier, with a decision of its
own to make: whether `CLAUDE.md`'s "ranks with one" for a machinery defect
reaches the work it waits on. `PL-QFWF` made that call for heads only. So the
match is withdrawn on `PL-4RK2` with this item as the reason.

Reproduced 2026-09-25 against 46954a81, with two synthetic items and no store
edit (scratch script, standard library plus `subprojects/docket/src`). Item A
is `blocked` by B, carries a sound `impairs-generators:`, and declares `plan.py`
in `touches`. Item B is `ready` at `P3`. Results:

- `plan.generator_blockers` returns `{}`, and `plan.unranked_generators`
  returns `[]`.
- `plan.recommend` offers B as "Highest-priority work that is ready to start
  (P3)", with no generator reason.
- `render._outside_clusters` prints "1 item ranks on the generator tier by
  `impairs-generators:` ... PL-AAAA (blocked)".

**The same reading is live today, for untriaged items.** `_startable` excludes
untriaged items, and `generator_blockers`' docstring says an untriaged head
"has not been seated to hold any" rank. Even so, the live store shows:

- `bin/docket show` prints "it ranks above every band but P0" for `PL-GPJ7`,
  `PL-XBV4` and `PL-PVW2`, three untriaged live heads, and for `PL-6P0F`, an
  untriaged `impairs-generators:` item. `bin/docket next` offers none of the
  four.
- `bin/docket generators` says the three heads are "still generating, so on
  the tier", and says `PL-6P0F` "ranks on the generator tier".

`placement_line`'s docstring records how this happened: `closed` was added
for `PL-BBT8` and `blocked` for `PL-4RK2`, one status per fix, and nothing
handles `untriaged`.

**Why it matters.** The generator tier is the one rank above a
`safety`-classed `P1`, and `CLAUDE.md` puts a machinery defect on it "because
while identification is broken a generator is never recorded". A blocked
machinery defect currently passes that rank to nothing and nothing names it.
Meanwhile two commands tell a session that items `next` is not offering are
ranked, so the reader believes a generator is being paid down when nothing
ranks it. That is a confident wrong answer about what the queue is doing.

**Generator check.** This item is the head of a new generator, recorded here
at triage. The fact is whether a generator-tier item holds its rank now,
passes it to its blockers, or ranks nowhere, and no head's `misread:` states
it. Three closed items misread that fact, each in a different reader or for a
different status:

- `PL-BBT8`: `show` called a closed head ranked.
- `PL-QFWF`: `next` dropped a blocked head's rank.
- `PL-4RK2`: a chain or milestone lost a blocked head's rank, and `show`
  called the blocked head ranked.

This item is the fourth. The untriaged case above is the fifth reading of the
same fact, and it is recorded here rather than as an item, because this head's
fix covers it. `PL-6T44`'s fact ("an item's current queue state") is a
different one: these readers knew the status, and printed it beside the id.
What they misread is what the tier does with that status.

Recording this head surfaced one more wrong line in the same function. Once
this item carried both fields, `docket generators` printed it under "items
rank on the generator tier by `impairs-generators:` and name no members",
although its `root-cause-of:` names three. `render._outside_clusters` never
asks whether an `impairs-generators:` item is also a head. Fix it with the
rest, since the function is already in this item's work.

**Done when.** One function in `plan.py` says where a generator-tier item's
rank stands. It covers both entrances (`ranks_as_generator` and
`ranks_as_generator_defect`) and every open status, `untriaged` included. The
answer is one of: held; passed to its open blockers; named as unranked; or
nowhere. `recommend`, `generator_blockers`, `unranked_generators`, `cmd_show`'s
placement line, `render._verdict_phrase` and `render._outside_clusters` all
read that answer instead of testing status themselves. A blocked
`impairs-generators:` item then either passes its rank to its open blockers or
is named by `docket next` the way `unranked_generators` names a head. Which of
the two is recorded in this brief when the work is done.

**Recommendation:** pass the rank one edge down, as `PL-QFWF` does for heads,
and let `unranked_generators` name the deeper shapes. `CLAUDE.md` gives the
tier's second entrance the "Same tier". `PL-QFWF`'s argument for heads also
holds word for word: "the rank is the head's, and it passes to what the head
waits on, since that is the work paying the generator down now". Neither
`PL-QFWF` nor `PL-4RK2` records the heads-only scope as an owner decision, so
this is a session's call, not the owner's.

**Built, 2026-09-26: the rank passes one edge down, as recommended.**
`plan.tier_standings` is the one function. It reads both entrances and every
open status, and answers `HELD` (it can start), `PASSED` (blocked, with the open
blockers the store holds), `UNRANKED` (blocked on nothing the store holds open),
or `NOWHERE` (untriaged). A blocker handed a rank while it is itself untriaged
or blocked also stands `NOWHERE`, because the rank goes no further.
`generator_blockers` and `unranked_generators` read it, and so do `recommend`,
`longest_waiting`, `cmd_show`'s plan and tier lines, `render._verdict_phrase` and
`render._outside_clusters`. `_unseated_by` is the one status test, and
`_startable` shares it, so what `next` offers and what the tier says is ranked
cannot disagree. A blocked machinery defect now lifts its blockers, and
`unranked_generators` names it where nothing offered carries it, marked as a
defect rather than given a member count. `_outside_clusters` leaves out a
defect that is also a head. The marks read "unblocks X on the generator tier",
because the item unblocked may be a defect rather than a generator.

The untriaged case is pinned with synthetic items in `test_plan.py` and
`test_cli.py`. The four live examples above were triaged to `ready` before the
work began, so the store no longer shows it.
