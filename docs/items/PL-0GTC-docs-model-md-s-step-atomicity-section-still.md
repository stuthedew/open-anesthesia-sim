---
id: PL-0GTC
title: docs/MODEL.md's step-atomicity section still calls the class RespiratorySystem, renamed four releases ago
priority: P3
effort: S
status: done
classes: docs
milestone: v0.4.8
touches: docs/MODEL.md
added: 2026-09-03
closed: 2026-09-07
pr: 376
verify: python3 tools/doc_check.py check && ! grep -q 'RespiratorySystem' docs/MODEL.md
---

**Problem.** `docs/MODEL.md` § "Step atomicity" opens
"`RespiratorySystem.advance()` captures every dynamic value before the step".
That class was renamed `AgentUptakeSystem` in v0.2.11 (`PL-006`), so the
model specification names a class that does not exist. The same document uses
the current name correctly twice further down, in "Step atomicity" itself and
in "Supported simulation step", so this is one missed occurrence rather than
a document written against the old vocabulary.

**Why it matters.** `docs/MODEL.md` is the authoritative specification, and
`CLAUDE.md` treats stale documentation here as a safety issue rather than
tidiness. The concrete cost is small but real: a reader who greps the source
for `RespiratorySystem` finds exactly one hit, in `core/uptake_system.py`'s
module docstring, which exists to explain *why the old name was wrong* - it
warns that a reader taking "RespiratorySystem" at face value would read
`total_stored_agent_l` as agent in the lungs and "be wrong by a large factor
on an accounting quantity". So the specification currently points at the one
name the code goes out of its way to disown.

**Why no check caught it.** `tools/doc_check.py` decides whether a *cited
path* exists; it does not read symbol names, so a class that vanishes from
the tree leaves every prose mention of it untouched. `PL-X2XX` is the
adjacent item - the citation check reads neither `docs/items/*.md` nor source
docstrings - and whether symbol-name resolution is worth adding is a question
for whichever of the two is scoped first, not a reason to hold this.

**Where.** `docs/MODEL.md` § "Step atomicity", the paragraph beginning
"`RespiratorySystem.advance()` captures every dynamic value".

**Done when.** The paragraph names `AgentUptakeSystem.advance()`, and
`RespiratorySystem` appears nowhere in `docs/MODEL.md`.

**Found.** 2026-09-03, sweeping the documentation for `PL-BNPY`'s change to
the same paragraph. Captured rather than fixed there because it is unrelated
to that item.

**A note on the verify command, which took two attempts.** The obvious shape
- `doc_check` paired with `grep -q 'AgentUptakeSystem.advance()'` - **passes
today** and proves nothing, because that string already appears twice
elsewhere in the file. The recorded command greps for the *absence* of the
old name instead, and was watched exiting 1 against the unfixed document.
This is the failure mode `.claude/skills/docket/SKILL.md` describes for
unrun commands, met in practice: the paired-grep shape assumes the work
*adds* a string, and this work removes one.

**Closed 2026-09-07 as already done, under `PL-CL8J`.** The work landed in
`d8deea5` (#376, the exact-matrix-exponential change), which rewrote § "Step
atomicity" and removed the stale class name as a side effect of rewriting the
prose around it. The item was never closed, so `bin/docket check --verify` has
reported it as "open but its `verify:` command already passes" ever since.

Established by replaying every one of the 80 commits that touch `docs/MODEL.md`
and testing each revision under the *same whitespace normalisation this item's
own `verify:` command uses*. A line-based `grep` is not sufficient here and gave
a false reading first time: this document is hard-wrapped, so a phrase can span
a newline and `git log -S` misses it.
