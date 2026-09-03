---
id: PL-3V8K
title: quality.yml does not run on pull_request edited, so renaming a title to satisfy pr_title_check cannot clear the check it just failed
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.3.2
touches: .github/workflows/quality.yml, .github/workflows/pr-title.yml
added: 2026-09-03
closed: 2026-09-03
pr: 256
verify: python3 tools/doc_check.py check && grep -rq 'types: [opened, synchronize, reopened, edited]' .github/workflows/
---

**Problem.** `tools/pr_title_check.py` fails a pull request whose title does not
lead with the ids the branch closes, and tells the author exactly what to do:
"Rename the pull request to lead with the ids". Renaming it does not clear the
check.

`.github/workflows/quality.yml` declares a bare `pull_request:` trigger, which
GitHub defaults to `types: [opened, synchronize, reopened]`. A title edit is
`edited`, so no run is queued and the failed check stays failed on the head
commit. The only way out is to push a commit — which is exactly what the
prohibition on empty commits to kick CI exists to prevent, so an author who
has nothing else to push is stuck between two rules.

Observed 2026-09-03 on PR #256: the branch closed `PL-P0BB` and `PL-SPMQ` after
the pull request was opened, the title check went red, and renaming the title
left it red.

**Why it matters.** A check that tells you the fix and then cannot observe the
fix is worse than no check: it reads as a defect in the branch when the branch
is correct. It also pushes toward the one remedy the working agreement forbids.

**Where.** `.github/workflows/quality.yml`'s `on:` block.

**Approach, and the reason not to take the obvious one.** Adding `edited` to a
bare `pull_request:` trigger would re-run the *entire* quality job — sync, ruff,
mypy, 1182 tests, docket, doc_check, contrast — on every title and body edit,
including the body edits a session makes while iterating on a description. That
is a large recurring cost for a check that reads one string and one `git log`.

Prefer splitting the title check into its own workflow triggered on
`pull_request: types: [opened, synchronize, reopened, edited]`, leaving the
heavy job on the default trigger. It needs no virtualenv — `tools/` runs under
a bare `python3` by contract, which `tests/unit/test_tools_portability.py`
holds it to — so the split job is a checkout and one script.

**Done when.** Renaming a pull request title to the form `pr_title_check`
prints clears the check without a push, and the heavy quality job still runs
only on open, push and reopen.

**Closed 2026-09-03, the recommended way rather than the obvious one** (project
owner authorized the fix the same day). `.github/workflows/pr-title.yml` is a
new workflow triggered on `pull_request: types: [opened, synchronize, reopened,
edited]`, carrying the title check alone; `quality.yml` keeps its default
trigger and no longer runs it. So a rename now clears the check it failed, and
no title or body edit re-runs the test suite.

The split job needs no uv and no virtualenv: `tools/pr_title_check.py` is
standard library plus the vendored `subprojects/docket/`, which it puts on
`sys.path` itself. Verified under a bare `python3` before the workflow was
written — it ran clean on Python 3.11, three minor versions below the pinned
3.14, which is the portability contract `tests/unit/test_tools_portability.py`
and `quality.yml`'s `floor` job hold `tools/` to. The job is therefore a
checkout and one script, with no dependency resolution in front of it.

`fetch-depth: 0` is carried over deliberately and the reason is written at the
step: the script computes what the branch closes from `PR_BASE..HEAD`, and a
depth-1 clone makes that range empty, which reads as "closes nothing" and would
pass any title at all. A cheaper checkout would have turned the check into a
no-op that reports success.

`tools/doc_check.py` needs no change: `WORKFLOW_GLOBS` already covers
`.github/workflows/*.yml`, so the new file's `run:` path is checked like any
other, confirmed passing.

**One thing this changes that only the project owner can act on.** The check
now reports under a new check-run name, `pr-title`, where it previously ran
inside `checks`. If branch protection on `main` requires specific status checks
by name, `pr-title` has to be added to that list or the title guard becomes
advisory. Verified from this session: the repository's checks are `checks` and
`floor`, and whether either is *required* is a repository setting this session
cannot read. To set it: GitHub → the repository → Settings → Rules → Rulesets
(or Settings → Branches → branch protection rules for `main`) → edit the rule
covering `main` → under "Require status checks to pass", add `pr-title` to the
list beside `checks` and `floor` → Save. If no ruleset requires status checks
today, nothing needs doing and the check behaves exactly as it did.
