---
id: PL-6PPZ
title: Move the six verification sections of docs/MODEL.md, word for word, to a new verification document for developers, with the code's citations of them and the checks that read them (stage 1 of the split PL-P3GZ decided)
priority: P1
owner-priority: P1, 2026-11-11, ratified
effort: M
status: ready
classes: docs
feature: model-md-structure
touches: docs/, tools/, subprojects/docket/, .claude/, CLAUDE.md, docket.toml, README.md, ROADMAP.md, src/anesthesia_sim/, tests/
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

**What `PL-CTXZ` set up for this move, 2026-11-11.** The steps that item
took, in order, and what went wrong the first time:

1. Add the new document's path to `docket.arming`: a constant beside
   `INTERFACE_DOC`, and an entry in `SPECIFICATION_DOCS`. The documentation
   check, `tools/model_rewrite.py` and `tools/model_doc_review.py` read that
   tuple. Then add the path to the four lists that restate it:
   `protected_paths`, `product_paths` and the `simulator` area in
   `docket.toml`, and `SECOND_PASS_PATHS` in `docket.arming`.
   `tools/config_home_check.py` names each copy that differs, in `CLAUDE.md`,
   `docs/worker.md` and `.claude/rules/expert-review.md` too.
2. Write the new file with its title and one opening paragraph, then run
   `python3 tools/model_rewrite.py move --to docs/NEW.md "Heading" ...`. It
   moves the sections and re-points the citations. `python3
   tools/model_rewrite.py lost` then shows whether any fact was lost.
3. Point `BOUND_FAMILIES` in `tools/doc_check.py` at the new document for each
   family whose section moved: "Required tests" and the hazard table are two.
   `_bound_families_in_one_fixture_document` in
   `tests/unit/test_doc_check.py` keeps the fixture tree in one document.
4. Read what `move` prints as unplaced, and re-point by hand each message in
   `src/` whose section name is split across string literals or filled in
   from a variable. The script cannot read those.
5. Check each open item's `verify:` command. `move` takes the quotation after
   a path for that path's own, which is wrong for `grep 'text' path`, so it
   re-pointed several to the wrong file. Point each at the document that
   holds its text, and add that document to the item's `touches`.
6. Run `bin/docket check`. It names each open item whose title changed, and
   so whose file must be renamed with `git mv`.
7. `move` also re-points fixtures in the tests of the tools, such as
   `tests/unit/test_new_prose.py`, which write their own `docs/MODEL.md`.
   Restore those files.
8. Add the document's row to the reader table in
   `.claude/rules/plain-writing.md`, which
   `test_every_product_document_has_a_reader_except_the_release_notes`
   requires, and its entry to `README.md`'s list of documents.
