---
id: PL-68XK
title: Check that every recorded commit hash resolves in the repository
priority: P2
effort: S
status: ready
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_checks.py
added: 2026-08-25
---

**Problem.** `docket check` requires a `done` item to record a `commit`, but
never checks that the hash names a commit that exists. Cutting v0.2.3 found
two that do not: PL-001 recorded `3749588` and PL-008 recorded `2484611`,
neither resolvable by `git rev-parse`. Both were carried in from the
single-file punch list, written against a history that was later rewritten,
and both survived the provenance repair in `547d9ac` because that pass
corrected which *release* an item shipped in without checking the hashes
themselves. The real commits are `94fa01d` and `de5cd97`; they were recovered
by hand from commit subjects and a "Closes PL-008" line, and are now recorded.

**Why it matters.** A `done` item's commit is the whole of its traceability -
it is how a reader gets from "the interface rounds to two decimals" to the
reasoning that chose two. An unresolvable hash fails silently and reads as
provenance, which is worse than an empty field, and it propagates: the
generated release notes cite the same hash, so a broken reference ships. This
is decidable by reading the repository, which is where `CLAUDE.md` says the
work belongs.

**Where.** `subprojects/docket/src/docket/checks.py`, using
`subprojects/docket/src/docket/vcs.py`'s existing `_run_git` helper.

**Approach.** An *advisory*, not an error, and only when git can answer.
`vcs.py` already collapses every git failure to "nothing known" so the
session-start digest works in a checkout without git, without a remote, or
without network - the same must hold here, or `docket check` stops working in
exactly the bare-checkout case it was built to survive. So: if git is
unavailable, say nothing; if it answers and a hash does not resolve, report it
for a person to look at. Do not report a hash that resolves but is unreachable
from any branch, which is a different and much noisier question.

**Done when.** `docket check` reports each `done` item whose recorded commit
does not resolve, stays silent when git cannot answer, and has tests covering
a resolvable hash, an unresolvable one, and a repository with no git at all.
