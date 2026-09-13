---
id: PL-T9XJ
title: docs/resident-instructions.md opens by naming two resident files when there are three, in the document that governs resident cost
status: untriaged
added: 2026-09-13
---

**Problem.** docs/resident-instructions.md opens by naming two resident files when there are three, in the document that governs resident cost

**Notes.** Lines 3-4 read "Two files reach every session at launch, before a
prompt has been read and before any tool has run: `CLAUDE.md`, and
`.claude/rules/instruction-writing.md`". There are three:
`.claude/rules/expert-review.md` carries no `paths:` and says so in its own header
("Resident by necessity; no `paths:`, deliberately"). `make check` already reports
all three — 49,802 characters over 715 lines, `CLAUDE.md` 32,692 /
expert-review.md 7,438 / instruction-writing.md 9,672 — so the ledger's
opening sentence disagrees with the measurement printed beside it.

The body of the same document is right: § "What stays resident, and on what
argument" names `.claude/rules/expert-review.md` at line 104, in the group it
heads "**Fires when the approach is being decided.**", with its
+4,721-character cost and `PL-WWDT` as the reason. Only the preamble was not
updated when it moved.

**Why it matters.** This is the document whose whole purpose is to stop the
resident-cost question being re-opened from scratch, and it understates the
number a session is being asked to economize on by 7,438 characters — in the
sentence a session reads first.

**Where.** `docs/resident-instructions.md`, lines 3-4.

**Found.** 2026-09-13, reviewing an outside article on long AI projects against
this repository.
