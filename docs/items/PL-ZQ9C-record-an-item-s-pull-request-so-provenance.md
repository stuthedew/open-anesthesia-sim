---
id: PL-ZQ9C
title: Record an item's pull request, so provenance survives squash-merge
priority: P2
effort: M
status: done
classes: infra
feature: public-history
milestone: v0.2.8
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/release.py, subprojects/docket/tests, .claude/skills/docket/SKILL.md, subprojects/docket/README.md, ROADMAP.md, docs/items
added: 2026-08-30
closed: 2026-08-30
pr: 90
verify: uv run pytest subprojects/docket/tests -k pull_request && bin/docket check
not-delegable: the brief leaves the migration open between backfilling `pr:` from the merge subjects and carrying both fields, and either pass rewrites the provenance of every closed item
---

**Problem.** A `done` item records `commit:`, the branch commit that carried
the work. PL-S4M2 (switch main to squash-merge and gate every merge) will make
that hash name a commit that never reaches main and becomes unreachable the
moment the head branch is deleted. Every item closed afterwards would then
record provenance that resolves nowhere.

**Why it matters.** The recorded commit is the whole of an item's
traceability - it is how a reader gets from "the interface rounds to two
decimals" to the reasoning that chose two. PL-68XK exists precisely to stop a
hash that does not resolve from reading as provenance, and cutting v0.2.3
already found two such hashes carried in from the single-file punch list. Left
alone, the squash switch would manufacture that failure on every future item
rather than catching it.

**Where.** `subprojects/docket/`: the item schema, the `check` command, and the
README's item-format section. Plus a migration pass over `docs/items/`.

**Approach.** Record the pull request rather than the branch commit. The number
is known before the merge, it is stable, and GitHub's squash-merge appends it
to the commit subject on main by default (`Title (#71)`), so the link from a
main commit back to its pull request is free and the item closes the loop from
the other side. That also sidesteps the trap PL-JL24 recorded and PL-68XK
carries forward: a hash cannot be recorded by amending, because amending
changes the hash.

The check then becomes decidable from the tree with no network - for an item
with `pr: 71`, assert that some commit on main has `(#71)` in its subject.
Keep `vcs.py`'s existing discipline of saying nothing when git cannot answer,
so `docket check` still works in a bare checkout.

**Migration.** The 32-plus hashes already recorded stay valid and reachable -
they were merged with merge commits, so they are ancestors of main. Do not
rewrite them. Either carry both fields, with `commit:` frozen as historical
and `pr:` used going forward, or backfill `pr:` from the merge commit subjects,
which all carry `Merge pull request #N`. Prefer the backfill if it is clean;
prefer keeping both to rewriting anything.

**Refresh PL-68XK.** PL-68XK (check that every recorded commit hash resolves)
is `ready` and specifies a reachability test against `commit:`. A worker who
picks it up before this item lands will build a check against a field that is
being replaced. Its brief needs refreshing to validate `pr:` instead - or the
two need doing together, which is probably cheaper.

**Done when.** An item records the pull request that carried it, `docket check`
reports an item whose recorded pull request has no matching commit on main,
the existing recorded hashes still validate, and `subprojects/docket/README.md`
documents the field.


**Closed 2026-08-30**, retroactively: the work landed in pull request 90
(`55eedb6`) and the `status` was never moved off `ready`. Verified against the
"Done when" above rather than assumed - `Item.pr` exists and `docket check`
refuses a `done` item without it, `_check_provenance` holds every recorded
number to one the default branch has seen (passing over numbers above its
high-water mark, since an item is closed on the branch that carries it),
`commit` stays legal and is still checked for shape, and
`subprojects/docket/README.md` documents the field. This is the rule that
stopped PL-STNV being closed in the session that finished it, which is the
requirement working as designed. The gap that let this finished item sit open
is PL-3CBS (docket has no way to notice that an open item's work already landed
on main).
