---
id: PL-2LB5
title: Design round: make one source of truth the core design principle everywhere, simulator and apparatus, and fix existing copies structurally rather than one instance at a time
priority: P2
effort: M
status: done
classes: planning, docs
feature: one-source-of-truth
milestone: v0.6.0
touches: CLAUDE.md, docs/resident-instructions.md
deferred-from: v0.6.0 - captured after the freeze on the owner's 2026-10-19 ask; the fixes are proposed as their own milestone once the inventory sizes them
added: 2026-10-19
closed: 2026-10-19
pr: 1682
verify: bin/docket feature one-source-of-truth
---

**Problem.** Design round: make one source of truth the core design principle everywhere, simulator and apparatus, and fix existing copies structurally rather than one instance at a time

**The ask** (project owner, 2026-10-19): "We should have one source of truth everywhere in this project. Apparatus, simulator etc. That should be a core design principle. And we should proactively fix this structurally everywhere."

**What already exists.** `CLAUDE.md` § "Architecture and development discipline" has carried "A shared fact has one source of truth" since 2026-10-12, resident, for the simulator and the apparatus alike. Two checks enforce part of it:
- `tools/literal_home_check.py` refuses a second copy of a number under `src/`. On 2026-10-19 its baseline was 35 sites in 9 files, nearly all layout values in `app/`. Tests pin the five in `core/` to the shipped data files.
- `tools/fact_home_check.py` refuses a reader of git, the tree, the GitHub API, the default branch or a shell command outside its home, and an upper-case constant defined in two apparatus files. Its baseline was 59 sites in 26 files.

No open item covers either baseline. Everything else is left to the sentence.

**Why it matters.** The 2026-10-19 defect review found two themes behind about half of every member a head explains:
- a fact worked out from history instead of recorded: 29 heads, 158 members
- one fact spelled in many places: 15 heads, 121 members

The first theme's organic inflow fell from about 30 a week to 0 after the recording fixes of 2026-09-23 to 09-26 (`PL-MB2W`, `PL-HMZZ`, `PL-WD5Z`, `PL-QHCW`). The simulator's largest cluster, stale state after a halt, is the same failure: two writers of one displayed fact (`PL-X7D5`, `PL-R4Y2`).

**Proposed approach: four shapes of a second copy, each fixed by its shape.**
1. **A value copied.** A number typed again is covered by the two checks above. A value held in a data file or in code and restated in `docs/MODEL.md`, `README.md` or a docstring is not. New: a `doc_check` rule ties such a number to its home and fails on a mismatch. Checked rather than generated, so `docs/MODEL.md` stays a hand-written, reviewable specification. That is an internal choice, decided here.
2. **State with two writers.** A displayed or derived state written on more than one path. The fix is the `PL-X7D5` pattern, one writer plus a guard that checks every widget by default, extended to every surface that states run state.
3. **A rule made in several places.** A quantity's range checked by hand is fixed with checked types (`.claude/rules/core-domain.md`). A predicate worked out again in the apparatus is fixed by `fact_home_check`. Copied logic is caught by pylint's existing duplicate-code checker (`R0801`) as a ratchet over `src/`, `tools/` and `subprojects/docket/`, rather than a new tool.
4. **Configuration restated.** The Python version, paths, commands and timeouts across `pyproject.toml`, `.github/workflows/`, the `Makefile`, `docket.toml` and the docs get one home each, held by a check.

Each check carries a baseline that can only shrink, and the baseline is burned down to zero.

**Two copies that must stay copies.** A test's expected value: `.claude/rules/test-oracles.md` requires it from a source independent of the code under test, and an expected value imported from that code verifies nothing. And a published value restated in a data file with its citation, which is provenance.

**Proposed breakdown** [superseded 2026-10-19: filed as `PL-K88Z`, `PL-JS6P`, `PL-WM5P`, `PL-VWXL` and `PL-SH0W`, below].
1. The principle's wording in `CLAUDE.md`, done on 2026-10-19 on this item's branch.
2. An inventory of second copies by shape across the whole tree, deterministic tools first, each finding filed under this feature (M).
3. The `doc_check` rule tying numbers in `docs/MODEL.md` and `README.md` to their home (M; safety-relevant, since `docs/MODEL.md` is the authoritative specification).
4. The single-writer guard extended to every surface that states run state (M).
5. The pylint duplicate-code ratchet (S).
6. One home for each configuration fact, with its check (S).
7. Burning each baseline down, as the inventory's items.

**Decision needed.** Where this goes against v0.6.0 ("the layout is the reader's", 38 of 39 Required ids closed on 2026-10-19). **Recommendation:** do step 2, the inventory, now. Scope the fixes as their own `ROADMAP.md` milestone after v0.6.0 ships, because the inventory decides how large the work is, and a milestone is scoped before it is built.

**Answer** (project owner, 2026-10-19, ratified, over folding the fixes into v0.6.0 and over leaving them unplaced): "Agree with recs". The inventory runs now as `PL-K88Z`, ahead of v0.6.0's last item. The fixes are `ROADMAP.md` planned-milestone item 43, placed on § "The timeline" as the `v0.6.x — one source of truth` row, directly after v0.6.0 and before the interface pass. Placing it directly after v0.6.0 is the session's reading of "after v0.6.0 ships": every release that waits behind it pays the defect inflow these copies cause. The row is scoped once the inventory has sized it. Steps 3 to 6 are filed as `PL-JS6P` (numbers in `docs/MODEL.md` tied to their home), `PL-WM5P` (one writer for every surface that states run state), `PL-VWXL` (the pylint duplicate-code ratchet) and `PL-SH0W` (one home for each configuration fact). Each waits on v0.6.0 and on the inventory. Step 7, burning each baseline down, is the inventory's own filings.

**Done when.** [superseded 2026-10-19: the whole program's end state now belongs to the feature `one-source-of-truth` and planned-milestone item 43.] This design round is done when the principle's wording is in `CLAUDE.md`, the breakdown is filed under `one-source-of-truth`, and the fixes are placed in `ROADMAP.md`. All three held on 2026-10-19.

**Generator check.** This widens `PL-4S6C` (the fact-home check and the resident principle, closed 2026-10-12) at the owner's ask, and is not a re-entry of it. No filing has fallen through `tools/fact_home_check.py` since it closed. The new scope is the shapes that check never covered: state, documents and configuration.
