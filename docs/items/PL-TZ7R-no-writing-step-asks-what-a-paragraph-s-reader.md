---
id: PL-TZ7R
title: No writing step asks what a paragraph's reader should take from it and do with it, or where a chosen value's reason is recorded, so paragraphs keep every figure and its history and state reasons no record supports
priority: P1
owner-priority: P1, 2026-11-02
effort: M
status: blocked
feature: reader-tested-prose
touches: .claude/rules/plain-writing.md, docs/items/PL-ZT47-docs-model-md-still-reads-as-machine-written.md, tools/model_rewrite.py, tests/unit/test_model_rewrite.py
blocked-by: PL-R7Q6
added: 2026-11-02
payoff: each paragraph carries what its reader needs, and each chosen value says what it does, why, and how to change it, from a record
verify: grep -q 'git log -S' .claude/rules/plain-writing.md
---

**Problem.** No writing step asks what a paragraph's reader should take from
it or do with it. Three steps push every figure to stay in the paragraph: the
plain-writing rule's point 7, the close-out prose review's "keep each number
... exactly as written", and `PL-ZT47`'s step 3 with `tools/model_rewrite.py
lost`. Asked why a number is what it is, writers told its history. Twice they
stated a reason that no record supports. Once they wrote that no record
existed without looking, though `git log -S 5e-3` finds the origin of the
0.5% tolerance in the first v0.1.0 build (`PL-H76S`, faults 3 and 4).

**Why it matters.** A clinician reading `docs/MODEL.md` loses the point under
figures and history, and a developer cannot tell what a value does or how to
change it. A stated reason with no source is a false statement in the
authoritative specification.

**What to build.** Decided in `PL-H76S`'s design round (project owner,
2026-11-02, 23:41Z, ratified, over a sixth plain-writing pattern).

1. **A step before writing.** In `.claude/rules/plain-writing.md`, the writer
   states in one sentence what the paragraph's reader should take from it and
   what they will do with it, using the reader table from `PL-R7Q6`. A fact
   that serves neither goes where its reader will look for it. Decision
   history goes to the item. Numerical detail goes to a marked note for
   developers in the same section of `docs/MODEL.md`, which must still hold
   the numerical method.
2. **A chosen value's reason.** Where a paragraph gives a chosen value, its
   part for developers says what the value does, why it is this number, and
   what changing it would do. Each answer is read from the code or test that
   uses the value, or from a cited record. Where the reason is not at hand,
   the writer first traces the value's history with `git log -S` and the
   items. Where the trace finds no reason, the writer files an item for the
   missing record, and the text says what the trace found.
3. **Point 7.** Keep every fact where its reader will find it: in the
   paragraph, in the note for developers, or in the item. Never change a
   value.
4. **The `docs/MODEL.md` section procedure.** `PL-ZT47` § "How each section
   part is done" admits "moved to the note for developers" in step 5's
   accounting. If `tools/model_rewrite.py lost` reports a fact moved within
   its section as gone, fix that, with a test.

**Done when.** The rule carries the step before writing and the tracing step
for a chosen value, point 7 says where a fact may go, and the section
procedure accepts a move to the note for developers.

**Generator check.** Part of the fix for `PL-H76S`, the live generator for
prose that passes every check and fails its reader.
