---
id: PL-FBCC
title: The session-start hook prints fabricated ahead/behind counts when no merge base resolves
status: untriaged
added: 2026-08-31
---

**Corrected 2026-08-31, before any work.** This item was filed claiming the
hook's counts degenerate whenever `origin/main` advances past a shallow
clone's graft boundary. That claim is wrong, and the session that filed it
caused the symptom itself: it had run `git fetch --depth=1 origin
'+refs/heads/*:refs/remotes/origin/*'` by hand, which re-truncates
`origin/main` to depth 1 and destroys the ancestry link the counts need.
Nothing in the repository runs a `--depth` fetch.

Measured on a constructed remote (20 commits, cloned `--depth=3`, remote then
advanced by 2):

| after | `git merge-base HEAD origin/main` | `rev-list --left-right --count` |
| --- | --- | --- |
| `git fetch origin` (what the hook runs) | resolves | `2  0` — correct |
| `git fetch --depth=1 origin '+refs/heads/*:...'` | empty | `1  3` — fabricated |
| a later plain `git fetch origin` | empty | `1  3` — not repaired |

So the hook is correct under its own fetch, in a shallow clone, both before
and after `PL-64LS` widened that fetch to every branch tip. The third row is
the one that still matters: the damage is recorded in `.git/shallow` and a
normal fetch does not undo it, so once a session truncates its own clone every
later reading is wrong for the rest of the session.

**What is left of the problem.** The hook prints whatever
`git rev-list --left-right --count origin/main...HEAD` returns without
checking that the two refs have a merge base. With no merge base the command
does not fail - it prints the count of each side of an unrelated pair, which
looks exactly like a real answer. A fabricated "98 ahead" tells a session it
is carrying work it does not have, which is an argument against merging, in
the case the line exists to catch.

**Why it matters, honestly weighed.** The state is reachable only when
something truncates the clone, which no committed code does - so this is a
guard against a session's own future mistake rather than a live defect. It is
worth what it costs and no more: one `git merge-base` call at session start.

**Where.** `.claude/hooks/docket-digest.sh`, `branch_state()`.

**Done when.** `branch_state` asks `git merge-base HEAD origin/main` before
counting, and where that is empty says the clone cannot answer - naming a
`--depth` fetch as the usual cause - instead of printing numbers. The
deepen-before-counting half of the original brief is dropped: it would pay
network on every session start to fix a state no committed code produces.
