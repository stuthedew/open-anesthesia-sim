---
id: PL-H8YD
title: Auto-merge landed #654 while pr-title was in a failed state, so the check that protects the squash subject does not actually gate the merge: the correct subject landed only because the rename beat auto-merge by three seconds
priority: P2
effort: S
status: done
classes: defect
feature: pr-title-enforcement
milestone: v0.4.28
touches: .github/workflows/pr-title.yml
added: 2026-09-17
closed: 2026-09-17
pr: 657
verify: python3 tools/doc_check.py check && grep -qF 'This job is in the required set as of 2026-09-17' .github/workflows/pr-title.yml
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

## Answered 2026-09-17: absent, and lost in a refactor rather than decided

**It was absent from the required set**, and the project owner has added it. The
question this brief left open - absent, or required but satisfied by a stale run
- is settled, and so is the one the owner asked next: whether it had been
removed deliberately to leave human editors a way through. It had not.

The title check was created as a **step inside `quality.yml`'s `checks` job**
(`PL-2XTF`, `#227`): at that commit `quality.yml`'s job list is `checks:` at
line 2, the title check at line 54, `floor:` at line 77. `checks` was already a
required status check, so the title rule genuinely gated merges.

`PL-3V8K` (`#256`, 2026-09-03) then split it into `pr-title.yml`, for a correct
and unrelated reason: `quality.yml` declared a bare `pull_request:` trigger,
which excludes `edited`, so renaming a title could not clear the check it had
just failed and the only way out was an empty commit the working agreement
forbids. **That split turned a step into a job**, and a job reports a status
check of its own that nothing makes required by default. The gate was therefore
left behind by a good fix to a different problem, and nothing in the tree could
show it, because the required list lives in repository settings no script here
can read.

**The repository already guards the opposite direction and only that one.**
`PL-KPP1` (`#377`) recorded that removing a job orphans any required check named
after it, which is why both workflows carry the job-name warning. Nothing guards
*adding* a job whose check ought to be required - which is the direction that
bit here, and which stayed lost for eleven releases until `#654`.

**Worth weighing against a real cost.** `pr-title.yml` exists as its own
workflow precisely so a rename can clear it (`PL-3V8K`, `#256`), and making it
required means a pull request cannot merge until a rename's re-run completes -
roughly twelve seconds here. That is the trade, and it looks strongly worth
taking, but the number belongs in the decision rather than in a reply.

**Done when.** It is established whether `pr-title` gates the merge, and if it
does not, either it is added to the required checks or a reason is recorded for
leaving it advisory. Either way `ROADMAP.md` or the workflow's own comment says
which, so the next session does not re-derive it.
