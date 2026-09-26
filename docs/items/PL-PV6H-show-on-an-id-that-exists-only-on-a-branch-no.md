---
id: PL-PV6H
title: show on an id that exists only on a branch no live hold names, such as a stranded capture the digest lists, still prints only 'no item matching', since PL-140X points at the branch only where a hold names the id
status: untriaged
added: 2026-09-26
---

**Problem.** show on an id that exists only on a branch no live hold names, such as a stranded capture the digest lists, still prints only 'no item matching', since PL-140X points at the branch only where a hold names the id

**Found 2026-09-26** while closing `PL-140X` (show names the branch holding an
item absent here). `PL-140X` scoped the pointer to an id a live hold names, and
`cli._say_held_elsewhere` stays silent otherwise, so the ordinary typo costs no
ref walk. On this checkout the session-start digest lists `PL-0T5X` and
`PL-7XGR` under "Only on a branch, not in this checkout", and `bin/docket show`
on either prints only `no item matching` and exits 1: no live hold names them,
so the new lines do not fire. `bin/docket stranded` is where they are read.

**Why it matters.** The digest names these ids and `show` is the command a
session reaches for next, so it is the same dead end `PL-140X` removed for held
ids. Whether the not-found path should pay a stranded read on every miss to
cover it is the judgment this item leaves to triage.
