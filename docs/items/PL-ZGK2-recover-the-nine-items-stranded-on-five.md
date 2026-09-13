---
id: PL-ZGK2
title: Recover the nine items stranded on five abandoned branches, and leave the four on a live session's branch
priority: P2
effort: S
status: done
classes: infra
feature: dev-tooling
milestone: v0.4.21
touches: docs/items/
added: 2026-09-13
closed: 2026-09-13
pr: 540
verify: bin/docket check && test $(ls docs/items/PL-4ZK8-* docs/items/PL-5NR5-* docs/items/PL-7B3G-* docs/items/PL-928V-* docs/items/PL-NJ9M-* docs/items/PL-Q664-* docs/items/PL-V67Q-* docs/items/PL-V9L3-* docs/items/PL-Z3V5-* 2>/dev/null | wc -l) -eq 9
---

**Problem.** Recover the nine items stranded on five abandoned branches, and
leave the four on a live session's branch.

`bin/docket stranded` reports thirteen item files that exist on no ref the
default branch has taken. Four of the thirteen are on
`origin/claude/determined-hamilton-atx5bi`, which is the branch of a session
that is running right now, and those are live work rather than a hole. The other
nine are on five branches nobody will merge.

**Why it matters.** A stranded item is a finding that has been made and paid for
and is now invisible to every session: `bin/docket next`, `status`, `gate` and
the digest all read the store on the default branch, so the work will be
rediscovered and re-reasoned from scratch. Two of the nine (`PL-V9L3`,
`PL-Q664`) were themselves captured *because* an earlier branch stalled, so the
mechanism has already demonstrated its own failure mode once.

**The judgment this item records, since the command cannot make it.**
`bin/docket stranded` says outright that it cannot tell a live branch from an
abandoned one and that the reader decides. The five recovered from, with the
evidence:

| Branch | Items | Why it is abandoned |
| --- | --- | --- |
| `claude/gate-items-zyfl0o` | `PL-4ZK8`, `PL-7B3G`, `PL-NJ9M` | last commit 2026-09-08; no session on the list |
| `claude/vibrant-curie-0x11e4` | `PL-5NR5`, `PL-Z3V5` | session archived |
| `claude/amazing-einstein-8gmfnz` | `PL-Q664`, `PL-V9L3` | session archived after a failure |
| `claude/optimistic-mayer-sx57dq` | `PL-928V` | session archived awaiting an artifact share |
| `claude/graph-y-scale-mac-percent-v-6ohg70` | `PL-V67Q` | last commit 2026-09-08; no session on the list |

Left alone: `PL-8GJ6`, `PL-LS3H`, `PL-QBKQ`, `PL-XWCY` on
`origin/claude/determined-hamilton-atx5bi`, whose session was `RUNNING` when
this was checked.

**Two things this item does not do.** It does not delete any of the five refs:
`.claude/hooks/no-prune-guard.sh` exists because a stale `origin/<branch>` can
be the only surviving copy of something, and recovering the file removes the
urgency rather than creating a reason to prune. And it does not triage the nine
- they land `untriaged`, as captures, which is where `bin/docket triage` can
reach them.

**Done when.** All nine files are on this branch, `bin/docket check` passes, and
the four on the live session's branch are untouched.

**What the recovery surfaced on the first `bin/docket check` after it, which is
the argument for having done it.** `PL-4QCJ` - an open item on the default
branch - names `PL-Z3V5` as a prerequisite in its prose and does not declare the
edge in `blocked-by`. That advisory could not fire while `PL-Z3V5` existed on
nobody's branch but one nobody would merge: the checker had no such id to
resolve against, so an open item sat blocked on something the store did not
contain and nothing said so. Captured as its own item rather than fixed here -
the advisory names two remedies (declare the edge, or reword the sentence if it
is not really a prerequisite) and choosing between them is a decision, which
fails the third test of `CLAUDE.md`'s fix-now rule.

**Two of the nine came back already triaged and seven untriaged**, which is the
expected shape: `bin/docket triage` is where they are folded into the queue, and
a recovery pass that also triaged them would be resolving nine items' fields on
a branch cut for something else.
