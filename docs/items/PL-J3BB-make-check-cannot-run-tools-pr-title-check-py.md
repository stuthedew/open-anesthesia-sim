---
id: PL-J3BB
title: make check cannot run tools/pr_title_check.py, so a branch that closes an item after its PR opened goes red in CI with nothing locally to catch it
priority: P3
effort: S
status: ready
classes: infra
feature: dev-tooling
verify: uv run pytest tests/unit/test_pr_title_check.py && grep -q 'pr-title' Makefile
touches: Makefile, tools/pr_title_check.py
added: 2026-09-03
---

**Problem.** `tools/pr_title_check.py` reads `PR_TITLE` and `PR_BASE` from the
environment and runs only in `.github/workflows/quality.yml`. `make check` does
not run it, so a session can have every local gate green and still turn CI red
on the title.

The failure is not hypothetical and is not a one-off: the check compares the
title against **what the branch closes**, and a branch closes more items as it
goes. A title that was correct when the pull request opened stops being correct
the moment the next item closes on that branch, which is the ordinary shape of
working an item and then a rider. Observed 2026-09-03 on PR #256.

**Why it matters.** This is the only gate in the project a session cannot run
before pushing, so it is the only one whose failures are always discovered by
CI rather than locally. Each occurrence costs a CI cycle and — because
`quality.yml` does not re-run on a title edit (`PL-3V8K`) — a further push to
clear it.

**Where.** `Makefile`, and possibly a small addition to
`tools/pr_title_check.py` so it can discover the title itself.

**A third approach, from `PL-3BC5` (dropped as a duplicate, 2026-09-05).**
Do not obtain the title at all. `closes(base, head)` already computes the ids
the branch closes with the standard library; an advisory on `make check` that
prints `PL-XXXX, PL-YYYY: <what it does>` whenever the branch closes anything
tells the session what its title has to lead with, before the push and before
the pull request exists. That sidesteps what makes both options below awkward -
the first depends on remembering, the second on the pull request already being
open - and it is advisory rather than an error, because `pr-title` is the gate
and a branch that never becomes a pull request owes nothing.

`PL-3BC5` also carries the recurrence evidence: `#339` failed `pr-title` three
times across two occurrences, `PL-BFV8` dropped as a duplicate after the title
was set and `PL-6SBB` closed on the same branch later the same day. The failure
is the sequencing rather than forgetfulness, which is the argument for a check
that fires on every push rather than a target somebody runs.

Check it against `CLAUDE.md`'s "a check earns its place every run" before
building: if it would print on most branches without changing what anyone does,
it is not worth it.

**Approach.** The script already does the hard half: it computes what the
branch closes from `PR_BASE..HEAD`. What it lacks locally is the title. Two
options, and the second is better:

- A `make pr-title PR_TITLE="..."` target the session runs by hand before
  opening a pull request. Cheap, but it depends on remembering, which is the
  failure mode being fixed.
- Have the script fall back to reading the *open pull request's* title for the
  current branch when `PR_TITLE` is unset, and skip silently when there is no
  pull request. Then `make check` can run it unconditionally: it is a no-op on
  a branch with no pull request open, and it catches the real case — a branch
  whose pull request exists and whose closed set has grown since. Discovering
  the title needs a GitHub call, so `make check` must treat "cannot reach the
  API" as a skip rather than a failure, in keeping with the stdlib-only,
  works-offline contract `tools/` holds to.

**Done when.** A branch whose open pull request's title no longer leads with
everything it closes fails `make check` locally, and `make check` still passes
offline and on a branch with no pull request.

**Triaged 2026-09-03, P3, and the priority is lower than it looked when
captured.** `PL-3V8K` closed the expensive half the same day: a wrong title now
costs a rename, which clears the check on its own, rather than a rename plus an
unrelated commit to make CI look again. What remains is one wasted CI cycle and
the round trip of noticing, which is real but small. P3 rather than P2 for that
reason, and because the second approach above needs a GitHub call from
`make check`, which has to stay green offline.
