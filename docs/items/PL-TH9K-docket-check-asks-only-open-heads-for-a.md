---
id: PL-TH9K
title: docket check asks only open heads for a generator verdict, so a closed head whose mechanism keeps producing is never re-asked: six of the fourteen closed heads were still live on 2026-09-22
priority: P3
effort: S
status: ready
classes: feature
feature: generator-identification
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-22
payoff: a closed head recorded as still live is put in front of a session instead of ranking nowhere unnoticed
not-delegable: its first step counts the closed heads still carrying generator: live, and that count decides between building the narrow check and dropping the item; no command can prove an outcome the count has not chosen yet
---

**Problem.** docket check asks only open heads for a generator verdict, so a closed head whose mechanism keeps producing is never re-asked: six of the fourteen closed heads were still live on 2026-09-22

**Reproduced 2026-09-23.** `model.generator_faults` returns nothing for a
closed item, so `bin/docket check` names none of the 22 closed heads that carry
a sound `root-cause-of:`. Twelve of those carry no verdict. This is the stated
rule, not a lapse: `subprojects/docket/README.md` says "A **closed** head is
asked for nothing: it is startable by nothing, so its verdict would move no
ranking", and `CLAUDE.md` says `bin/docket check` "asks any open generator that
has not answered". Four closed heads do carry `generator: live` (`PL-0HPV`,
`PL-8FJK`, `PL-LN69`, `PL-WFFX`). They rank nowhere, and nothing says so.
`bin/docket show` says they do rank, which is `PL-BBT8`.

**Half of it is already answered.** Since `PL-KVDK` (#915, 2026-09-22), triage
asks every new workflow-lane item whether it is a post-close instance of a
closed head. Three such instances are recorded as a generator on an open item,
where it ranks. That asks the question at the only moment new evidence arrives,
and all 25 heads are in the workflow or crossing lane. What it does not reach
is a verdict already written. Each of the four closed `live` heads records a
mechanism that is still producing, and nothing puts them in front of a session.

**Why it matters.** A `live` verdict on a closed head is a recorded claim that
the store is still being handed work, and it moves nothing, because the tier
ranks only startable items. Four such claims stand today, and nothing prompts
anyone to record them where they would rank.

**This is not `impairs-generators:`, and that was checked** (triage,
2026-09-23). The code does what its rule says. Re-asking closed heads would
re-specify the generator rule's "asked for nothing".

**Pause.** `PL-6Q9L`'s pause holds this. While any open item carries
`generator: live`, no re-specification of the generator rule is built.
`blocked-by` names the three open items that carried one on 2026-09-23. When
they close, confirm that `bin/docket next` shows the generator tier empty before
unblocking, because any new `live` head keeps the pause in force.

**Unblocked 2026-09-23 by `PL-1P5V`, the last open item on the generator
tier.** `PL-BBT8` and `PL-DSPM`, the two machinery defects that shared it, merged
the same hour, so the tier is empty once `PL-1P5V`'s pull request lands and the
pause above has ended.

**Done when.** One of two outcomes. Either `docket check` names a closed head
that carries `generator: live` and asks for its mechanism to be recorded on an
open item, or the item is dropped because triage's post-close question has
re-homed the four. Demanding a verdict from all 22 closed heads is not the fix,
since that is what the README refuses.

**Recommended.** When the pause lifts, count the closed `live` heads first, and
build the narrow check only if any still stand.

**Generator check.** A one-off from `PL-KVDK`'s audit. It is not a post-close
instance of any head, and it is not a re-entry. Its design fact is that a head's
status records the fix while its verdict records the mechanism, so the verdict
is stranded when the fix closes. `model.generator_faults` and
`render._verdict_phrase` encode that on purpose. The item is another proposal
to re-specify the generator rule, which is the rule-driven inflow `PL-KVDK`
counts and `PL-6Q9L` pauses.
