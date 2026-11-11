---
id: PL-CTXZ
title: Move the seven interface sections of docs/MODEL.md, word for word, to a new interface document for contributors, re-point the code's citations of them, and extend the documentation checks to the new file (stage 1 of the split PL-P3GZ decided)
priority: P1
owner-priority: P1, 2026-11-11, ratified
effort: L
status: ready
classes: docs
feature: model-md-structure
touches: docs/MODEL.md, tools/doc_check.py, subprojects/docket/src/docket/arming.py, CLAUDE.md, .claude/rules/plain-writing.md, tools/model_rewrite.py, src/anesthesia_sim/, tests/
added: 2026-11-11
payoff: a contributor finds what the interface must show in one document, and a clinician no longer reads past 60,000 words of interface rules to reach the model
verify: ! grep -qE '^## (Runtime controls|Minimum displayed outputs)$' docs/MODEL.md
---

**Problem.** Move the seven interface sections of docs/MODEL.md, word for word, to a new interface document for contributors, re-point the code's citations of them, and extend the documentation checks to the new file (stage 1 of the split PL-P3GZ decided)

**Why it matters.** The project owner decided on 2026-11-11 to split
`docs/MODEL.md` by reader (`PL-P3GZ`, which holds the design and the
counts). Seven sections state what the interface must do. Their reader is a
contributor who changes the interface, and a clinician reads past them.
They hold 59,940 of the document's 129,000 words, the code cites them 141
times, and most of the 60 open items that will edit `docs/MODEL.md` add to
them. This is the first of three moves, so it also sets up what the other
two reuse.

**What to do.**

1. Create the interface document under `docs/`. The build chooses the file
   name. Move these `##` sections of `docs/MODEL.md` into it unchanged:
   "Runtime controls"; "Reset behavior"; "Agent-change behavior";
   "Discarding a run, and the questions that guard it"; "What a branch
   comparison asserts, and what it does not"; "Interface boundary";
   "Minimum displayed outputs".
2. Re-point each citation of a moved section with a script: in `src/`, in
   `tests/`, in the other documents and in the item briefs that are open.
   `tools/doc_check.py` already refuses a docstring citation when the
   document it names holds no such heading.
3. Make everything that reads `docs/MODEL.md` as the specification read
   the new file too. `PL-P3GZ` lists them under "What the split changes
   outside the documents": `CLAUDE.md`, `.claude/rules/plain-writing.md`
   (a row for the new document and its reader), `tools/doc_check.py`,
   `subprojects/docket/src/docket/arming.py`, six tools and the rules,
   skills and agents that name the path. State the list of specification
   documents once, where those tools read it, so that `PL-6PPZ` and
   `PL-FWR6` each add one path.
4. Leave one sentence in `docs/MODEL.md` that names the new document and
   what it holds.
5. Show that the move lost nothing: every value, equation, code span and
   citation of the moved sections is in the new file. `tools/model_rewrite.py
   lost` makes that comparison within one file. Check first whether it can
   compare across two.
6. Re-point the `touches` of `PL-SY7G` (sort the interface document) at the
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

**Done when.** `docs/MODEL.md` holds none of the seven headings, the new
document holds the seven sections word for word, every citation of them
resolves, the checks that read `docs/MODEL.md` read the new file, and
`make check` passes.

**Generator check.** Part of the fix for the cause that `PL-P3GZ` records:
the repository named no home but `docs/MODEL.md` for a test's description,
an interface requirement or a value's source history, so each change added
them there. No new head.
