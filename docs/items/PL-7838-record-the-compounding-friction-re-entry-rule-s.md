---
id: PL-7838
title: Record the compounding-friction re-entry rule's own first miss, so the pattern is recognizable
priority: P2
effort: S
status: done
classes: session-cost, docs
feature: planning-cadence
milestone: v0.2.8
touches: CLAUDE.md, ROADMAP.md
added: 2026-08-30
closed: 2026-08-30
commit: 4cb9af5
pr: 91
verify: python3 tools/doc_check.py check
---

**Problem.** The project owner asked (2026-08-30) how to get sessions to
recognize that process work with large downstream effects should be
prioritized and recommended as it arises, even during a freeze - while *not*
treating every appealing idea the same way ("refactor docket into Rust just for
fun" was their own counter-example).

The trigger was a real miss by this session. `PL-0RS6` (`docket next` leads with
out-of-scope work) was found mid-gate and deferred to the next gate on the
grounds that it was captured after the freeze. That was wrong twice over:

1. **The existing rule already admitted it.** `ROADMAP.md`'s "The gate is a
   snapshot" re-enters a finding whose *problem* was present at the freeze,
   "whatever id it is filed under or however long after the freeze it happened
   to be noticed". `docket next` has always ranked band-first, so the problem
   was present. The capture date was never the test, and using it was a
   misreading rather than a gap in the rule.
2. **The cost was never weighed.** The mitigation offered was "say two extra
   words when starting a session". The owner then demonstrated that the two
   words do not work: a fresh session asked for the "next recommended gate
   item" still ran twelve commands and reasoned its way past `docket next`
   before it could answer. Eighteen entries times that detour is a large
   fraction of the saving v0.2.8 exists to deliver.

**Why it matters.** Both failures are recommendation failures rather than
recording ones. The finding was captured, triaged and briefed correctly; what
was missing was saying "this one pays for the rest of the gate, do it first".
A session that files such a finding and moves on has done everything except the
part that mattered, and the owner cannot act on what only reached the queue.

**What was changed, 2026-08-30.** Both edits are in the tree:

- `CLAUDE.md` gains "Friction that compounds is recommended the moment it is
  found, not filed" - the duty to say so unprompted, with the arithmetic, in
  the reply that finds it.
- `ROADMAP.md`'s "The gate is a snapshot" gains "Friction that compounds is the
  clearest presence case" - that such a finding re-enters the frozen gate and
  is worked early rather than merely admitted.

Both carry the same discriminator, which is the half that keeps the rule from
swallowing everything: **the test is arithmetic, not enthusiasm.** Name the
per-item saving and multiply by the items remaining. Work that is merely
valuable, cleaner or more interesting makes no remaining item cheaper and waits
for the roadmap - the Rust rewrite is the canonical example and is named as
such. If the per-item saving cannot be named, it does not qualify.

**Done when.** Both edits are on `main` and say the same thing: that a finding
whose cost is paid by every remaining entry re-enters a frozen gate and is
recommended in the reply that finds it, and that the qualifying test is a named
per-item saving rather than how appealing the work is.

Recorded and edited in the same session, per `CLAUDE.md`'s rule that a behavior
change takes effect in the session that asks for it. This item is the record;
the two edits are the change.
