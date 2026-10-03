---
id: PL-6QZP
title: CLAUDE.md's fix-now test 2 says a wider fix fails the touches audit, but under verify --self that check reports and the branch still ACCEPTs, so the deterrent the rule describes does not fire on a session's own branch
priority: P2
effort: S
status: ready
classes: defect, docs
feature: worker-instructions
touches: CLAUDE.md
added: 2026-09-15
payoff: CLAUDE.md's fix-now test 2 stops promising a refusal the self-audit does not make, so a session reads the real rule: reported by name, obeyed by the session, refused only at a delegated review
verify: grep -qF 'names every file changed outside the item' CLAUDE.md
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

## Design round 2026-10-03: recommendation

**Re-checked against the tree, 2026-10-03.** The clause stands in `CLAUDE.md`
as quoted, 183 characters. `subprojects/docket/src/docket/verify.py` carries
the four commission checks with an `advisory` flag; under `--self` they print
`NOTE`, name every path, and the verdict stays `ACCEPT`, and `cli.cmd_verify`
closes a self-audit with the footer "the four commission checks reported
rather than refused. A delegated review runs without `--self` and refuses on
any of them." That mode was the project owner's answer on 2026-09-12
(`PL-69JZ` § "Answered 2026-09-12"; dated before 2026-09-16, so its kind is
unrecorded). The fix-now door is in use - seven commits on `main` since
2026-09-22 cite it - and a fix-now commit carries no marker: it leads with the
current item's id exactly as the item's own commits do, so the only signal a
tool can read is "outside `touches`", the signal `PL-69JZ` made advisory.
`PL-G424` (done 2026-09-19) left this member open deliberately: a claim about
what a command prints is judgment its route does not reach.

**Q. Does test 2 keep a deterrent (b), or become an honest description of an
advisory (a)?**
**Recommendation: (a).** The replacement clause, 221 characters against the
183 it replaces:

> `bin/docket verify --self` names every file changed outside the item's
> `touches` and still `ACCEPT`s, so a wider fix is reported, not refused:
> this test holds where the session obeys it, and a delegated review refuses
> it.

The resident set grows by 38 characters, and the payment is a false claim
exchanged for a true one, which the growth rule asks to be named rather than
avoided. The clause also names `--self`, which closes the first of the three
routes `PL-PFK1` lists to a bare `bin/docket verify` on a session's own branch.
The deterrent survives where it was always real - a delegated review refuses on
an outside path - and the self-audit is as it was decided: reported, by name,
on an `ACCEPT`.

**(b) is refuted on mechanism, not on trust.** With no marker on a fix-now
commit, "REJECT on paths outside `touches` where the diff carries a fix-now
commit" cannot be written; what can be written is "REJECT on any outside path
under `--self`", which re-opens `PL-69JZ`'s answer on the evidence it was
given to settle - the commission checks fire by construction on a correct
close-out whose `touches` was outgrown. The one sound way to restore a refusal
is **(c)**: a `Fix-now:` trailer on such commits, which would let `--self`
check the count of two and that each fix-now commit stays inside the files the
item's other commits touch. That is a new field and a new rule, with no
reported instance of a wider fix-now to pay for it, so it is recorded here as
the route if the owner wants the deterrent back, and not recommended now. The
trust question the brief raises is answered by picking (a) alone or (a) with
(c); (a) alone is this recommendation.

**Build.** One clause in `CLAUDE.md`, batched with any other `CLAUDE.md` edit
open at the time, since resident text costs a cached prefix per edit; the
`verify:` is a `grep -qF` for the new clause's opening words. Size S, as filed.

## Answers 2026-10-03

**Answered 2026-10-03: Q1 ratified: (a)** (project owner, 2026-10-03,
ratified, over (b), a refusal restored in `verify --self`, and over (c), the
`Fix-now:` trailer that would make such a refusal sound). The build replaces
the 183-character clause in `CLAUDE.md`'s fix-now test 2 with the
221-character clause quoted in the design round above, batched with any other
`CLAUDE.md` edit open at the time, and names the 38-character growth as a
false claim exchanged for a true one. (c) stays recorded as the route if the
deterrent is wanted back. Status moves to `ready` with this answer, as
`docket check` requires of a recorded answer.
