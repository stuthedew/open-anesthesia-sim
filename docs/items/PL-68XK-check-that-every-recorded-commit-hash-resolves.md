---
id: PL-68XK
title: Check that a recorded commit hash resolves, now that it is the optional half of provenance
priority: P2
effort: S
status: ready
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_checks.py
added: 2026-08-25
---

**PL-ZQ9C has landed; this brief is written against what it left.** PL-ZQ9C
(record an item's pull request, so provenance survives squash-merge) made `pr`
the field a `done` item must carry and left `commit` optional beside it, and
PL-XCYB (a provenance check must refuse to answer in a shallow checkout, not
answer wrongly) built the machinery both checks need. So this item is no
longer "validate the field that makes a closure traceable" - `docket check`
already holds every recorded `pr` to a pull request the default branch names.
It is now the narrower job named in the title: a `commit` that is *present*
should still resolve, because a hash that leads nowhere reads as provenance
whether or not the item also carries a number.

**Problem.** `commit` is optional and unvalidated. 66 items carry one, and one
of them was wrong: PL-003 recorded `621d9a6`, which resolves in no clone at
all. PL-ZQ9C's backfill caught it only because deriving a pull request from
the hash forced the hash to be resolved, and repaired it to `e475823` from the
history of the item's own file. Nothing would have caught it otherwise, and
nothing would catch the next one. Two earlier instances - PL-001's `3749588`
and PL-008's `2484611` - were found by hand when v0.2.3 was cut; all three
were carried in from the single-file punch list, written against a history
that was later rewritten.

**Why it matters.** A hash that resolves nowhere fails silently and reads as
provenance, which is worse than an empty field. It is decidable by reading the
repository, which is where `CLAUDE.md` says the work belongs. The consequence
is smaller than it was before PL-ZQ9C - `pr` now carries the traceability, and
the generated release notes cite the pull request in preference to the hash -
so this is no longer the only thing standing between a reader and the
reasoning behind a closed item. It is a stale field that lies.

**Where.** `subprojects/docket/src/docket/checks.py`, alongside
`_check_provenance`, using `subprojects/docket/src/docket/vcs.py`.

**Approach.** Follow the shape `_check_provenance` already has rather than
inventing a second one. It takes what git knows as an argument
(`PullRequestHistory`) rather than shelling out, so `analyze` stays pure and
`check` is the only command that pays for the read; the same applies here.

An *error* where git can answer, and a recorded refusal where it cannot (this
supersedes an earlier draft here that made it advisory; PL-B043's decision
settled that a condition decidable from the tree belongs in `docket check` as
an invariant rather than as advice).

**A shallow checkout must decline, not fail** (this is why PL-XCYB paired with
PL-ZQ9C rather than with this item). Every hash recorded before the graft
point fails `git rev-parse --verify` in a shallow clone: eight of forty
sampled did, all of them real commits. Reuse `Report.declined` and the "Not
checked" section PL-XCYB added, so this check reports that it could not run
rather than reporting sound provenance as broken - and so the two provenance
checks decline for the same reason in the same words.

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

**The amend trap is no longer load-bearing** (from PL-JL24). Recording a hash
by amending cannot converge, because amending to write the hash changes the
hash - which is why `commit` was always written after the fact, and how a
wrong one gets in. PL-ZQ9C's `pr` is not subject to it: the number is
allocated before the merge, so it is written in the same commit as the
closure. Keep the note as the reason `commit` stays optional rather than being
tightened.

**Done when.** `docket check` reports each item whose recorded `commit` does
not resolve or is unreachable, declines with a reason in a shallow checkout
rather than failing, says nothing when git cannot answer at all, and has tests
covering a reachable hash, an unresolvable one, an orphaned commit that
`cat-file -e` would accept, a shallow checkout, and a repository with no git.
