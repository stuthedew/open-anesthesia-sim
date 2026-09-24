---
id: PL-Y1W0
title: Eight squash bodies landed non-empty but different from their pull request's body (#834, #844-847, #861, #868, #938), and tools/pr_body_check.py tests only for an empty body, so it cannot see one
priority: P2
effort: M
status: ready
classes: defect
feature: pr-body-integrity
touches: tools/pr_body_check.py, tests/unit/test_pr_body_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-24 triage pass
added: 2026-09-23
payoff: a commit on main that says something other than its pull request is reported, not passed as intact
verify: grep -q 'def test_fires_on_a_squash_body_that_differs_from_its_pull_request_body' tests/unit/test_pr_body_check.py
---

**Problem.** Eight squash bodies landed non-empty but different from their pull request's body (#834, #844-847, #861, #868, #938), and tools/pr_body_check.py tests only for an empty body, so it cannot see one

**Premise re-checked at triage, 2026-09-24.** In `tools/pr_body_check.py`,
`missing()` counts a body as lost only when it is empty. Nothing compares a
squash body with its pull request's. Detection is offline by design, and
`fetch_body` runs only under `--recover`, for commits whose body is already
empty.

All eight named pull requests were fetched and compared after normalising
them, and all eight differ:

- `#834`, `#861` and `#868`: the squash body is exactly
  `auto_merge.commit_message`, the body as it stood when auto-merge was armed.
  The pull request's body was edited after that. This is the body version of
  `PL-M7W1`'s frozen subject.
- `#844` to `#847` and `#938`: merged directly, with no edit after the merge.

Of the 69 squash merges after `#921`, three differ: `#938`, `#968` and `#981`.
The last two are not in this title. A plain equality test would flag 68 of the
69, because GitHub appends a `---------` line and a `Co-authored-by` trailer
and the footer differs. Those have to be normalised away first.

**Why it matters.** The check exists so that a commit on `main` carries the
reasoning its pull request states. It passes on a body that says something
else, so its guarantee is void for exactly the merges it cannot see.
`PL-WFFX` was closed `spent` on this check's reading ("none of the 47 merges
since #918 lost its body"), which could not have seen these.

**Done when.** `tools/pr_body_check.py` reports a squash body that differs
from its pull request's body, after normalising GitHub's appended lines, in a
mode that may use the network. `tests/unit/test_pr_body_check.py` pins it.

Two neighbours, and neither blocks this:

- `PL-73G8` shares the file. It is about the recovery header's claim that it
  holds the body verbatim.
- `PL-DMNX` asks the neighbouring question for what a session sends: whether
  reading the published body back could be scripted.

**Generator check.** An instance of `PL-WFFX`'s fact, filed after that head
closed: the squash commit's body as the merge sends it, not as the pull
request shows it. `#938` merged 2h13m after the close, with a differing body.
That is one post-close item and three post-close merges. A second post-close
item would reopen `PL-WFFX`'s `spent` verdict, and this item's work is what
would let the store see one.
