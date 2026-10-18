---
id: PL-XTBF
title: docs/maintainer.md tells the owner to leave auto-merge armed while a session fixes a held pull request's failed check, but bin/docket arm's hold tells that session to leave auto-merge off and disarm an armed one, so the fix may stall unarmed where the owner expects it to land
priority: P2
effort: S
status: done
classes: defect
feature: arm-follows-owner
touches: docs/maintainer.md, subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_arming.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
closed: 2026-10-18
payoff: a session repairing a held pull request the owner has armed leaves it armed, so the fix lands where the owner expects it instead of sitting green and unarmed
verify: grep -qF 'armed it after reading' subprojects/docket/src/docket/arming.py
recurrences: 2026-10-17 PL-8TPV
---

**Problem.** Two instructions give a session opposite directions on the same
push.

- `docs/maintainer.md` § "Bring a stale base in when you merge, with Update
  branch" covers a check that fails after the owner's Update branch, on a pull
  request the owner has read and armed: "Leave auto-merge armed and ask a
  session to fix the branch; auto-merge lands it once the fix is green."
- `CLAUDE.md` has a session ask `bin/docket arm` "before every later push while
  a pull request is open". For that pull request it answers `hold`, since the
  pull request changes paths outside the store, the tooling and the records. The
  hold line `Verdict.lines` prints in `subprojects/docket/src/docket/arming.py`
  says "Leave auto-merge off, disarming it before the push that brings this if
  it is armed".

If a session obeys the printed line, it disarms the owner's auto-merge before
pushing the fix, and the pull request sits green and unarmed while the owner
expects it to land. If it follows `docs/maintainer.md`, it leaves auto-merge
armed and the fix lands unread. `docs/maintainer.md` accepts that, but nothing
on the session's side says so. `CLAUDE.md`'s arming bullet says "disarming it
before the push that brings the hold or green CI merges half the work". That
reads as aimed at the push that first makes a pull request held, not at a
repair to one the owner has already read and armed. The printed line draws no
such distinction.

**Found** 2026-10-01, while answering whether a session can still add to a pull
request once it is marked ready. No instance has been observed; this is a
reading of the two texts side by side.

**Decision for triage:** which side is right. Either an owner-armed held pull
request stays armed through a repair push, and the hold line says so, or the
repair disarms it and `docs/maintainer.md` tells the owner to re-arm once they
have read the fix.

**Why it matters.** Two carriers give a session opposite instructions for one push on the owner's merge path: obeying the hold line strands a green fix unarmed while the owner expects it to land, and obeying `docs/maintainer.md` lands a repair unread with nothing on the session's side saying that is intended.

**Done when.** `docs/maintainer.md` and the hold line `Verdict.lines` prints say the same thing about a repair push to a held pull request the owner has armed, per the answer recorded below the question.

**Decision needed.** Whether an owner-armed held pull request stays armed through a repair push. **Recommended: it stays armed**, and the hold line excepts a pull request the owner armed after reading. The owner has read and armed it, `docs/maintainer.md` already accepts the repair landing unread, and the alternative costs a second read and a re-arm on every repair. The cost is a session's repair reaching `main` unread, which that document accepts. The exception is prose, not a computed branch: a session's GitHub calls are the owner's, so the code cannot tell who armed it.

**Generator check.** The fact is whether an armed held pull request stays armed through a repair, stated oppositely by two documents; no head states it, and no instance has been observed. One-off.

**Decided** (2026-10-12, in the first batched design round, a session's call):
it stays armed, as recommended. The two carriers disagree about one decision
rather than posing a new one. `docs/maintainer.md`'s sentence came in with
`PL-6MW8` (`#977`, 2026-09-23), the decision `CLAUDE.md`'s base-merge bullet
records as (project owner, 2026-09-23, ratified), and the hold line came later
(`PL-KKHD`, 2026-10-03) without the exception, so the later carrier is the one
out of step and the fix is to make it agree. Its blast radius is one printed
line and one sentence of the owner's manual, which rule 14 of
`.claude/rules/instruction-writing.md` makes a session's. The form: the hold
line excepts a held pull request that is already armed - a session never arms
a held pull request, so one that is armed was armed by the owner after
reading, and the repair rides it, as `docs/maintainer.md` already says; where
`arm` cannot read whether auto-merge is on, the printed line carries the
exception as prose. A repair of two carriers that disagree is a defect in what
exists, so the pause on new workflow mechanisms does not hold it. Reopening
this is on ordinary evidence: a repair that landed unread and should not have.

**Built 2026-10-18.** The hold line now ends with the exception for a repair,
as decided. `arming.REPAIR_EXCEPTION` says that a pull request that already
held before this push and is armed was armed by the owner after reading it,
so the session leaves it armed and auto-merge lands the fix. A hold that a
claim makes keeps the draft line and names no repair, since the owner never
armed a draft. `docs/maintainer.md` now says that `arm` tells the session the
same. Three tests in the new `subprojects/docket/tests/test_arming.py` pin the
line's place after the disarm line, its absence beside a claim, and its
absence from an `arm` answer. They fail before the fix, where
`arming.REPAIR_EXCEPTION` does not exist.
