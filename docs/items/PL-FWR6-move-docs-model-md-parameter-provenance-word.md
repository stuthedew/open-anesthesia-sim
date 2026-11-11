---
id: PL-FWR6
title: Move docs/MODEL.md § Parameter provenance, word for word, to a new parameter document, with the code's citations of it and the check that holds its table to the data files (stage 1 of the split PL-P3GZ decided)
priority: P1
owner-priority: P1, 2026-11-11, ratified
effort: M
status: blocked
classes: docs
feature: model-md-structure
touches: docs/MODEL.md, tools/doc_check.py, CLAUDE.md, .claude/rules/expert-review.md, src/anesthesia_sim/, tests/
blocked-by: PL-6PPZ
added: 2026-11-11
payoff: a reader checking a stored value finds its file, its source and why it was chosen in one document
verify: ! grep -q '^## Parameter provenance$' docs/MODEL.md
---

**Problem.** Move docs/MODEL.md § Parameter provenance, word for word, to a new parameter document, with the code's citations of it and the check that holds its table to the data files (stage 1 of the split PL-P3GZ decided)

**Why it matters.** The project owner decided on 2026-11-11 to split
`docs/MODEL.md` by reader (`PL-P3GZ`). § "Parameter provenance" holds the
table of stored values with each one's file and key, how each source was
read, and why each value was chosen. Its reader is a developer, or a
clinician checking one value against its source. It holds 13,176 words.

**What to do.** Follow `PL-CTXZ` (the interface move) and `PL-6PPZ` (the
verification move), which are done first.

1. Create the parameter document under `docs/`. Move the `##` section
   "Parameter provenance" of `docs/MODEL.md` into it unchanged.
2. Re-point each citation of the section and of its subsections, and add
   the new path to the list of specification documents.
3. `check_provenance` in `tools/doc_check.py` holds the provenance table to
   the data files in both directions, and reads it from `docs/MODEL.md` and
   `README.md`. Point it at the new file. The check must still fail when a
   stored value has no row and when a row has no stored value.
4. Change the sentence in `CLAUDE.md` that puts parameter provenance in
   `docs/MODEL.md`, and the pointer in `.claude/rules/expert-review.md` to
   § "Source hierarchy: what may be cited as the authority for a value" if
   that subsection moves.
5. Show that the move lost nothing, as `PL-CTXZ` step 5 does.
6. Re-point the `touches` of `PL-N83Z` (sort the parameter document) at the
   new file.

**What it must not do.** Change no word, value, equation, code span or
citation in the moved text. A section that mixes readers moves whole;
sorting its paragraphs is stage 3. Run no copy editor on the moved text: the
owner's hold of 2026-11-10 lasts for this document until its stage 3 item
closes. Set no word target (`PL-J1ZM`).

**Branches in flight.** A branch that edits a moved section ports its edit
to the new file once, when it brings `main` in. Say so in the pull request
body, with the list of moved headings.

**The pause on new workflow mechanisms.** The owner asked for the split, and
pointing the existing checks at the new file keeps them reading the text
they read today. The item builds no new check.

**Done when.** `docs/MODEL.md` holds no "Parameter provenance" heading, the
new document holds the section word for word, every citation of it
resolves, the provenance check reads the new file and still fails both
ways, and `make check` passes.

**Generator check.** Part of the fix for the cause that `PL-P3GZ` records:
the repository named no home but `docs/MODEL.md` for a test's description,
an interface requirement or a value's source history, so each change added
them there. No new head.
