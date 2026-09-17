---
id: PL-H8YD
title: Auto-merge landed #654 while pr-title was in a failed state, so the check that protects the squash subject does not actually gate the merge: the correct subject landed only because the rename beat auto-merge by three seconds
status: untriaged
feature: pr-title-enforcement
added: 2026-09-17
---

**Problem.** Auto-merge landed #654 while pr-title was in a failed state, so the check that protects the squash subject does not actually gate the merge: the correct subject landed only because the rename beat auto-merge by three seconds

**Why it matters.** `tools/pr_title_check.py`'s own docstring states the stake:
a squash subject "is what reaches the default branch. `docket check` reads it to
recover which pull request closed an item, and `docket flight` reads it to know
what is in flight, so a title that names no id is not a style lapse - it
destroys provenance that cannot be reconstructed from anywhere else." `#220` is
the case that produced the check (`PL-2XTF`): a generated title named none of
the three items it closed, `main` went red, and the numbers had to be read off
the GitHub UI by hand.

**The measurement, from `#654` on 2026-09-17.** Times are the GitHub check-run
timestamps:

| Time | Event |
| --- | --- |
| 03:52:39 | `pr-title` completes: **failure** - title led with `PL-GPYV`, which the branch does not close, and omitted `PL-V03Q`, which it does (`dropped` is a closed status) |
| 03:54:09 | project owner enables auto-merge, squash |
| ~03:54:3x | session renames the pull request to lead with `PL-MQHN, PL-V03Q` |
| 03:54:31 | `checks` completes: success |
| **03:54:34** | **auto-merge merges the pull request** |
| 03:54:39 | the rename's `pr-title` re-run *starts* |
| 03:54:51 | that re-run completes: success |

So the merge fired on `checks` alone, three seconds after it went green, while
the only *completed* `pr-title` run was the failure. The correct subject reached
`main` only because the rename happened to land before auto-merge fired - a
few seconds either way and `#220`'s failure repeats, with `PL-V03Q`'s
provenance unrecoverable.

**This is the first of `CLAUDE.md`'s three compounding-friction tests**, which
is why it is raised in the reply rather than only filed: the guarantee the check
stands for is void at the moment it matters, while the check itself reports
correctly and looks like it is working. It also sits upstream of every future
merge rather than affecting one pull request.

**What is not yet established**, and is the first thing to check: whether
`pr-title` is absent from the branch's required status checks, or is required
but was satisfied by a stale run. The session that found this could not read the
repository's branch-protection settings. The remedy differs - adding the check
to the required set, versus making the rename re-run block - so measure before
changing anything.

**Worth weighing against a real cost.** `pr-title.yml` exists as its own
workflow precisely so a rename can clear it (`PL-3V8K`, `#256`), and making it
required means a pull request cannot merge until a rename's re-run completes -
roughly twelve seconds here. That is the trade, and it looks strongly worth
taking, but the number belongs in the decision rather than in a reply.

**Done when.** It is established whether `pr-title` gates the merge, and if it
does not, either it is added to the required checks or a reason is recorded for
leaving it advisory. Either way `ROADMAP.md` or the workflow's own comment says
which, so the next session does not re-derive it.
