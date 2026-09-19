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
resolve, and Support's confirmation. (Re-checked 2026-09-19: 89 of the 90 are
gone and `refs/pull/298/head` is not - see the closing section.)

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

**Re-checked 2026-09-19, in `PL-6ZQY`'s crossing-lane sweep. The purge has
almost run, and the count above is stale: it reads 1, not 90.** The brief's own
command returns a single survivor, `refs/pull/298/head` →
`66279b3293728a7d34fd60a64b40ad85ad12c1c1`; refs `297` and `299..386` no longer
resolve. The total is now 628 pull heads rather than 500.

**That one ref still serves both works**, so the exposure is narrowed rather
than closed - confirmed against GitHub's contents API at `ref=refs/pull/298/head`,
path `docs/references`, which still lists
`baker-farmery-2011-inert-gas-transport-in-blood-and-tissues.pdf` (1,449,838
bytes) and `schuttler-schwilden-2008-modern-anesthetics-hep-182.pdf` (5,232,436
bytes). The local `git ls-remote` half is reproducible from any checkout; the
API half needs a token that can read the repository.

**So what is left is one ref and one sentence**, which is smaller than this
brief reads: ask Support to finish `298` - naming it, since their own list of 90
was worked through and this is the remainder - and then write the outcome and
its date into `docs/references/README.md`, whose account still ends at
`PL-SHG5` and records no exposure at all. Neither half is a session's to do
alone: the first is the project owner's ticket, and the second wants the date
the first lands.

**Measured exhaustively 2026-09-19, later the same day. The exposure set is
exactly one ref, and that is now established rather than inferred.** Every
previous count here, this brief's own commands included, took Support's list of
90 pull requests as the set to check. That was the set *Support* searched, not
the set that carries the works, and nothing had tested whether it was complete.
It is: all **631** pull heads on this repository were fetched and their trees
read, and `refs/pull/298/head` is the only one serving either work. Two further
facts fall out of the same scan, and both narrow what is owed:

- **No other ref of any kind reaches the pre-rewrite commit.** `git ls-remote
  origin` returns exactly one line for
  `66279b3293728a7d34fd60a64b40ad85ad12c1c1`, that pull head. The branch the
  pull request was opened from,
  `claude/unfiled-housekeeping-item-id-a36q1s`, is gone from the remote, and no
  tag resolves there. There is therefore nothing left for the project owner to
  delete: the one surviving path is the one kind of ref a repository owner
  cannot touch, which is why this stays Support's to finish.
- **Pull request 298 is the pull request that introduced both files** — `#298`,
  *"PL-JX2T: file the review-article PDFs as cited references, under
  docs/references/"*, merged 2026-09-04 — so its head commit is not a ref that
  happened to inherit the sensitive SHA but the commit that created it. That is
  worth saying in the ticket: it explains why this one is the remainder of
  Support's own 90 rather than an oversight, and it identifies the ref without
  ambiguity.

**A second finding from the same scan, recorded so nobody re-raises it as a
breach.** 101 pull heads, `387` through `487`, still carry
`docs/references/jugel-2014-m4-visualization-oriented-time-series-aggregation.pdf`.
That is **not** an exposure and needs no ticket: the M4 paper is CC BY-NC-ND
3.0 per the statement on its own first page, which permits verbatim
redistribution with attribution, so a public repository may carry it. Its
removal from `main` under `PL-8LXM` was a housekeeping decision — a paper
nothing then founded — never a licence one. Anyone repeating the scan below
without the name filter will see those 101 and should stop here.

**The commands recorded above this line are superseded.** Both the
`awk '$1>=297 && $1<=386'` count and the contents-API check have the same two
defects: they are bound to Support's range, so they cannot see a ref outside it,
and they test a *ref list* rather than what a ref's tree actually holds. This
one is range-free, reads trees, needs no token, and downloads no copyrighted
bytes — `--filter=blob:none` fetches commits and trees and no blobs, which is
what makes it safe to run from anywhere. Run verbatim 2026-09-19; it printed
`298`, and 4.2 MB was the whole transfer for all 631 refs:

```sh
git init -q --bare /tmp/pullscan && cd /tmp/pullscan
git remote add origin https://github.com/stuthedew/open-anesthesia-sim.git
git fetch -q --filter=blob:none --depth 1 origin 'refs/pull/*/head:refs/pulls/*'
for r in $(git for-each-ref --format='%(refname)' refs/pulls); do
  git ls-tree -r --name-only "$r" -- docs/references/ \
    | grep -qiE 'baker-farmery|schuttler-schwilden' && echo "${r#refs/pulls/}"
done
```

**Read the output, never the exit status** — the loop's status is the last
`grep`'s and means nothing. Printing nothing is the exposure closed; printing
`298` is the state on 2026-09-19. It is deliberately not wired into `make
check`: it needs the network, and once it goes quiet it would fire on nothing
for the life of the project, which is what `CLAUDE.md` § "A check earns its
place every run" refuses.

**The README half is done, ahead of the date it was waiting for.** The reasoning
above — that the sentence in `docs/references/README.md` wants the date Support
lands — held only for the *closing* sentence. What the section said in the
meantime was wrong today rather than merely incomplete: it read as though the
2026-09-06 removal had finished, and sent a reader to `PL-SHG5`, a closed item,
for "what remains". `docs/references/README.md` § "Redistribution" now records
the live state — the ticket, Support's undertaking, one ref of 631 as of
2026-09-19, and that both works are still fetchable by anyone holding the hash —
and points here for the ref and the closing date. So what is left is one ref and
one date, and the date replaces a sentence that is accurate in the meantime
instead of filling a silence.

**Still owed:** Support finishing `refs/pull/298/head`, and the closing date
written into that section.
