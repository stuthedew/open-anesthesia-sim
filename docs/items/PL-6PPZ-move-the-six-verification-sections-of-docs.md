---
id: PL-6PPZ
title: Move the six verification sections of docs/MODEL.md, word for word, to a new verification document for developers, with the code's citations of them and the checks that read them (stage 1 of the split PL-P3GZ decided)
priority: P1
owner-priority: P1, 2026-11-11, ratified
effort: M
status: done
classes: docs
feature: model-md-structure
touches: docs/, tools/, subprojects/docket/, .claude/, CLAUDE.md, docket.toml, README.md, ROADMAP.md, src/anesthesia_sim/, tests/
blocked-by: PL-CTXZ
added: 2026-11-11
closed: 2026-11-22
pr: 2204
payoff: a developer finds the numerical method, each required test and its limit in one document, apart from the model description a clinician reads
verify: ! grep -qF '## Numerical method' docs/MODEL.md
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
   from a variable. The script cannot read those. Read the second list it
   prints too: each quotation that follows one document's path and names a
   section only the other has, such as the second of two sections after one
   path. Then search `src/` for a message that names the old document and a
   moved section with no quotation marks, and for a test that opens the old
   document to read a moved section. Both blind review passes on `PL-CTXZ`
   found each of these.
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

**Done 2026-11-22**, in pull request #2204. The six sections moved word for
word to `docs/VERIFICATION.md`. `python3 tools/model_rewrite.py lost` showed
only the moved citations: `docs/MODEL.md` named three fewer times and
`docs/VERIFICATION.md` added. After the move, five sentences that said "this
document" for the equations were changed to name `docs/MODEL.md`, and 23
section marks gained the `docs/MODEL.md` path they had meant. The resident
instructions went 485 characters over their cap with the new document in
`CLAUDE.md`'s lists, so `PL-7YHK` moved the document reader rows to a rule
that loads with the documents.

The two blind review passes raised five points. Four are fixed, and one is
declined:

1. A test of the numerical envelope's refusal still expected `docs/MODEL.md`.
   The search missed it because the path is written with an escaped dot.
2. The document also holds the comparison with measurements in volunteers
   and the hazard list, which its title and the pointers to it did not say.
   The title, the opening, the pointer in `docs/MODEL.md`, `README.md`'s list
   and `CLAUDE.md` now say so.
3. `docs/MODEL.md`'s rule on what a dated statement means did not cover the
   new document. It does now.
4. The text that decides whether the owner must read a change named only
   `docs/MODEL.md` and `docs/INTERFACE.md`, so an edit weakening a hazard
   row in the new document would have counted as housekeeping. `JUDGE_ASK`
   now names the documents from `SPECIFICATION_DOCS`, and the pull-request,
   coordinator, close-out and model-review instructions, `docs/maintainer.md`
   and `tools/blind_review.py` name them too.
5. Both passes asked for the clinician to be named as a reader of the new
   document. Declined: `PL-P3GZ` names a developer as its reader, and the
   comparisons with measurements in people go to `docs/MODEL.md` in
   `PL-48MX`. Until then, the pointer in `docs/MODEL.md` § "Status" sends a
   clinician to them. The owner was asked who the document is for, and
   answered "Research best practice" (project owner, 2026-11-22). The
   published guidance keeps developers as the only reader. The ISPOR-SMDM
   task force on model transparency asks for two documents: a nontechnical
   description for anyone, which includes the validation methods, results
   and limitations, and technical documentation detailed enough for a reader
   with the needed expertise to evaluate and reproduce the model (Eddy DM et
   al. Med Decis Making. 2012;32(5):733-43. doi:10.1177/0272989X12454579;
   abstract read through PubMed). `docs/MODEL.md` after `PL-48MX` is the
   first and this document is the second. The FDA's guidance on reporting
   computational modelling studies addresses its report, with sections for
   code verification, calculation verification, validation and limitations,
   to industry and FDA staff, and names no clinician reader (FDA, Reporting
   of Computational Modeling Studies in Medical Device Submissions, 2016,
   Introduction and sections III, VIII, X and XIII; pages 1 to 16 read).

**Files checked** for a citation of a moved section, and for a sentence that
names `docs/MODEL.md` as the home of the numerical method, the tests or the
hazards: `CLAUDE.md`, `README.md`, `docs/MODEL.md`, `docs/INTERFACE.md`,
`docs/ARCHITECTURE.md`, `docs/apparatus.md`, `docs/maintainer.md`,
`docs/worker.md`, `docs/WORKING_NOTES.md`, `docs/resident-instructions.md`,
every rule, skill and agent under `.claude/`, `docket.toml`,
`subprojects/docket/src/docket/arming.py`, `tools/doc_check.py`,
`tools/product_paths.py`, `tools/blind_review.py`, the messages and
docstrings under `src/anesthesia_sim/`, and the tests that name a moved
section. `ROADMAP.md`, the release notes and the closed briefs record what
was true when they were written and were left as they are. A test message
that names `docs/MODEL.md` with no section, such as the coupled-dynamics
test's, is left for `PL-10BC`.
