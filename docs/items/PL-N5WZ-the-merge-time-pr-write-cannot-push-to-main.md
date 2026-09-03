---
id: PL-N5WZ
title: The merge-time pr: write cannot push to main, because required status checks can never report on a GITHUB_TOKEN push - write it locally instead, riding the session's next commit
priority: P2
effort: M
status: done
classes: defect, infra
feature: delegation
touches: .github/workflows/record-pr.yml, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests, Makefile, .claude/skills/docket/SKILL.md, subprojects/docket/README.md
added: 2026-09-03
closed: 2026-09-03
verify: uv run pytest subprojects/docket/tests/test_cli.py subprojects/docket/tests/test_checks.py && grep -q 'def _record_owed' subprojects/docket/src/docket/cli.py
---

**Problem.** `PL-WTQR` moved the `pr:` write to a job fired by the merge. The
job was correct and its first run proved it: it computed `pr: 261` for
`PL-WTQR`, committed it, and was refused by `main`.

```
remote: error: GH006: Protected branch update failed for refs/heads/main.
remote: - 3 of 3 required status checks are expected.
```

**This was not a bypass away from working, which is what decided the item.**
The requirement is *required status checks*, and it cannot be satisfied by
anything that job can do: a push made with `GITHUB_TOKEN` starts no workflow,
so `checks`, `floor` and `pr-title` can never report on the commit it pushes.
The `Base` ruleset was already disabled when the run happened - the project
owner turned it off trying to clear the way - and the push failed anyway, so
the ruleset was never the blocker either. Every configuration that would accept
the push weakens `main`'s own gate, which is a worse trade than the per-item
commit this was built to remove.

**Why it mattered.** Parking the job stopped the failure but restored the cost:
a session reading an advisory, composing a commit, and often a pull request,
after every merge that closed anything. That is what the project owner
objected to in the first place.

**Done when.** A merge that closes items leaves those items carrying their
pull request number without a session composing a commit for it, and without
any change to `main`'s protection.

**Worked 2026-09-03. The project owner chose the local trigger.**

**`docket record`, bare, is the write.** No number and no `--merge`: it asks
the question `check` already asks - which landed closures owe a `pr`, and
which number does the base name for each - and writes the answer instead of
printing it. `closures_on_base` is literally the same call `cmd_check` makes,
so the reporting and the writing cannot disagree.

**Taking no merge is the load-bearing part, not a simplification.** A session
open for a while may be owed numbers from several merges, and reading them
from the base rather than from one commit is what lets the write ride whatever
commit the session was about to make. The cost being removed was never the
typing; it was the commit the typing needed.

**`make fix` runs it**, beside `ruff format` and `ruff check --fix`. That split
already existed for exactly this reason: `make check` runs in CI, where
mutating the tree is not the job, so the reporting half stays there and the
writing half goes here.

**A closure the base names no number for is left alone.** `check` is the
command that decides whether that is provenance lost, a decline, or a
truncated checkout, and pre-empting it would be guessing. That is what makes
`record` safe to run unattended, which putting it in `make fix` requires.

**The explicit form survives for the case that produced `PL-2XTF`.** A squash
subject that led with no id leaves nothing to derive, and the number has to
come from a person reading it off the pull request. `docket record <number>
--merge <commit>` writes that safely - `closed_by` still supplies what the
merge closed, and the command still refuses to overwrite a different number -
rather than the file being edited by hand.

**`.github/workflows/record-pr.yml` is deleted, with its test.** The decision
settles what it was parked pending. `vcs.closed_by` stays: it is what the
explicit form reads, and it is the more careful of the two answers to "what
did this commit close" - by id rather than by path, so a title edit renaming
a file cannot be read as a closure, and declining outright where the parent is
out of reach.

**The exactness argument that chose CI in `PL-WTQR` was worth less than it
claimed.** It rested on the subject scan being the only fallback. It is not:
`PL-2XTF`'s second half already added recovery from the item's own file
history, which is exact for the rider case `PL-GW37` found and for the
UI-titled subject that defeats the scan. What a merge-time trigger uniquely
bought was therefore mostly already in hand - which is the measurement worth
keeping, because it is the one that would have prevented the round trip.
