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

**Read PL-ZQ9C first.** PL-ZQ9C (record an item's pull request, so provenance
survives squash-merge) replaces the `commit:` field this check validates,
because PL-S4M2 switches main to squash-merge and the recorded branch hash
will no longer reach main. Building this check against `commit:` first means
building it twice. The two are probably cheapest done together.

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

**Approach.** An *error* where git can answer, silent where it cannot (this
supersedes an earlier draft here that made it advisory; PL-B043's decision
settled that a condition decidable from the tree belongs in `docket check` as
an invariant rather than as advice). `vcs.py` already collapses every git
failure to "nothing known" so the session-start digest works in a checkout
without git, without a remote, or without network - the same must hold here,
or `docket check` stops working in exactly the bare-checkout case it was built
to survive. So: if git is unavailable, say nothing; if it answers and a
recorded hash is unreachable, fail. All 32 recorded hashes are reachable
today, so turning this on costs nothing and keeps a clean condition clean.

**Reachability, not mere presence** (folded in from PL-JL24). `git cat-file -e`
succeeds for any object still in the local object database, including a commit
orphaned by an amend or a reset and reachable only through the reflog. A
presence test therefore passes locally on exactly the hashes this check exists
to catch - it passed on the orphan that closing PL-G3TG produced. Test
reachability from any ref (`git rev-list --all`, or equivalent) rather than
`cat-file -e`.

This supersedes an earlier line here that said not to report a hash which
resolves but is unreachable. That caution was aimed at the *noisy* form of the
question - `git merge-base --is-ancestor <hash> HEAD` - which flags legitimate
work sitting on an unmerged branch. Reachability from any ref does not: a
commit on an unmerged local branch is reachable, a true orphan is not. The
noise came from choosing HEAD as the reference point, not from asking about
reachability at all.

**Note on the underlying trap** (from PL-JL24). Recording a hash by amending
cannot converge - amending to write the hash changes the hash. An item's
`commit:` has to be written in a follow-up commit, or name the merge commit.

**Done when.** `docket check` reports each `done` item whose recorded commit
does not resolve, stays silent when git cannot answer, and has tests covering
a resolvable hash, an unresolvable one, an orphaned commit that `cat-file -e`
would accept, and a repository with no git at all.
