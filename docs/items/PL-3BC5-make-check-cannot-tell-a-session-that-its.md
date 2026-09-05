---
id: PL-3BC5
title: make check cannot tell a session that its branch now closes an item whose id leads no commit subject, so the mismatch is only found by pr-title in CI
status: untriaged
feature: documentation-standard
touches: tools/pr_title_check.py, tools/branch_id_check.py, Makefile
added: 2026-09-05
---

**Problem.** `tools/pr_title_check.py` refuses a pull request whose title does
not lead with every id the branch closes. It runs only in
`.github/workflows/pr-title.yml`, because a title does not exist until the pull
request does. `tools/branch_id_check.py` is the local half and deliberately
asks a weaker question — *some* commit on the branch carries an id — and says
so in its own docstring: "Not every commit - one is enough."

So nothing local answers "which ids does this branch close, and does anything
lead with them?" On `#339` the closure arrived in the last commit: `PL-BFV8`
was dropped as a duplicate after the pull request had already been opened and
titled, and `make check` passed with `branch-id: visible in flight - a commit
subject leads with PL-MPZ0` while the title was already wrong. Two CI runs of
`pr-title` failed before the rename.

**It recurred on the same branch, which is the point.** Later the same day
`PL-6SBB` was closed on `#339` too, again after the title was set, and
`pr-title` failed again — three failed runs across two occurrences on one pull
request, each fixed by a rename rather than by a commit. A session that has
just been caught by this check still walks into it, because nothing between
the closure and the push mentions the title.

**Why it matters.** The failure mode is the sequencing rather than
forgetfulness: a title is written when the pull request opens, and the set of
ids the branch closes can still grow afterwards — a duplicate found late, a
rider closed on the way past. A session that has read `CLAUDE.md`'s "a commit
closing more than one item leads with all of them" can still get this wrong for
that reason, which is what happened here.

The cost is small and it is paid in the slowest place: a CI cycle per miss, on
the check that runs before a merge.

**Where.** `closes(base, head)` in `tools/pr_title_check.py` already computes
the answer with the standard library, by comparing the closed set at both ends
so a base merge is not read as a closure. What is missing is a caller that runs
it locally and prints the required prefix. Two shapes, and the second is
probably right:

- extend `tools/branch_id_check.py` — but its narrow question is deliberate and
  documented, and widening it would blur what it certifies;
- add an advisory to `make check` that calls `closes()` and prints
  `PL-XXXX, PL-YYYY: <what it does>` when the branch closes anything. Advisory,
  not an error: `pr-title` is the gate, and a branch that will never become a
  pull request owes nothing.

**Done when.** A session that closes an item on a branch is told, before it
pushes, which ids its pull request title has to lead with — and the advisory
stays silent on a branch that closes nothing. Check it against
`CLAUDE.md`'s "a check earns its place every run" before building: if it would
print on most branches without changing what anyone does, it is not worth it.
