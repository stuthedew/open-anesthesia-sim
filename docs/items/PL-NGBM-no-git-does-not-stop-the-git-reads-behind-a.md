---
id: PL-NGBM
title: --no-git does not stop the git reads behind a printed count, so docket digest --no-git shells out to git despite the flag saying branch detection is off
priority: P3
effort: S
status: ready
classes: defect
feature: count-input-addressing
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-20
payoff: --no-git either means what its help says or says what it means, so a session reading a digest count under the flag can tell which reads were skipped
verify: grep -q 'def test_no_git_stops_every_git_read' subprojects/docket/tests/test_cli.py
root-cause-of: PL-T441, PL-WF3X, PL-N0MH, PL-3T2Q, PL-M6FY, PL-P757
generator: live - cli.py builds no invocation object, so root, store prefix, config, runner and --no-git are re-derived per call site; each fix centralised one facet and filed the next, PL-WF3X re-entering 23h after PL-P757 (PL-KVDK)
---

**Problem.** `_flight`, `_stranded` and `_orphaned` each return an empty
report under `--no-git`, so the flag holds for everything the digest used to
do. The inputs `cli._complete_report` gathers do not check it: `cmd_check`
never did, and `digest` and `next` inherited that when `PL-VKGJ` routed all
three through one gathering. So `bin/docket digest --no-git` now runs
`merged_pull_requests`, `closures_on_base`, `records_on_base`, `lost` and
`cut_window` - about 250 ms of git subprocesses - under a flag whose help
reads "skip branch detection".

**Why it matters.** Small in cost and a correctness question in kind: a flag
that turns some git reads off and not others cannot be reasoned about, and the
help text says the wrong thing either way. Honouring it in all three keeps
`PL-VKGJ`'s invariant intact, because all three would then skip the same
inputs and still print counts that agree.

**Done when.** `--no-git` either stops every git read behind a printed count,
in all three commands alike, or says in its help that it means branch
detection only - and a test pins whichever was chosen.
