---
id: PL-BBT8
title: bin/docket show reports a dropped head marked generator: live as ranked on the generator tier, because cli.cmd_show skips the status test render._verdict_phrase applies (PL-LN69)
priority: P2
effort: S
status: done
classes: defect
feature: generator-identification
milestone: v0.5.8
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/render.py, subprojects/docket/README.md, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_model.py, subprojects/docket/tests/test_plan.py
added: 2026-09-22
closed: 2026-09-23
pr: 944
payoff: show stops telling a reader that a closed head is ranked, so a mechanism its own verdict calls live gets recorded where it can rank instead of being taken as handled
verify: grep -q 'def test_show_on_a_closed_head_says_it_ranks_on_no_tier' subprojects/docket/tests/test_cli.py
impairs-generators: cli.cmd_show reports rank from model.ranks_as_generator and model.impairs_generators_soundly, which test no status, so a done or dropped item carrying generator: live or a sound impairs-generators: is shown as ranked on the generator tier while plan.recommend ranks only startable items - a still-live mechanism on a closed head reads as ranked and is ranked by nothing
---

**Problem.** bin/docket show reports a dropped head marked generator: live as ranked on the generator tier, because cli.cmd_show skips the status test render._verdict_phrase applies (PL-LN69)

**Reproduced 2026-09-23.** `bin/docket show PL-LN69` prints `ranked on the
generator tier - above every band but P0` under the dropped head's `generator:
live` line. So does `show` on the three done heads carrying `generator: live`
(`PL-0HPV`, `PL-8FJK`, `PL-WFFX`), and, through the other entrance, on the done
`impairs-generators:` item `PL-LSR0`. On `PL-8FJK` and `PL-LSR0` the plan line
adds "it ranks above every band but P0" as well. Five closed items misreport.
`bin/docket generators` prints no verdict for the same heads, so the two
surfaces disagree. The cause is that `cmd_show` asks `model.ranks_as_generator`
and `model.impairs_generators_soundly`, and neither tests status, while
`plan.recommend` ranks only the startable set.

**Why it matters.** `show` is how a named item is read. It tells the reader
that four closed heads are being pulled by the tier, when each one's own
verdict says its mechanism is still producing and nothing ranks it. A reader who
believes that has no reason to record the mechanism on an open item, which is
the only place a verdict can rank. So a generator that its own record calls
live goes unranked, while the surface that reports its rank says the opposite.

**Why `impairs-generators:`** (triage, 2026-09-23). This breaks the part of
the machinery that shows a claim to a reader, one of the functions
`subprojects/docket/README.md` lists for the field. It also contradicts rules
the code already states: `render._verdict_phrase`'s "a closed head is on no
tier whatever its verdict says", and the README's "A **closed** head is asked
for nothing". It is a defect in what exists, so `PL-6Q9L`'s pause does not
hold it.

**Done when.** `bin/docket show` on a `done` or `dropped` item that carries
`generator: live` or a sound `impairs-generators:` says the item is on no tier
because it is closed, in both the verdict line and the plan line. An open
`live` head still prints the ranked line.
`test_show_on_a_closed_head_says_it_ranks_on_no_tier` in
`subprojects/docket/tests/test_cli.py` pins the dropped-head case.

**Generator check.** A re-entry of `PL-T7QR` (closed 2026-09-21). Its split of
record from rank put the closed-head test in `render._verdict_phrase` and not in
`cli.cmd_show`, so this is the same conflation of a recorded generator with a
ranked one, at a sibling site. The design fact is that "a closed head is on no
tier" is restated by each reader instead of living in the predicate they share.
No other open item stands on it.

**Worked 2026-09-23.** The status test moved into the rank predicates instead
of being added to `cmd_show` as a third restatement, because the brief's own
generator check names the restating as the design fact. `model.ranks_as_generator`
now refuses a closed item, and `model.ranks_as_generator_defect` is the same
question for the `impairs-generators:` entrance, beside the soundness predicate
`show` had been asking. `recommend` passes only startable items, so it is
unchanged. `show` still names "closed" in its own lines, because it has to say
why an item is on no tier, and `placement_line` takes `closed` so the plan line
stops claiming any rank for a closed item. That was also false of every
ordinary closed item ("it ranks on its band alone").

A third reader had the same fault and was worked here rather than filed, under
the capture rule's clause for a finding that completes an in-progress item.
`bin/docket generators` said "3 items rank on the generator tier by
`impairs-generators:`" and listed `PL-LSR0 (done)` among them. It now lists the
closed defect on its own line, as ranking on no tier.

