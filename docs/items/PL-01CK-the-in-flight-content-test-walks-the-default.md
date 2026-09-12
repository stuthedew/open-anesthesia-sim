---
id: PL-01CK
title: The in-flight content test walks the default branch's history once per blob a candidate branch adds
priority: P3
effort: S
status: dropped
classes: perf, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-08-31
closed: 2026-09-12
reason: fixed by PL-3D2M (#313): deciding a ref is unlanded now computes the whole landed/outstanding split, so _base_blobs answers every blob with one git rev-list --objects walk instead of a git log --find-object walk per blob
---
**Problem.** `_work_already_on_base` (added by `PL-CPSY`) asks `git log -1
--find-object=<blob> <base>` once per blob a candidate ref adds to the tree it
forked from. Each call is a full history walk with a diff at every commit, and
it only stops early when it finds the blob - so the cost of the refs that are
*not* landed, which is every live session's branch, is paid in full.

`all()` short-circuits on the first blob the default branch has never held, so
the common shape - a live branch whose first blob is its own - costs one walk.
The bad shape is a branch most of whose blobs landed and one of whose did not:
that pays a walk per landed blob before the answer arrives.

**Why it matters.** `branches_in_flight` runs in the session-start digest, so
its cost is paid by every session before it does anything. Measured in this
repository at 135 commits it is 3-8 ms per walk, which is nothing; the walk is
linear in history, so a repository an order of magnitude older pays an order
of magnitude more, per blob.

**Where.** `subprojects/docket/src/docket/vcs.py` - `_work_already_on_base`.

Two narrowings exist and neither is free. A pathspec (`-- <path>`) makes the
walk diff one path instead of every path, which is most of the saving, but the
path has to be parsed out of `git diff --raw` output, where git quotes names
containing specials unless `-z` is used - the reason the current code reads
only the blob. Capping the blobs tested per ref bounds the work but has to
decide what an untested blob means, and the safe answer ("not landed") gives
back the fix for exactly the large branches the cap fires on.

**Done when.** Either the walk is narrowed with a measurement showing the
saving on a history where it matters, or the cost is measured and recorded as
acceptable and this is dropped with that number in its reason.

**Decision needed.** Narrow the walk, or accept the cost and drop this? Nothing
in this repository forces the question: `bin/docket flight` answers in 116 ms
end to end, interpreter start included, measured 2026-09-01. The decision wants
the walk count on a history where it matters, which this project cannot produce
yet, so the honest answer today may be to drop it with that number.

**Triaged 2026-09-01.** P3, `perf`/`infra`, `parallel-sessions`. Left out of
v0.2.8's frozen list: the walk is slow in a shape nobody has observed, which is
an improvement to named machinery rather than a defect in it.

**Dropped 2026-09-12**, by the workflow-lane consolidation pass (`PL-6ZQY`).
The premise was checked against the tree by an adversarial reviewer whose
default was to refuse, and it did not survive:

> Fixed by `PL-3D2M` (a commit pushed after its pull request merged lands nowhere), pull request 313: deciding a ref is unlanded now computes the whole landed/outstanding split, so `_base_blobs` answers the per-blob question for every blob at once with one `git rev-list --objects <base>` walk instead of a `git log --find-object` walk per blob. `subprojects/docket/src/docket/vcs.py:485` carries the measurement — 17 `--find-object` walks at 0.62 s against 0.033 s for the complete split, on this repository at 425 commits — and `test_a_squash_merged_branch_is_judged_against_the_history_not_the_tip` pins the single walk. Traced 2026-09-12: `bin/docket flight`, `next` and `digest` issue zero `--find-object` calls. The rejected narrowings recorded above (pathspec quoting, per-ref blob cap) are kept in this file because neither was taken. The remaining flight-read cost — the report computed twice 

What the file keeps that exists nowhere else, which is why it is dropped rather
than deleted: Nothing actionable, provided the file is kept. PL-01CK holds three observations that exist nowhere else in the tree: the per-walk figure (3-8 ms at 135 commits), the end-to-end baseline (`bin/docket flight` in 116 ms, measured 2026-09-01), and the analysis of the two narrowings that were considered and rejected (a `-- <path>` pathspec, blocked by git quoting paths with specials unless `-z` is used, which is why the code read only the blob; and a per-ref blob cap, whose safe reading of an unteste

