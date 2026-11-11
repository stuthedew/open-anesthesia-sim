---
id: PL-6PPZ
title: Move the six verification sections of docs/MODEL.md, word for word, to a new verification document for developers, with the code's citations of them and the checks that read them (stage 1 of the split PL-P3GZ decided)
priority: P1
owner-priority: P1, 2026-11-11, ratified
effort: M
status: blocked
classes: docs
feature: model-md-structure
touches: docs/MODEL.md, tools/doc_check.py, CLAUDE.md, .claude/rules/plain-writing.md, src/anesthesia_sim/, tests/
blocked-by: PL-CTXZ
added: 2026-11-11
payoff: a developer finds the numerical method, each required test and its limit in one document, apart from the model description a clinician reads
verify: ! grep -qE '^## (Numerical method|Required tests)$' docs/MODEL.md
---

**Problem.** Move the six verification sections of docs/MODEL.md, word for word, to a new verification document for developers, with the code's citations of them and the checks that read them (stage 1 of the split PL-P3GZ decided)

**Why it matters.** The project owner decided on 2026-11-11 to split
`docs/MODEL.md` by reader (`PL-P3GZ`). Six sections say how the
implementation is shown to solve the model's equations correctly. Their
reader is a developer. They hold 32,206 words.

**What to do.** Follow `PL-CTXZ` (the interface move), which is done first
and sets up the script, the list of specification documents and the
comparison.

1. Create the verification document under `docs/`. Move these `##` sections
   of `docs/MODEL.md` into it unchanged: "Conservation of agent mass";
   "Numerical method"; "Reasonably foreseeable misuse, and the hazards the
   presentation carries"; "Required invariants"; "Required tests"; "Release
   gate".
2. Re-point each citation of a moved section, and add the new path to the
   list of specification documents.
3. The named-test and bound-family checks in `tools/doc_check.py` read
   these sections. Point them at the new file.
4. The verification document becomes the home of the numerical method.
   Change the two sentences that put it in `docs/MODEL.md`: the one in
   `CLAUDE.md` under the safety-critical standard, and the one in
   `.claude/rules/plain-writing.md` that cites `PL-TZ7R`.
5. Show that the move lost nothing, as `PL-CTXZ` step 5 does.
6. Re-point the `touches` of `PL-4H8Q` (sort the verification document) at
   the new file.

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

**Done when.** `docs/MODEL.md` holds none of the six headings, the new
document holds the six sections word for word, every citation of them
resolves, the named-test and bound-family checks read the new file, and
`make check` passes.

**Generator check.** Part of the fix for the cause that `PL-P3GZ` records:
the repository named no home but `docs/MODEL.md` for a test's description,
an interface requirement or a value's source history, so each change added
them there. No new head.
