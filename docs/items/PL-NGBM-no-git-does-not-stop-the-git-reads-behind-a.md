---
id: PL-NGBM
title: --no-git does not stop the git reads behind a printed count, so docket digest --no-git shells out to git despite the flag saying branch detection is off
status: untriaged
feature: count-input-addressing
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-20
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
