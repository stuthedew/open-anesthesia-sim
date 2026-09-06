---
id: PL-J3BB
title: make check cannot run tools/pr_title_check.py, so a branch that closes an item after its PR opened goes red in CI with nothing locally to catch it
priority: P3
effort: S
status: done
classes: infra
feature: dev-tooling
milestone: v0.4.3
touches: Makefile, tools/pr_title_check.py, tests/unit/test_pr_title_check.py
added: 2026-09-03
closed: 2026-09-05
pr: 369
verify: uv run pytest tests/unit/test_pr_title_check.py && grep -q 'def test_a_stale_title_on_the_open_pull_request_fails_locally' tests/unit/test_pr_title_check.py && grep -q 'pr-title' Makefile
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

**Closed 2026-09-05, on the second approach**, with the third folded into how
it declines rather than added beside it.

`tools/pr_title_check.py` gained `--discover`: when `PR_TITLE` is unset it
reads the title from *this branch's own open pull request* through the GitHub
API, and `make check` runs it on that flag. `make pr-title` runs it alone, for
the moment a session has just closed a rider and wants the string to rename to
before pushing.

**Every way the lookup can fail is a silent skip returning 0** - no token, no
network, a proxy refusing, a rate limit, a repository the token cannot see, a
detached HEAD, a non-GitHub remote, or simply no pull request open yet. That is
what keeps `make check` green offline, and it is why the skip prints nothing
rather than declining out loud: a decline would print on every run before a
pull request exists, which is the "prints on most branches without changing
what anyone does" shape this brief said to check against `CLAUDE.md` first.
The advisory from `PL-3BC5` is not built for the same reason; what survives of
it is that the failure message names the exact replacement title, which it
already did.

**The lookup runs before `closes()`, and that ordering is the design.**
`closes()` is a `git show` per item file at both ends of the range - measured
3.2 s against `origin/main` on 555 files - while the lookup is one request. So
a branch with nothing open pays milliseconds, and the expensive half runs only
when there is a title to check it against. The test named for the silent skip
that never reads the trees pins it, with a `_git` that raises if reached.

Ten tests added, seventeen in the file: the stale-title failure and that it
names the pull request number, a leading title passing, the silent skip,
`PR_TITLE` winning over the lookup without spending a request, no token and a
refused connection both declining, all four remote spellings, a non-GitHub
remote, and a detached HEAD.

**The `verify:` command was strengthened when the item was started**, per the
rule about a command that specifies nothing: it was `pytest … && grep -q
'pr-title' Makefile`, which the Makefile edit alone would have satisfied with
no test written. It now also names the test the work owes. Both new halves were
confirmed absent at `HEAD` before the work rather than assumed - `git show
HEAD:… | grep` exits 1 for each - and the whole command passes now.

One thing this still cannot see, unchanged from the brief: a merger who
retypes the subject in GitHub's squash dialog. `PL-2XTF`'s recovery half is
what covers that.
