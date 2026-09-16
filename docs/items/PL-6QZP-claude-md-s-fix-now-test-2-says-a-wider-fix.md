---
id: PL-6QZP
title: CLAUDE.md's fix-now test 2 says a wider fix fails the touches audit, but under verify --self that check reports and the branch still ACCEPTs, so the deterrent the rule describes does not fire on a session's own branch
priority: P2
effort: S
status: needs-decision
classes: defect, docs
feature: worker-instructions
touches: CLAUDE.md
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

**Why it matters.** Test 2 is one of the three gates on `CLAUDE.md`'s fix-now
door, and that door is granted on the strength of its gates: the rule's own
design note says the narrowness is what makes it safe to give a session at all.
The sentence tells a session the audit will *fail* a wider fix. On the only
branch the rule can ever apply to - the session's own, since a session using
the fix-now door is by definition working its own branch - it does not. So a
session reads a deterrent, relies on it, and the deterrent does not fire.

That is `CLAUDE.md`'s own first compounding-friction test, word for word: a
check passing while the guarantee it stands for is void. The bound on it is
that the audit still *reports* the outside paths - under `--self` they print as
`NOTE` with every path named - so the information reaches a reader even though
the refusal does not reach the session. Nothing is silently lost; what is wrong
is one clause's claim about what the tool does.

**Decision needed.** Whether test 2 keeps a deterrent or becomes an honest
description of an advisory. Two answers, and they are not equivalent:

- **(a) Past-tense the claim.** Say that the audit *reports* the outside paths
  by name on a branch whose verdict is still `ACCEPT`, which puts the whole
  weight of test 2 on the session obeying it and makes the record visible to a
  reader rather than refused to the session. A one-clause edit to resident
  text.
- **(b) Restore the refusal in the tool.** Have `verify --self` REJECT on paths
  outside `touches` where the diff carries a fix-now commit, so the sentence
  becomes true as written. This changes what `--self` means and re-opens the
  question `PL-69JZ` answered - the four commission checks are advisory under
  `--self` precisely because they fire by construction on a correct close-out.

The brief argues (a) may be the right rule anyway. That is the part needing a
decision rather than an assumption, and it is the project owner's: it decides
how much a session is trusted to police itself, which is direction rather than
fact.

**Done when.** The clause in `CLAUDE.md`'s fix-now test 2 states what
`bin/docket verify --self` actually does, under whichever answer is chosen, and
the choice and its reasoning are recorded here. Resident text, so the edit
costs a cached prefix - worth batching with any other `CLAUDE.md` change rather
than taken alone.
