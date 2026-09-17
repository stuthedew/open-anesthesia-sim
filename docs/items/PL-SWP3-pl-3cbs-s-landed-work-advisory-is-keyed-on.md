---
id: PL-SWP3
title: PL-3CBS's landed-work advisory is keyed on verify: and scoped to ready/needs-decision, so an item captured and worked in the same commit is structurally invisible to it: #635 left PL-0J9K and PL-MMVF untriaged with their code on main
status: untriaged
feature: queue-hygiene
added: 2026-09-17
---

**Problem.** PL-3CBS's landed-work advisory is keyed on verify: and scoped to ready/needs-decision, so an item captured and worked in the same commit is structurally invisible to it: #635 left PL-0J9K and PL-MMVF untriaged with their code on main

**What was found.** `PL-3CBS` (done, v0.2.8) built the advisory that reports an
open item whose work has already landed. It is keyed on `verify:` — "the item's
own statement of what would prove it done" — and scoped to `ready` and
`needs-decision` items carrying one. That key was chosen on a measurement and
the measurement was right: the obvious alternative, an item id at the head of a
merged commit subject, was 85% false positives (eleven of thirteen such ids on
`main` were capture or triage commits).

**The blind spot is the shape the key cannot reach.** An item captured *and*
worked in the same commit never passes through `ready`, so it never acquires a
`verify:` command, so it can never be a candidate. Both of the check's scoping
clauses exclude it, independently.

**The instance, verified 2026-09-17 against `origin/main`.** `#635` (`ff4be61`,
"PL-XD3C, PL-MMVF, PL-0J9K: make digest's git calls measurable, then cut them by
half") *added* six item files and landed 385 lines of
`subprojects/docket/src/docket/vcs.py` in one commit. `git cat-file --batch`
(`PL-0J9K`'s ask) is at `vcs.py:313` and `GitRunner`'s memo (`PL-MMVF`'s ask) is
at `vcs.py:174`. Both item files still read `status: untriaged` on `main`.

**What it cost, rather than what it could cost.** Both items appeared in
`bin/docket triage`'s untriaged list and in this session's own review of it, and
were recommended to the project owner as live work on a four-item branch. The
correction came from reading `vcs.py`, not from any check. A session had already
been started on that branch when the error was caught.

**Why the capture-and-work shape is common here rather than exotic.**
`CLAUDE.md` asks a session that diagnoses a cluster to file it in one call
(`docket new --feature ...`) and permits fixing what its three-test door admits
in the same branch. A commit that files five items and implements two is
therefore the encouraged shape, not an aberration — which is what makes this
worth a check rather than a one-off correction.

**Do not re-propose the commit-subject signal.** `PL-SRCP` was dropped as a
duplicate of `PL-3CBS` partly for proposing it, and the 85% figure is why. A
candidate key worth measuring instead: an *open* item whose file was **added**
by a commit that also changed a non-`docs/items/` path, which is decidable from
one `git log --diff-filter=A` and does not depend on the subject line at all.
Count its false-positive rate before building it — `CLAUDE.md`'s "name the
number that would change your mind, then go and count it" applies, and the
number here is what fraction of captured-and-worked commits actually finished
the item versus merely started on it.

**Not a defect in `PL-3CBS`.** Its check is sound within its scope and its key
was chosen correctly on evidence. This is the residual it did not cover.

**Where.** `subprojects/docket/src/docket/checks.py`, beside the advisory
`PL-3CBS` added.

---

## The counts this item asked for, run 2026-09-17 against `origin/main`

Three keys were measured, not one. **The key this item proposed is dead, and so
is the check it proposed building.** What survives is narrower than both, and it
belongs somewhere else. Numbers first, because the conclusion rests on them
rather than on the argument.

### Key 1 — the one this item named: open item, file **added** by a commit that also changed a non-`docs/items/` path

**248 of 319 open items match (78%).**

This is not a signal. It is a description of how this project commits, which is
the thing the item's own § "Why the capture-and-work shape is common here"
predicted and then did not apply to the proposed key. `PL-024` and `PL-027` match
because their files were added by `4bfa604` ("Add docket, a standalone queue for
memory-less sessions"), which changed 38 paths and worked neither of them. The
key cannot separate *the commit worked this item* from *the commit was doing
something else and filed this while it was there* — and the second is the
overwhelmingly common case, by construction.

Measured again where it would actually be read, on the live untriaged list:
**10 of 11 untriaged items match.** A mark on ten of eleven rows is not a mark.

### Key 2 — add the clause the item forbids: **and the commit's subject names this id**

**6 of 319 open items match.** All six were read in full; **none is an item that
should have closed:**

| id | status | why it is not landed work |
| --- | --- | --- |
| `PL-1T6T` | needs-decision | a re-test the commit captured as a follow-up; nothing of it landed |
| `PL-2XM2` | needs-decision | its own brief says "**Partly fixed in this session**" — the remaining reorder is the item |
| `PL-38PN` | ready | stale line citations in two *other* items; unrelated to `2edf43d`'s work |
| `PL-SVRW` | ready | its brief says "Found while making `vcs.leading_ids` public" — a finding, not the work |
| `PL-XD3C` | ready | `not-delegable` says what remains is one measurement on the owner's own clone |
| `PL-Y4YX` | needs-decision | captured by a triage commit |

**0/6 precision today.** The reason the forbidden clause does not rescue the key
is that sessions lead a subject with the ids they *captured and triaged* as
readily as with the ids they worked, so "the subject names it" does not mean
"the commit did it".

### Key 3 — Key 2 replayed over all history, scoped to `untriaged` at the moment of firing

**22 firings.** Adjudicating them by script gives **6/22 = 27% precision**, and
that adjudication is itself wrong in both directions, which is the finding rather
than a caveat:

- it scores `PL-0J9K` and `PL-MMVF` — the two genuine instances this item was
  filed for — as **false**, because the commit that later triaged them
  (`075f054`) touched one code path;
- it scores `PL-1T6T` and `PL-2XM2` as **true**, which reading them refutes.

No refinement of the script fixes this. Whether a commit that both filed an item
and changed code *finished* that item is not a property of the diff. It is a
relation between the item's intent and the diff's content, and the identical
commit shape — *N* item files added, *M* code paths changed, ids in the
subject — is produced by work finished, work started, a finding captured while
doing adjacent work, and a triage pass. **This is `CLAUDE.md`'s "do not script
the judgment" arriving as a measurement rather than as a principle.**

### What the numbers do support

Key 2, scoped to `untriaged`, delivered **as an annotation on `bin/docket
triage` rather than as an advisory on `docket check`**, and saying what the
commit *did* rather than what the item *is*:

```
PL-0J9K  git cat-file --batch for the digest's per-blob fan-out
  Filed by ff4be61 (#635), which also changed subprojects/docket/src/docket/vcs.py
  (+385). Read it before triaging: the work may already be on main.
```

Why this and not the check the item proposed:

- **It is silent unless the shape occurs.** 0 of 11 rows on the current list;
  22 firings across the store's whole life. Key 1 would mark 10 of 11, and a
  `docket check` advisory built on Key 2 would carry six standing false
  positives forever — `CLAUDE.md`'s "a check that fires every run without
  changing a decision is a defect in the check", met exactly.
- **It summarizes rather than decides**, which is the only honest disposition
  given Key 3. It hands the reader the commit and the path; the judgment stays
  theirs. `CLAUDE.md`: "Printing the few lines a decision needs … is the same
  win as answering the question outright."
- **It arrives at the moment of the error.** #635's correction came from reading
  `vcs.py`; the annotation puts that read *before* the recommendation instead of
  after it.
- **It fits the existing surface.** `render.py:989-995` already carries
  per-item triage annotations of this shape (`IN FLIGHT on …`, `Its file is
  already edited on …`), so this is one more line in a list that has them.

The cost is one `git log --diff-filter=A` over `docs/items/` plus one
`git show --name-only` per untriaged item, on a command that already reads the
whole store.

**Precision is the wrong measure for an annotation** and the right one for an
advisory, which is the whole of why the disposition moved. An advisory claims
the item has landed; this claims only that the commit which filed it also
changed code, which is true by construction every time it prints.

### Open question for the project owner

Whether to build the annotation at all, given that what it buys is a pointer
rather than an answer, and that the shape recurs roughly 22 times across ~1,180
items filed. Recorded rather than decided here: the deliverable differs
materially from the check this item describes, so it is the owner's call.

`PL-6TN8`, the first row of the current untriaged list, is the same failure
recurring under a different key — `PL-3DC7` was set `ready` with a `verify:`
command naming a test that did not exist, for behaviour already on `main` — so
the underlying hazard is live and is not confined to the capture-and-work shape.
