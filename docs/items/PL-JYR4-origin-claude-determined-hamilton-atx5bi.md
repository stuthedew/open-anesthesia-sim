---
id: PL-JYR4
title: origin/claude/determined-hamilton-atx5bi carries four closed Gate 1 items and the three agent files' Yasuda adoption, has no pull request, and its session is archived failed - PL-Q664's defect happening live
priority: P2
effort: S
status: done
classes: defect
feature: parallel-sessions
touches: docs/items
added: 2026-09-13
closed: 2026-09-13
pr: 548
verify: bin/docket check && grep -q '^status: done' docs/items/PL-B9K7-yasuda-targ-and-eger-1989-s-tissue-solubility.md
---

**Problem.** origin/claude/determined-hamilton-atx5bi carries four closed Gate 1 items and the three agent files' Yasuda adoption, has no pull request, and its session is archived failed - PL-Q664's defect happening live

**What is on it.** Nineteen files, 601 insertions against the merge base, three
commits, the newest dated 2026-09-13 21:47 UTC:

- `PL-B9K7`, `PL-8GJ6`, `PL-FN5F` and `PL-LS3H` at `status: done`. Three of the
  four exist on no other ref - `main` has never seen their item files at all.
- `src/anesthesia_sim/data/agents/desflurane.json`, `isoflurane.json` and
  `sevoflurane.json` changed, which is the twelve partition coefficients'
  provenance, plus `src/anesthesia_sim/core/circuit.py`.
- `PL-N701` retitled from "The 2026-09-13 Yasuda 1991 corpus read for PL-ZP7Z
  owes an extraction note" to "Two 2026-09-13 corpus reads owe an extraction
  note", and `PL-QS9H` moved to `ready`.

**Why it matters.** Verified 2026-09-13: the branch has no pull request
(`list_pull_requests` returns #544, #545 and #546 and none of them is this one),
and the session that wrote it - "Gate items batch",
`session_01Sk9XWiSwKER6BLF9mygjYf` - is archived with `status_category: failed`.
Nothing will merge it on its own. Meanwhile every session's digest reads
`PL-B9K7` as in flight and says "do not start these again", so the queue is
telling sessions to leave alone work that nobody is doing, which is the exact
failure `PL-Q664` describes and the reason that item exists. `bin/docket
stranded` does not report the four either: they are closed on the branch, and
`stranded` looks for *work* that exists only on a branch.

This blocked the 2026-09-13 triage pass from answering `PL-B9K7` and `PL-N701`,
which are the two of twenty-seven captures it had to leave untriaged.

**What it is not.** Not a request to merge the branch unread. It changes three
agent data files, which is safety-critical provenance under `CLAUDE.md`'s
clinical-output standard, so whatever opens the pull request owes those four
closures the same review any other science work gets.

**Done when.** The branch's work is either on a pull request against `main` or
deliberately abandoned with that recorded, and `PL-B9K7` and `PL-N701` are
reachable for triage again either way.
## Closed 2026-09-13, by the branch merging rather than by work here

The condition this item names was met without anything being done to the
branch: `origin/claude/determined-hamilton-atx5bi` merged, and `PL-B9K7`,
`PL-8GJ6`, `PL-FN5F` and `PL-LS3H` are all `status: done` on `origin/main`,
with the three agent data files' Yasuda adoption and `core/circuit.py` beside
them. `PL-N701` became reachable and was triaged in the same pass that filed
this.

The `verify:` command records that condition rather than a change made here,
and its failing state is a matter of record rather than something re-runnable:
the file it greps did not exist on `origin/main` at all while the finding
stood, so the command exited 2 rather than 1.

**Kept rather than deleted, because the mechanism did not improve.** Nothing
detected the branch and nothing would detect the next one - `bin/docket
stranded` cannot see it, since the items on it are closed rather than stranded
work, and `flight` reports it as in flight, which is the opposite of the truth.
`PL-Q664` (a branch whose items are all closed and which has no open pull
request is indistinguishable from live work in `docket flight`) is the item
that fixes it, and this is its worked instance with a cost attached: four
closed Gate 1 items and three agent data files reached `main` only because a
triage pass happened to look at why two captures were unreachable.
