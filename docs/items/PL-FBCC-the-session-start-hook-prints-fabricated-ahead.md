---
id: PL-FBCC
title: The session-start hook prints fabricated ahead/behind counts when no merge base resolves
priority: P2
effort: S
status: done
classes: defect
feature: dev-tooling
milestone: v0.2.8
touches: .claude/hooks/docket-digest.sh, tests/unit/test_docket_digest_hook.py
added: 2026-08-31
closed: 2026-08-31
pr: 109
verify: uv run pytest tests/unit/test_docket_digest_hook.py
---

**Problem.** `branch_state()` prints whatever `git rev-list --left-right
--count origin/main...HEAD` returns, without checking that the two refs share
history. Given an unrelated pair the command does not fail: it prints the size
of each side, which reads exactly like a real position.

**Why it matters.** The line exists to stop a session working from a stale
base or stacking commits on merged history, and both are read off those two
numbers. A fabricated "98 ahead" says the branch carries work it does not,
which is an argument against merging — in the very case the line was written
to catch.

**Corrected 2026-08-31, before any work.** This item was first filed claiming
the counts degenerate whenever `origin/main` advances past a shallow clone's
graft boundary. That is wrong, and the session that filed it caused the
symptom itself: it had run `git fetch --depth=1 origin
'+refs/heads/*:refs/remotes/origin/*'` by hand, which re-truncates
`origin/main` and destroys the ancestry the counts need. Nothing in the
repository runs a `--depth` fetch.

Measured on a constructed remote (20 commits, cloned `--depth=3`, remote then
advanced by 2):

| after | `git merge-base HEAD origin/main` | `rev-list --left-right --count` |
| --- | --- | --- |
| `git fetch origin` — what the hook runs | resolves | `2  0` — correct |
| `git fetch --depth=1 origin '+refs/heads/*:...'` | empty | `1  3` — fabricated |
| a later plain `git fetch origin` | empty | `1  3` — not repaired |
| `git fetch --deepen=100 origin` | resolves | `2  0` — repaired |

So the hook is correct under its own fetch, in a shallow clone, both before
and after `PL-64LS` widened that fetch to every branch tip. What survives is
the third row: the truncation is recorded in `.git/shallow`, so once a session
truncates its own clone every later reading is wrong for the rest of it.

**Weighed honestly.** The state is reachable only when something truncates the
clone, which no committed code does — so this guards against a session's own
future mistake rather than a live defect. It is worth what it costs and no
more: one `git merge-base` call at session start.

**Where.** `.claude/hooks/docket-digest.sh`, `branch_state()`.

**Done when.** `branch_state` asks `git merge-base HEAD origin/main` before
counting, and where that is empty says the clone cannot answer — naming a
`--depth` fetch as the cause and `--deepen` as the repair — instead of
printing numbers. The deepen-before-counting half of the original brief is
dropped: it would pay network on every session start for a state no committed
code produces.
