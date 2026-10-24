---
id: PL-TL6T
title: Sessions ask the owner to delete branches that are already gone: rule 14 lists remote branches to delete with no qualifier, and tools/branch_sweep.py's dry run reads this clone's unpruned tracking refs, so a pull request's own branch, which GitHub deleted at merge, shows as kept inside the 72 h grace period
priority: P2
effort: S
status: done
classes: defect
touches: tools/branch_sweep.py, .claude/rules/instruction-writing.md, .claude/skills/docket/modes/capture.md, tests/unit/test_branch_sweep.py
added: 2026-10-24
closed: 2026-10-24
pr: 1745
payoff: a closing block never asks the owner to delete a branch GitHub already deleted or one the daily sweep will delete on its own
verify: uv run pytest -q tests/unit/test_branch_sweep.py
---

**Problem.** Sessions ask the owner to delete branches that are already gone: rule 14 lists remote branches to delete with no qualifier, and tools/branch_sweep.py's dry run reads this clone's unpruned tracking refs, so a pull request's own branch, which GitHub deleted at merge, shows as kept inside the 72 h grace period

**The owner asked on 2026-10-24:** "Why do all these sessions suddenly start
asking me to delete branches again?" `PL-4X5B`'s session was one of them. Its
closing block told the owner that `claude/pl-4x5b-name-layout-literals` could
be deleted, without checking that the branch still existed. It did not.

**Measured 2026-10-24, about 20:40 UTC.** Three things combine:

1. `git ls-remote --heads origin` listed 7 heads: `main` and 6 `claude/`
   branches. `claude/pl-4x5b-name-layout-literals` was not among them. Its
   pull request, `#1741`, had merged minutes earlier, and GitHub deletes a
   pull request's branch when it merges.
2. In the same clone, `python3 tools/branch_sweep.py` reported 14 `claude/`
   branches and kept 12. At least 6 of the 12 no longer existed on the remote,
   `claude/pl-4x5b-name-layout-literals` among them. The sweep lists branches
   with `git for-each-ref refs/remotes/origin/`, and `fetch_remote` never
   prunes, by design, so a session's clone keeps a tracking ref for every
   branch deleted since it started. In CI the clone is fresh, so the daily job
   is not affected. Only the dry run that the housekeeping mode tells a session
   to run is.
3. The sweep keeps any branch whose last commit is less than 72 hours old
   (`GRACE`). So a session that has just merged its pull request sees its own
   branch as kept. The rule says to hand the owner "only a branch the sweep
   keeps that should go anyway", and a merged branch looks like exactly that.

**Why it got worse today (inferred, not counted).** Until `#1718`
(`PL-Z90G`, merged 2026-10-24), the resident `CLAUDE.md` housekeeping bullet
said that the daily sweep deletes finished branches. `#1718` moved that
sentence to `.claude/skills/docket/modes/capture.md`, which a session closing a
pull request does not read. What stayed resident is rule 14's clause, "a list
of remote branches to delete stays in the reply", which carries no
qualifier. No count of asks before and after `#1718` was taken.

**What a fix probably needs, for the session that takes it.** The dry run
should check each branch against `git ls-remote` before it reports it, or
should say that it reads local refs. Rule 14's clause should say that a reply
names no branch unless `git ls-remote` shows it still exists and the sweep
keeps it for a reason other than the grace period. Both are apparatus changes.
The generator pause does not apply, because this fixes a defect in a mechanism
that exists.

**Generator check.** None recorded. The defect produces repeated asks in
replies, not new items. The fact it misreads is which branches the remote
still holds, which the sweep's dry run reads from this clone's tracking refs.
