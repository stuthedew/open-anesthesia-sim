---
id: PL-794W
title: A closing-block line putting a decision to the project owner does not disclose that its answer will produce a commit, so it can be ordered after a line that merges the branch the commit belongs in
priority: P2
effort: S
status: done
verify: python3 tools/doc_check.py check && grep -q 'sorts as work' .claude/rules/instruction-writing.md
classes: defect, docs
feature: worker-instructions
touches: .claude/rules/instruction-writing.md
added: 2026-09-01
closed: 2026-09-01
---

**Problem.** Rule 14 of `.claude/rules/instruction-writing.md` already requires
the closing block to be ordered "the way it will be done", and says a line
"has to land before the next makes sense" goes first. It is adequate as
written. What it does not require is that a line *disclose its own output* —
and a line that reads as a question rather than as work is the one that gets
mis-sorted, because nothing on its face says a commit follows from answering
it.

Observed 2026-09-01, at least the third time the project owner has raised
wrong ordering. The block was:

1. Merge #159 once CI reports green.
2. Decide where `PL-7QKY`'s thread pointer gets delivered.

Item 2's answer was a change to `docs/items/PL-7QKY-*.md`, a file #159 was
already modifying, in a pull request whose whole purpose was triaging that
item. So item 2 had to land before item 1 made sense, and the numbering said
the opposite. The owner answered both at once, the merge went first, and the
decision became orphaned work.

**Why it matters.** The cost is not the mis-ordering, it is the recovery. That
one inversion cost a branch restart against a squash-merged base, a
cherry-pick, a force-with-lease push, a second CI run, a second pull request
(#160) and a second review — for a one-file change that would have been three
lines inside #159. It also walked the session straight into `CLAUDE.md`'s
stale-tracking-ref trap: the push recreated a branch GitHub had deleted on
merge.

Rule 14 is explicit that "a numbered list states an order whether or not one
was meant", so the reader is entitled to act on the numbering, and did.

**Where.** `.claude/rules/instruction-writing.md`, rule 14. Prose only.

**The rule, approved by the project owner 2026-09-01 and now in rule 14.** One
clause: a closing-block line whose answer will produce a commit says so, and
sorts as work rather than as a question. Where that commit belongs in a branch
another line would merge or close, the decision line comes first —
unconditionally, since a merge is irreversible against a branch and a decision
is not.

Deliberately narrow. It adds a disclosure requirement rather than a second
ordering rule, because the ordering rule is already right and a second one
competing with it is how this file starts contradicting itself.

**Watch for.** Do not solve this by widening rule 14 into a general dependency
analysis of the block. The failure is specific and recognisable: a question
whose answer is a diff.

**Done when.** Rule 14 requires a decision line to disclose that answering it
produces a commit, and states that such a line precedes any line merging or
closing the branch that commit belongs in.
