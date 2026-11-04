---
id: PL-T3KB
title: Re-run the current prose review over docs/MODEL.md's first four rewritten parts (Status through the source hierarchy), which were written before the review named each text's readers, and rewrite what it now fails with no value changed
priority: P2
effort: M
status: done
classes: docs
feature: prose-quality
milestone: v0.6.15
touches: docs/MODEL.md
added: 2026-11-03
closed: 2026-11-03
pr: 1970
payoff: the opening sections, conventions, equations, numerical method and source hierarchy of the model specification meet the same reader-named prose review as the later sections, so a clinician reads the whole document to one standard
verify: grep -q '^Prose-review: read' docs/items/PL-T3KB-re-run-the-current-prose-review-over-docs-model.md
not-delegable: `docs/MODEL.md` is a `protected_paths` entry, so no delegated diff may touch it. Readability is judged by a person: no command separates plain prose from padded prose.
---

**Problem.** `PL-ZT47`'s first four section parts were rewritten and merged
before the prose review changed: `PL-J8CG` (#1944, § "Status" through
§ "Model boundary"), `PL-XTZW` (#1945, § "Conventions" through § "Conservation
of agent mass"), `PL-TZ47` (#1947, § "Numerical method") and `PL-HJDK` (#1949,
§ "Source hierarchy"). Since then the review names each kind of text's readers
(`PL-R7Q6`, #1957), asks what the named reader would take from each unit
(`PL-1XC7`, #1959), and refuses a rewrite longer than the text it replaces
(`PL-CWRZ`, #1962). The project owner asked on 2026-11-03 for those parts to go
back through the review as it now stands (project owner, 2026-11-03).

Parts 5 to 7 and the runtime-controls part are out of scope. Each ran the
current prompt, unchanged since #1962 (2026-11-03 02:37Z): `PL-QL0X` (#1953) at
03:14Z, `PL-70B2` (#1950) at 04:25Z, and `PL-WBR3` (#1952) and `PL-QHR2` (#1964)
after it.

**Why it matters.** A clinician reads `docs/MODEL.md` to decide whether to
trust a displayed value. The first four parts are the ones that state the
intended use, the hazards, the equations and the numerical method, and they
are the only parts not yet held to the reader-named review.

**How.** Print each part's units with `tools/new_prose.py` against a base that
lacks that part's lines, give each part's output to one fresh reviewer as
close-out step 8 says, and apply the rewrites that keep every value, unit,
condition, identifier and citation. Move a fact the reviewer moves to the
place it names, such as a section's note for developers. No stored value or
equation changes. The checked rewrite merges on green without the owner's
read (project owner, 2026-11-02 19:40Z).

**Done when** the four parts' prose has been through the current review, the
rewrites are applied, and the branch's `Prose-review:` trailer records the
counts.
The close-out writes those counts into this file as a line of its own, in
the trailer's form, and `verify:` reads that line.

**Moved from `docs/MODEL.md`.** The review moved two pieces of history out of
the document, and they are kept here.

- § "This is an engineering bar, not a regulatory status": "ISO 14971:2019 is
  the second standard this section relies on. The 2007 edition mentioned
  **reasonably foreseeable misuse** only in passing. The 2019 edition made it a
  defined term."
- § "Source hierarchy", on Lowe and Ernst: "Interlibrary loan is a third way of
  reaching a source. It is neither the route that
  `.claude/rules/citing-sources.md` describes nor the personal access through
  which the Workbook arrived."

Two hazard-table and display sentences that recorded wording as a placeholder
were cut: "The wording is a placeholder while the interface is being built"
(the mark-stopped row) and "The wording is a placeholder that the project owner
may revise" (the "Model outputs — not measurements." heading). Both wordings
remain placeholders under the project owner's 2026-10-18 rule on look, wording
and placement.

**Counts.** Parts 1 to 4 and the new notes for developers, together:

Prose-review: read 378, rewrote 248, rejected 33
