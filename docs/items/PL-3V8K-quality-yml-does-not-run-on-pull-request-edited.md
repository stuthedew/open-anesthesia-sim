---
id: PL-3V8K
title: quality.yml does not run on pull_request edited, so renaming a title to satisfy pr_title_check cannot clear the check it just failed
status: untriaged
touches: .github/workflows/quality.yml
added: 2026-09-03
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
