---
id: PL-BKDP
title: "A v0.4.8 tag exists on the commit that closed PL-0GTC and PL-SR8F, but no release was cut there: pyproject.toml still reads 0.4.7, there is no docs/releases/v0.4.8.md, and doc_check fails on the missing version-table row"
priority: P1
effort: S
status: needs-decision
classes: defect, planning
feature: release-process
touches: ROADMAP.md, pyproject.toml, docs/releases
added: 2026-09-07
---

**Problem.** `git ls-remote --tags origin` holds `v0.4.8` at `3ddea5c`,
dereferencing to `b03a7d0` — the merge commit of `#432`, which closed
`PL-0GTC`, `PL-CL8J` and `PL-SR8F` and turned main's verify replay green. No
release was cut at that commit:

- `pyproject.toml` on `main` reads `version = "0.4.7"`;
- there is no `docs/releases/v0.4.8.md`;
- `ROADMAP.md`'s version table has no `v0.4.8` row, and its current baseline is
  still v0.4.7.

`tools/doc_check.py check` therefore fails on clean `main`, verified 2026-09-07
by stashing all local changes:

```
ROADMAP.md: git holds v0.4.8, but no row of the version table marks v0.4.8
completed; a release that shipped is one this table has to name
```

**Why it matters, and why it is P1 despite changing no displayed value.** Main
had been red for six merges on the `PL-0GTC`/`PL-SR8F` verify replay; `#432`
fixed exactly that and run 1548 went green at 17:11. This puts it straight back
to red on the next push, for a different reason, and the gate that is red for
two unrelated reasons in one afternoon is the gate a session learns to skim -
which is the failure mode `CLAUDE.md` names when it says a check that fires
without changing a decision is a defect in the check.

It also leaves the release train describing something untrue. A tag is what
`bin/docket release` reads to decide whether the previous release shipped, so
`v0.4.8` existing means the *next* cut will believe 0.4.8 already went out and
number itself accordingly, while nothing in the tree records what 0.4.8 was.

**This is a decision rather than a fix, and it is the project owner's**, because
both routes need a tag operation and a session cannot push tag refs here
(`PL-N936`).

1. **Delete the tag, then cut 0.4.8 properly.** `git push origin :refs/tags/v0.4.8`,
   then `make release VERSION=0.4.8` with its `ROADMAP.md` row and baseline, then
   re-tag at that merge commit. Leaves the train correct and the notes describing
   the nine-plus items that have accumulated since 0.4.7. Costs one destructive
   remote operation.
2. **Cut 0.4.8 and let the tag stand where it is.** Cheaper, and wrong in a way
   that is permanent: the tag would sit *behind* the commit that cut the release
   it names, so `git describe --contains` would place the release's own cut
   outside it and the notes would list work the tag does not span. `PL-028F` is
   already open on exactly this class of mismatch - work inside a tag's span but
   absent from its notes - so this route creates a second instance of a defect
   already filed.

Route 1 is recommended. Route 2 is recorded so the cheaper option is visibly
considered and rejected rather than silently skipped.

**How it probably happened, stated as a guess and not as a finding.** The
v0.4.7 cut (`PL-H1GH`) ended with three tag commands for the owner to run, and
v0.4.7 was tagged correctly at `888c1f4`. A second tag at the next number,
pushed onto the next merge, is the shape of those commands being re-run with the
version incremented. If that is right, the durable fix is that the tag step
should name the commit the release was cut at rather than `origin/main`, whose
meaning moves - worth considering when this is resolved, and filed here rather
than separately because it is the same event.

**Decision needed.** Which of the two routes above, and it is the project
owner's alone because both need a tag push that a session cannot make
(`PL-N936`). Route 1 - delete `v0.4.8`, cut the release properly, re-tag at the
cut's own merge commit - is recommended. Route 2 - cut 0.4.8 and leave the tag
where it is - is cheaper and leaves the tag permanently behind the commit that
cut the release it names.

**Done when.** `tools/doc_check.py check` passes on clean `main`: either
`v0.4.8` no longer exists and the next release is cut under its own number, or
a v0.4.8 release has been cut with its version-table row, its baseline section
and its `docs/releases/v0.4.8.md`, and the tag agrees with it.

**Found 2026-09-07** by `tools/doc_check.py` while closing `PL-JX0Z`, and
confirmed against clean `main` rather than against a working tree carrying local
edits.
