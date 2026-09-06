---
id: PL-0SCG
title: GitHub Support ticket 4733783 is open: pre-rewrite blobs may still be reachable through refs/pull/*/head after the copyright purge, and nothing tracks it
priority: P2
effort: S
status: ready
classes: docs, infra
feature: provenance
touches: docs/items, docs/references
added: 2026-09-06
not-delegable: whether GitHub has dereferenced the pull refs is a fact about a third party's servers rather than about this tree, so no command run here can be made to fail before the work and pass after; and if the ticket is declined, what the project does about a permanent partial exposure is the project owner's call
---

**Problem.** `PL-SHG5` (two publisher-copyright full texts redistributed from
the now-public repository) is closed: the two PDFs are gone from `origin/main`
and from its history, `docs/references/README.md` states the repository's
actual visibility, and `tools/doc_check.py`'s `_check_reference_files_exist`
now guards the directory. One thread it opened is not closed, and closing
`PL-SHG5` would have been the only place it was written down.

`git filter-repo` and the force-push rewrote every branch and tag, but
`refs/pull/*/head` are read-only to the repository owner. `PL-SHG5` records
roughly 388 of them still pinning pre-rewrite commits, which is why GitHub
Support ticket 4733783 was raised on 2026-09-06: it asks GitHub to dereference
or remove those refs, run a server-side garbage collection, and purge cached
commit and blob views. Nothing local can do any of that, and nothing in the
repository reports whether it has happened.

**Why it matters.** While those refs resolve, the two works the purge existed
to remove are still fetchable from this public repository by anyone who knows a
commit hash — the rewrite reduced the exposure rather than ending it. It is
also the half nobody will notice closing: a support ticket resolves silently,
and the state that would prove it is on GitHub's servers rather than in any
file `make check` reads.

**Where.** GitHub Support ticket 4733783. `docs/references/README.md`, whose
"Redistribution" section is where the outcome belongs once it is known.
`PL-SHG5` carries the full account of the breach and the rewrite.

**How to check the current state.** Read it rather than recalling it — the
ticket may have been actioned since this was written:

```sh
git ls-remote origin 'refs/pull/*/head' | wc -l
git fetch origin refs/pull/370/head && git ls-tree -r --name-only FETCH_HEAD -- docs/references/
```

A pull ref that no longer resolves, or one that resolves to a tree with no
`baker-farmery` or `schuttler-schwilden` PDF, is the ticket having landed.

**Done when.** Either the pre-rewrite blobs are confirmed unreachable through
`refs/pull/*/head` and `docs/references/README.md` records that the exposure is
closed and when; or GitHub has declined, and the project owner's decision about
a permanent partial exposure is recorded there instead.

**Found.** Triage, 2026-09-06, while closing `PL-SHG5` — its three "Done when"
clauses were all satisfied on `origin/main`, and this was the one live thread
its closure would have dropped.
