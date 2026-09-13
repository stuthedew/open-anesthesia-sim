---
id: PL-7XNX
title: The in-flight editing filter asks git once per edited item file, where one diff per ref would answer for all of them
status: untriaged
added: 2026-09-13
---

**Problem.** The in-flight editing filter asks git once per edited item file, where one diff per ref would answer for all of them

**Found while closing `PL-8MJ3`, 2026-09-13**, which added the read this
describes.

**Where.** `vcs.branches_in_flight`'s `edited` comprehension calls `_superseded`
once per edited item file, and each call is one `git diff --numstat`. `_superseded`
already takes a tuple of paths and asks git for all of them in one command, so the
per-item call is using a batching interface one path at a time.

**Why it matters, modestly.** It is on the hot path `PL-PMT7` just cleared: `next`
and the session digest both compute the flight report, and `PL-PMT7` removed the
duplicate computation to get `next` from 26 git subprocesses back to `flight`'s 13.
This adds one per edited item, which is typically nought to four and is bounded by
how many item files unmerged branches have touched - so it is small, and it is
also exactly the kind of cost that stops being small on a checkout holding many
stale refs.

**Approach.** Group the edited entries by ref and call `_superseded` once per ref
with all of that ref's paths, which is the shape it was written for. The result is
a set of superseded paths, so the grouping needs no change to `_superseded` itself.

**Not a correctness question.** The answer is identical either way; only the number
of subprocesses differs. Worth doing when something else is already in this
function rather than as a pass of its own.
