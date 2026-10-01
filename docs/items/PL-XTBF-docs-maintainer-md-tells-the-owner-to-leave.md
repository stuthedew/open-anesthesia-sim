---
id: PL-XTBF
title: docs/maintainer.md tells the owner to leave auto-merge armed while a session fixes a held pull request's failed check, but bin/docket arm's hold tells that session to leave auto-merge off and disarm an armed one, so the fix may stall unarmed where the owner expects it to land
status: untriaged
touches: docs/maintainer.md, subprojects/docket/src/docket/arming.py
added: 2026-10-01
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
