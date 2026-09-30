---
id: PL-6WPD
title: bin/docket set --touches says nothing about whether the paths it writes owe a Generator check, so a capture triage marks undecided (12 of 22 on 2026-09-28) is decided by reading workflow_paths in docket.toml by hand, at the moment the question is likeliest to be skipped
priority: P1
effort: S
status: done
classes: defect
feature: generator-identification
milestone: v0.5.19
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, .claude/skills/docket/modes/triage.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-30 triage pass
added: 2026-09-28
closed: 2026-09-30
pr: 1240
payoff: a capture whose touches triage writes in the set that takes it off the list is still asked where it came from, so a generator reached through one is found rather than queued
verify: grep -q 'def test_set_names_the_paths_a_triage_write_leaves_owing_a_generator_check' subprojects/docket/tests/test_cli.py
impairs-generators: cli.cmd_set writes the touches render._generator_check reads and moves the item off the triage list that mark prints on, in one call and printing nothing of the check, so a capture with no touches - 12 of 22 on 2026-09-28 - is asked where it came from only if the session holds the rule
---

**Problem.** bin/docket set --touches says nothing about whether the paths it writes owe a Generator check, so a capture triage marks undecided (12 of 22 on 2026-09-28) is decided by reading workflow_paths in docket.toml by hand, at the moment the question is likeliest to be skipped

**Found closing `PL-4NZ7`, 2026-09-28.** `bin/docket triage` now marks each
untriaged item whose `touches` name a `workflow_paths` path as owing a
Generator check, and says `undecided until touches is set` where capture left
them unset. But a triage pass usually writes `touches` and `--status ready` in
one `bin/docket set` call, after which the item has left the triage list, so
the mark for those twelve never prints: the session has to hold the rule and
check each path against the 60-entry list itself. A line from `set` naming the
declared paths under `workflow_paths`, where the brief carries no
`**Generator check.**` line (`checks.answers_generator_check`), would put the
answer where the paths are written.

[superseded 2026-09-30: no open item carries `generator: live` since `PL-MT3R`
closed, and triage recorded this as a defect in identification machinery, which
the pause never held] Captured, not built: `generator: live` items are open, and
this is new identification machinery for triage to rank.

**Reproduced 2026-09-30, at `c9ae80e7`.** In a scratch store declaring
`workflow_paths = ["tools"]`, `bin/docket triage` printed "Generator check:
undecided until `touches` is set" for an untriaged capture. `bin/docket set
PL-D4D4 --touches tools/check.py --status ready --priority P2 --effort S
--classes defect` then printed its five field lines and the file's path and
nothing about the check, and `bin/docket triage` afterwards printed "Nothing is
untriaged."

**Why it matters.** Triage's Generator check is how a generator is found in
what arrives (`.claude/skills/docket/modes/triage.md` § "Ask every item touching
the apparatus where it came from"). For a capture with no `touches` - twelve of
the twenty-two untriaged on 2026-09-28, four of the five on 2026-09-30 - the
triage list can only say the check is undecided, and the write that decides it
takes the item off that list. So whether the check is asked rests on the session
holding a 59-entry path list at the step it is likeliest to skip, and a
generator reached through such an item is queued rather than found: the failure
`PL-4NZ7` was fixed for, one command further on.

**Done when.** A `bin/docket set` write that decides the check - one writing
`touches` or moving `status` on an item that was untriaged, or writing the first
`touches` on one that declared none - says what `bin/docket triage` would have:
that a check is owed, naming the paths under `workflow_paths`, where the brief
carries no `**Generator check.**` line; that it is undecided, where the write
takes the item out of triage with no `touches`. It says nothing where the brief
answers the check, where no path is apparatus, or on a write to an item already
triaged with paths declared. Tests in `subprojects/docket/tests/test_cli.py` hold
each, and `triage.md` and `subprojects/docket/README.md` say so.

**Generator check.** Not a member of any head: it is the identification
machinery itself, a follow-up of `PL-4NZ7` found while closing it and recorded
under `impairs-generators:` as `PL-4NZ7` was. The fact both read - which items
owe triage's Generator check, read off `touches` against `workflow_paths` - is
stated in no head's `misread:`, and two items on one fact are not three.

**Scope: triage writes only, counted 2026-09-30.** The capture proposed the line
on any `--touches` write. 118 of the 169 open triaged items reaching
`workflow_paths` carry no `**Generator check.**` line, most triaged before the
rule of 2026-09-22, so a start's re-confirmation or a close-out's reconciliation
rewriting their `touches` would be told a check is owed that the rule never asks
of them: an advisory firing where it changes no decision. The narrowing gives up
an item triaged with no `touches` at all, whose check was never decidable; that
is one open item, and the first `touches` written on such an item counts as a
triage write.

**What landed, 2026-09-30.** `render.generator_check_on_set` reads the item
before and after a `set` write and, on the writes the scope above names, prints
`owes a Generator check, whatever its lane: it touches ...` with the paths under
`workflow_paths`, or that it "leaves triage declaring no `touches`" where the write ends
triage with the item open and no paths; `cli.cmd_set` prints it after its other
notes. `render._apparatus_named` is the one reading of which paths owe the
check, shared with the triage mark. Held by
`test_set_names_the_paths_a_triage_write_leaves_owing_a_generator_check`, the
undecided test, and five silent cases in `subprojects/docket/tests/test_cli.py`;
the two positive tests fail on the old code, and a mutant dropping both scoping
conditions fails three of the silent ones.
