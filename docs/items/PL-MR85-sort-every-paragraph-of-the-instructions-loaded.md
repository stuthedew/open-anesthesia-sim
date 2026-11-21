---
id: PL-MR85
title: Sort every paragraph of the instructions loaded at launch into four groups (enforced by a named check, procedure for a skill, history, judgment no check can carry) and bring the table to the owner before any text moves
status: untriaged
feature: standing-weight
added: 2026-11-20
---

**Problem.** Sort every paragraph of the instructions loaded at launch into four groups (enforced by a named check, procedure for a skill, history, judgment no check can carry) and bring the table to the owner before any text moves

**Why it matters.** Every session loads 1,332 lines of instructions before it reads anything, as `python3 tools/doc_check.py check` reports. The instruction files grew from 60,199 characters on 2026-09-19 to 92,660 on 2026-11-20. The rule that every edit names what it replaces dates from 2026-09-19, so that rule has not stopped the growth. `PL-WKKH` (the streamlining questions from the study of the one-shot rewrite) holds the measurements and the sources.

**Answered 2026-11-20.** The owner agreed to the sort, and to a line cap after it (project owner, 2026-11-20, ratified, "Agree with recs", over leaving the size to the rule that each edit names what it replaces).

**What to do.**

1. Take each paragraph of `CLAUDE.md`, `.claude/rules/expert-review.md`, `.claude/rules/instruction-writing.md` and `.claude/rules/plain-writing.md`.
2. Put it in one of four groups. A paragraph that a named check enforces keeps one line, which names the check. A procedure moves to a skill. History moves to `docs/resident-instructions.md`. Judgment that no check can carry stays.
3. For each paragraph in the first group, confirm that its check runs in `make check` or in CI. A hook alone does not count, because project threads do not run the repository's hooks.
4. Bring the table to the owner. Move no text before the owner approves it.

**What follows the owner's approval.** File the moves as items. File a check in `make check` that fails when the lines loaded at launch pass a cap. `CLAUDE.md` § "The queue, and how the project owner works" records that a ceiling on its size was refused earlier, and this answer reopens that.

**Done when.** The owner has approved or changed the table, and the moves and the cap are filed as items.
