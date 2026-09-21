---
id: PL-BXNH
title: Recover the four squash-commit bodies lost on origin/main, newest #822, before the pull requests can be edited or the reasoning becomes unretrievable
priority: P3
effort: S
status: done
classes: housekeeping
milestone: v0.5.1
touches: docs/pr-bodies
added: 2026-09-21
closed: 2026-09-21
pr: 851
payoff: the reasoning behind four merged changes is in the checkout rather than only on the forge, where it can still be edited
verify: ls docs/pr-bodies/818.md docs/pr-bodies/820.md docs/pr-bodies/821.md docs/pr-bodies/822.md
---

**Problem.** Recover the four squash-commit bodies lost on origin/main, newest #822, before the pull requests can be edited or the reasoning becomes unretrievable

**Done 2026-09-21** in the session that filed this, at the project owner's
request. `python3 tools/pr_body_check.py --recover` fetched all four from the
public API and wrote them under `docs/pr-bodies/`:

| pull request | file | size |
| --- | --- | --- |
| #822 | `docs/pr-bodies/822.md` | 1,983 chars |
| #821 | `docs/pr-bodies/821.md` | 3,074 chars |
| #820 | `docs/pr-bodies/820.md` | 5,205 chars |
| #818 | `docs/pr-bodies/818.md` | 6,282 chars |

`python3 tools/pr_body_check.py` prints nothing afterwards, which is its clean
state. Filed before the work rather than after, per `CLAUDE.md`'s rule that
repository work no item names is filed first so every in-flight guard can see
it - all of which match a `PL-` id.

**Why it matters.** A squash merge writes the pull request body into the commit
message, and this repository's bodies carry the reasoning behind the change -
what was considered, what was refused, what the measurement was. When that body
is lost on the way to `origin/main`, the reasoning survives only in the forge,
which is editable and is not part of any checkout. Recovering it before anyone
edits the pull request is the only window in which the recovered text is
certainly the text that was merged.

**Done when.** The four bodies are under `docs/pr-bodies/` on the default branch
and `python3 tools/pr_body_check.py` prints nothing for them.

**Verified closed 2026-09-21.** All four files are on `main`. Two *newer*
squash commits have since lost their bodies - the session-start digest names
`#849` as the newest - which is the same mechanism recurring rather than this
item reopening; that recurrence belongs to whichever item holds the mechanism,
not here.
