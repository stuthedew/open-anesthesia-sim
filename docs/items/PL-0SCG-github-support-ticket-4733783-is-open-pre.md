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

**GitHub Support replied, 2026-09-12** on ticket 4733783, shown to the session
by the project owner. This is the disposition the item was waiting for, and it
is an intention rather than a completed action - Support says confirmation will
follow.

**What they found.** Their tooling located references to the sensitive commit
SHA in 90 pull requests: `297` through `386` inclusive.

**What they will do.** *"Based on your request, we will just delete their
internal references, which will make the diffs and the sensitive data
inaccessible, but preserve the comment history."*

**What that leaves.** The exposure this item records - pre-rewrite blobs
reachable through `refs/pull/*/head` after the copyright purge - is confirmed
real rather than suspected, and is being closed by GitHub rather than by
anything this repository can do. Measured the same day, before the purge ran:
all 90 of `297..386` still had a `refs/pull/<n>/head` on the remote, out of 500
pull heads in total.

**Still owed before this can close:** a re-check that the 90 head refs no longer
resolve, and Support's confirmation.

**`status: ready` is now correct, and earlier sessions arguing otherwise were
right about the old state rather than this one.** While the ticket was an
open-ended wait, this item was unstartable and `bin/docket next` could hand a
legal-exposure item to a session with no move available - which is what
`PL-JTXX` records. Support's reply ends that: the remaining work is a bounded
check any session can run in one command, against a named range.

```text
git ls-remote origin 'refs/pull/*/head' | sed -E 's#.*refs/pull/([0-9]+)/head#\1#' \
  | awk '$1>=297 && $1<=386' | wc -l
```

Measured 2026-09-12, after Support's reply and before the purge ran: **90**, so
not yet. When that reads 0 the exposure is closed and this item is done. Until
then a session picking it up learns the answer and puts it down again, which is
cheap and correct rather than a dead end. `PL-JTXX` (this item is status ready
but waits on a third party) should be dropped on those grounds rather than
worked.

**One consequence outside this item**, recorded because nobody would look for
it here: the purge takes `refs/pull/312/head`, which `PL-VV4D` had recorded as
a test vector for the exact left-behind check. `PL-LF2C` carries that, and
`PL-R808` has been amended.
