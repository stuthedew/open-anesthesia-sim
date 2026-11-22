---
id: PL-PNB2
title: Replace each paragraph of the instructions loaded at launch that a check enforces with one line naming the check, as PL-MR85's approved table marks them: rows 30-35, 43, 71 and 72
priority: P2
effort: M
status: done
classes: session-cost
feature: standing-weight
milestone: v0.6.19
touches: CLAUDE.md, .claude/rules/rule-routing.md, docs/resident-instructions.md, docs/items/PL-G3KZ-fail-make-check-when-the-lines-loaded-at-launch.md
deferred-from: v0.7.0 - the move changes how sessions are instructed, not the schematic, so the release does not wait on it
added: 2026-11-21
closed: 2026-11-21
pr: 2193
payoff: sessions load fewer lines of instructions before they read anything, so each rule that stays is likelier to be followed
verify: grep -qF 'tools/import_boundary_check.py' CLAUDE.md
---

**Problem.** Replace each paragraph of the instructions loaded at launch that a check enforces with one line naming the check, as PL-MR85's approved table marks them: rows 30-35, 43, 71 and 72

**Why it matters.** Every session loads about 1,332 lines of instructions before it reads anything. Claude Code's memory documentation says to "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence" (https://code.claude.com/docs/en/memory, § "Write effective instructions", read 2026-11-21). The project owner approved `PL-MR85`'s sort of every paragraph on 2026-11-21, and its table, in `PL-MR85`'s brief, names each row this item moves and how many lines stay.

**What to do.** Each row keeps one line that states the rule and names the check that enforces it, such as `tools/import_boundary_check.py` for simulation time held as explicit state. The co-author line in row 72 has no check, so it stays as it is.

**Generator check.** One-off. It carries out the owner's approval of `PL-MR85`'s table, and no fact was misread to cause it.

**Checked 2026-11-21**, by `PL-TPXK` (the independent review of the four streamlining decisions). Row 72 names two checks, `tools/branch_id_check.py` and `tools/pr_title_check.py`, and `PL-HS2T` (retire the branch-name check) deletes the first. So row 72's line names only `tools/pr_title_check.py`, which requires the item id at the front of the pull request title. No check requires an id at the front of each commit subject, and `tools/branch_id_check.py` never did: its docstring says "Not every commit - one is enough to make the branch visible". The sentence that asks for the id on each commit therefore stays as text, beside the co-author line.
<!-- absent: tools/branch_id_check.py -->

**Done when.** Each row listed in the title holds no more lines than `PL-MR85`'s table gives it, each named check runs in `make check` or in CI, and `make check` passes.

**Built 2026-11-21.** Each row that the title lists now holds no more lines than the table gives it. `python3 tools/doc_check.py check` counts 784 lines and 63,104 characters loaded at launch, where it counted 812 lines and 65,023 characters after `PL-T51K` (move procedures into the pull-request skill, the coordinator mode and the run-the-app skill). `docs/resident-instructions.md` § "The paragraphs that a check enforces" keeps each paragraph as it was loaded before the cut.

What each row keeps:

1. Rows 30 and 31 keep one line, which names `tools/import_boundary_check.py`. That check keeps `time`, `datetime`, `random`, `secrets` and `uuid` out of `core/`. The safety-critical standard still asks for deterministic behavior.
2. Row 32 keeps one line, which now says that `make check` holds `core/` at 100% coverage.
3. Row 34 is unchanged, and row 35 keeps one line.
4. Row 43 keeps one line: `pytest -q` while iterating, and `make check` before committing.
5. Row 71 keeps one line, which says that `make check` prints the size of what loads at launch. `PL-G3KZ` (the cap in `make check`) turns that line into the cap.
6. Row 72 keeps three lines.

Two things differ from the table. The first corrects it, as `PL-TPXK` (the independent review of the four streamlining decisions) found.

1. The table names `tools/branch_id_check.py` and `tools/pr_title_check.py` for row 72. `PL-HS2T` (retire the branch-name check) deleted the first on 2026-11-21, and that check never required an id on every commit subject. So row 72 names only `tools/pr_title_check.py`, for the title, and keeps as text the two rules that no check enforces: the item's id at the front of each commit subject, and the co-author line. `.claude/skills/docket/modes/start.md` already held the claim, the session name and the branch name.
2. Row 71 held two rules beside the growth figures: a rule that lands in none of the four places has been lost, so never delete a rule for being wordy, and a rule whose failure a check now catches is retired. The table sends the row's history to the ledger and names no home for those two rules. `.claude/rules/rule-routing.md` now ends with them, because it loads when a session edits `CLAUDE.md` or a file under `.claude/`, which is when they apply.

`docs/resident-instructions.md` § "The attribution sentence, added 2026-09-24" quoted the heading "Name the work after the item", which `CLAUDE.md` no longer holds, and now describes the bullet in words.

**Docs checked.** `subprojects/docket/src/docket/vcs.py` and `tools/pr_title_check.py` say that `CLAUDE.md` asks every commit subject to lead with the item's id, and it still does.

`PL-G3KZ` (the cap in `make check`) moves from blocked to ready in this change, because this item was its last open blocker.
