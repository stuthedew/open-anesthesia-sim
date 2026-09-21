---
id: PL-BXNH
title: Recover the four squash-commit bodies lost on origin/main, newest #822, before the pull requests can be edited or the reasoning becomes unretrievable
status: untriaged
added: 2026-09-21
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
