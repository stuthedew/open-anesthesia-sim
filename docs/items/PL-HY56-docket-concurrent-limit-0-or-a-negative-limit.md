---
id: PL-HY56
title: docket concurrent --limit 0 or a negative limit offers a one-item batch instead of refusing the value, the off-by-one PL-RMN8's brief recorded and left outside its done-when
status: untriaged
added: 2026-09-26
---

**Problem.** docket concurrent --limit 0 or a negative limit offers a one-item batch instead of refusing the value, the off-by-one PL-RMN8's brief recorded and left outside its done-when

**Found 2026-09-26** while closing `PL-RMN8` (next refuses a `--limit` below
one). On `origin/main` at `cfa51ff3` plus that branch, `bin/docket concurrent
--limit 0` and `bin/docket concurrent --limit -1` both print "A batch that can
be worked at once (1 items, best-first)" at exit 0. `PL-RMN8`'s brief noted
this as "off by one rather than false" and scoped only `next`, whose `--limit`
now goes through `cli._at_least_one`; `concurrent`'s is still a bare
`type=int, default=None`.

**Why it matters.** A zero or negative count cannot be honoured, and answering
one with a batch of one reads as a real answer. Lower stakes than `next`'s,
since the output is never "nothing to do".
