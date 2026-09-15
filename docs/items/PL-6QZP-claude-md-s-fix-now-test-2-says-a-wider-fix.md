---
id: PL-6QZP
title: CLAUDE.md's fix-now test 2 says a wider fix fails the touches audit, but under verify --self that check reports and the branch still ACCEPTs, so the deterrent the rule describes does not fire on a session's own branch
status: untriaged
added: 2026-09-15
---

**Problem.** CLAUDE.md's fix-now test 2 says a wider fix fails the touches audit, but under verify --self that check reports and the branch still ACCEPTs, so the deterrent the rule describes does not fire on a session's own branch

**Found 2026-09-15**, in `PL-7XTS`'s close-out doc sweep, as a second-order
consequence of `PL-69JZ` (the `--self` mode) plus `PL-7XTS` (routing the
close-out to it).

`CLAUDE.md`'s fix-now rule, test 2, reads:

> **It touches no file outside what the current item's work already touches.**
> `bin/docket verify` reads the diff for files outside an item's declared
> `touches`, so a wider fix either fails that audit honestly or tempts the
> single edit that defeats it.

The disjunction is the rule's whole deterrent, and its first branch no longer
happens where the rule is actually applied. A session using the fix-now door is
by definition working its own branch, so the audit it will run is
`bin/docket verify --self <id>` - which `PL-7XTS` now routes the close-out to
directly. In that mode `diff stayed inside touches` is an advisory: it prints
`NOTE`, names every path, and the verdict is still `ACCEPT`
(`subprojects/docket/src/docket/verify.py`, `advisory=self_audit`). A wider fix
therefore does not "fail that audit honestly" on the only branch the rule
governs.

**What the sentence should say instead is the open question**, and it is
narrower than rewriting the rule. The cap of two per branch and the three tests
are untouched; what is wrong is one clause's claim about what the tool does.
The honest replacement is that the audit *reports* the outside paths by name,
on a branch whose verdict is still `ACCEPT` - which makes the record visible to
a reader rather than refused to the session, and puts the whole weight of test
2 on the session obeying it. That may be the right rule anyway; it is not what
the sentence currently says.

Resident text, so the edit costs a cached prefix - worth batching with any
other `CLAUDE.md` change rather than taken alone.
