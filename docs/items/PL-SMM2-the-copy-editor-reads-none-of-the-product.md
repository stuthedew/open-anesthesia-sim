---
id: PL-SMM2
title: The copy editor reads none of the product documents under docs/ other than MODEL.md (ARCHITECTURE.md, references/, machine-survey.md, interface-provenance.md, consultant-brief.md), because no row of the reader table names them
priority: P2
effort: S
status: done
classes: docs
feature: copy-editor
milestone: v0.6.15
touches: .claude/rules/plain-writing.md, tests/unit/test_new_prose.py
added: 2026-11-04
closed: 2026-11-04
pr: 2023
payoff: a consultant, an educator or a contributor reading the architecture, the surveys or the release notes gets text reviewed for them
verify: grep -qF 'docs/ARCHITECTURE.md' .claude/rules/plain-writing.md && grep -qF 'docs/releases/' .claude/rules/plain-writing.md
---

**Problem.** The copy editor reads none of the product documents under docs/ other than MODEL.md (ARCHITECTURE.md, references/, machine-survey.md, interface-provenance.md, consultant-brief.md), because no row of the reader table names them

**Checked 2026-11-04.** The reader table in `.claude/rules/plain-writing.md` names two product documents, `docs/MODEL.md` and `README.md`. It names none of the others that `docket.toml`'s `product_paths` lists: `docs/ARCHITECTURE.md`, `docs/consultant-brief.md`, `docs/interface-provenance.md`, `docs/machine-abstraction.md`, `docs/machine-survey.md`, `docs/references/`, `docs/releases/` and `ROADMAP.md`. The capture's list left out the last three and `docs/machine-abstraction.md`. `tools/new_prose.py` lists a changed file that no row names under "Not reviewed". `PL-22T5`'s plan, point 6, left these documents to this item.

**Why it matters.** Some of these documents have readers outside the project, such as a consultant or an educator reading the release notes. A change to one gets no review for its reader now.

**Done when.** Each of those documents has a row in the reader table, or the table says why it is not reviewed, and `tools/new_prose.py` prints a changed paragraph from each one that has a row. The edit to the resident rule names what it replaces, or says why nothing can be cut.

**Generator check.** A remainder of `PL-J1ZM`'s fix, which `PL-22T5` left out on purpose. The fact is which text the copy editor reads, and the reader table is its one record. With `PL-Q98K` that makes two items on the fact, so no new head. Not a re-entry, because `PL-22T5` named it out of scope.

**Done 2026-11-04.** Four rows of the reader table now name `docs/ARCHITECTURE.md`, `docs/interface-provenance.md`, `docs/machine-abstraction.md`, `docs/machine-survey.md`, `docs/references/`, `ROADMAP.md` and `docs/consultant-brief.md`. `docs/releases/` has no row, and the rule says why: `bin/docket release` writes each note from item titles, so a copy edit there would make a note disagree with its item. That leaves the release notes this item's payoff named unreviewed, because their text is the item titles. `tests/unit/test_new_prose.py` reads `product_paths` and fails on a Markdown product document that no row names. A probe paragraph appended to each of the seven documents was printed with its row's readers, and the one appended to `docs/releases/v0.6.14.md` was listed as not reviewed.
