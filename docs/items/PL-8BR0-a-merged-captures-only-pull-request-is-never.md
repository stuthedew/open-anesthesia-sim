---
id: PL-8BR0
title: A merged captures-only pull request is never recognised as merged, because vcs.landed_whole refuses queue-only commits as merge evidence (PL-JBRC), so branch tells its session to merge the base in, arm says arm for a pull request that already merged, and the next capture there lands nowhere
priority: P2
effort: M
status: done
classes: defect, infra
feature: one-snapshot
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/render.py, subprojects/docket/README.md, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_vcs_silence.py, tools/open_pull_requests.py, tests/unit/test_open_pull_requests.py, docket.toml, docs/ARCHITECTURE.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-snapshot batch
added: 2026-09-25
closed: 2026-09-27
pr: 1147
payoff: a session whose pull request already squash-merged is told to restart instead of merging the base in, so its next capture is not stranded on a branch nothing will merge again
verify: grep -q 'def test_a_merged_captures_only_branch_is_told_to_restart' subprojects/docket/tests/test_vcs.py
recurrences: 2026-09-26 PL-RLTK
---

**Problem.** A merged captures-only pull request is never recognised as merged, because vcs.landed_whole refuses queue-only commits as merge evidence (PL-JBRC), so branch tells its session to merge the base in, arm says arm for a pull request that already merged, and the next capture there lands nowhere

Reproduced (scenario f): capture, push, PR; `arm` says arm; squash-merge; fetch; `branch` says "1 behind, 1 ahead ... git merge origin/main", `arm` says behind 1; capture again, `arm` says "arm - mark its pull request ready and arm it" for a merged PR. `stranded` does catch the lost capture. PRs carrying only item files are exactly the ones PL-WNCT auto-merges. A gap in PL-8M8H.

**Why it matters.** A lost-capture path on the one kind of pull request the process arms automatically.

**Done when.** A captures-only branch whose pull request merged is told to restart; the forge's merged state, where available, is the evidence; a test holds scenario f.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Seen again, 2026-09-25, on a pull request that was not captures-only.** `PL-P0FP`'s pull request 1007 carried `docs/stress-2026-09-25/evidence.tar.gz` beside its items. It squash-merged and GitHub deleted the branch. The next session-start digest in that session still reported the branch 2 behind and 9 ahead and told it to run `git merge origin/main` before its first edit, while listing `PL-P0FP` itself among the items landed on `origin/main`. Every path the branch changed already matched `origin/main`. So the captures-only reading above may not be the whole cause: check whether the digest and `branch` consult `landed_whole` at all before advising a merge.

Reproduced 2026-09-25 against 46954a81, in scratch clones: a branch carrying one capture was pushed and squash-merged onto `origin/main`; after a fetch, `branch` said `claude/scratch-cap is 1 behind origin/main and 1 ahead`, advised `git merge origin/main`, and listed the branch's own capture as landed, and `arm` said `behind 1`. On the question the paragraph above leaves open: `branch_state` does consult `landed_whole` (vcs.py:2136), but only when it would advise a merge, and `landed_whole` still refuses a queue-only commit as merge evidence. `arm`'s verdict is `arming.arm`, so `touches` now carries `arming.py`.

**Generator check.** PL-GHHW's fact, whether the base already holds a branch commit's change by whatever route, in an instance filed once that head had closed (2026-09-23, spent): `landed_whole` is a reader its fix did not move onto `vcs.change_landed`. Not PL-XBV4's freshness fact, since the refs here were fresh, so it is removed from that head's `root-cause-of`.

## Design, 2026-09-27 (the session that built it)

**The evidence is the forge's word on the branch's newest pull request, read
through a configured command.** `PL-SK88` and `PL-VV4D` keep GitHub out of
`docket`, so the package asks a command named in `docket.toml`, as
`open_pull_requests_command` already does: `newest_pull_request_command`,
empty by default, which `tools/open_pull_requests.py --newest BRANCH BASE`
answers with the listing `tools/left_behind_check.py` already makes (every
state, that head, that base, newest first, one result). Contract: exit 0 and
one line `NUMBER STATE HEAD`, `STATE` one of `open`, `merged`, `closed`; exit
0 and nothing where no pull request was ever opened from the branch; non-zero
where it could not ask. `HEAD` is the listing's `head.sha`, which GitHub
freezes when a pull request closes: checked on `#793`, whose branch took a
commit after the merge, the API still names `46620e20`, the commit
`refs/pull/793/head` holds.

**The reading is git's and stays in `vcs`.** A branch still carries a merged
pull request where the newest is `merged`, its head `H` is a commit this clone
holds, `H` is not on the base, and `HEAD` is `H` or descends from it. The
commits past `H` that are not merges, not on the base, and not ones whose
change `vcs.change_landed` finds on the base are what nothing will merge.
`H` on the base is a merge-commit merge, after which every branch restarted on
the base descends from `H`; the reading stands aside there rather than send a
restarted branch round again. It sets `BranchState.merged`, and `disposition`
answers `LANDED` whatever the counts say, since a branch that merged the base
in after its pull request merged reads `CURRENT` and its next commit lands
nowhere; a declined read, `REWRITTEN` and `PULL` still come first. A newest
pull request that is `open` outranks the content reading's `LANDED`, which
then gives `MERGE` (`PL-RLTK`'s symptom, where the forge answers; that item's
content fix is still needed offline and for `orphaned`). Closed unmerged, none
opened, or `H` not carried: the content reading as before, queue-only refusal
(`PL-JBRC`) included, since without the forge it is still right.

**Asked by `branch` and `arm` only.** The per-command snapshot stays off the
network (`PL-XBV4`). `branch` asks only where the answer could move the advice:
not the default branch, not declined, not `REWRITTEN`, and `ahead > 0`.

**What they print.** `branch`: the pull request and the head it merged, the
commits past it, and the restart with a `git cherry-pick` of exactly those, or
restart-before-the-next-commit where none is past it. A configured command
that did not answer adds one line saying so, and that the answer rests on
content, which cannot see a merge of queue-only commits. `arm`: a fifth
answer, `landed` (exit 1), outranking `hold`, `behind` and `arm`: nothing
merges a merged pull request again, so restart, push, and open a new one. A
configured command that did not answer is `unknown`, since `arm` never answers
from a partial read.

**Tests.** Scenario f with real git: capture, push, `arm` arms; a squash from
another clone; `branch` and `arm` say landed; capture again; `branch` names
that capture as the commit to carry. Beside it, the open override, the
unanswered command, a merged head on the base standing aside, and the tool's
`--newest` parsing.
