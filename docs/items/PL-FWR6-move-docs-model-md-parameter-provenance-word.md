---
id: PL-FWR6
title: Move docs/MODEL.md § Parameter provenance, word for word, to a new parameter document, with the code's citations of it and the check that holds its table to the data files (stage 1 of the split PL-P3GZ decided)
priority: P1
owner-priority: P1, 2026-11-11, ratified
effort: M
status: done
classes: docs
feature: model-md-structure
milestone: v0.6.20
touches: docs/, tools/, CLAUDE.md, .claude/, README.md, ROADMAP.md, docket.toml, subprojects/docket/, src/anesthesia_sim/, tests/
blocked-by: PL-6PPZ
added: 2026-11-11
closed: 2026-11-22
pr: 2220
payoff: a reader checking a stored value finds its file, its source and why it was chosen in one document
verify: ! grep -qF '## Parameter provenance' docs/MODEL.md
recurrences: 2026-11-21 PL-RMNP
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

**Checked 2026-11-22** against `d4e8200`: still applies. `docs/MODEL.md` still has `## Parameter provenance` at line 2577, and no parameter document exists under `docs/`. The blocker `PL-6PPZ` (the move of the six verification sections) is still open and was claimed by another session at 00:45 UTC on 2026-11-22. `PL-CTXZ` (the interface move) merged as #2109 on 2026-11-13, so this item waits only on `PL-6PPZ`.

**Done 2026-11-22.** `docs/MODEL.md` § "Parameter provenance" moved word for
word to `docs/PARAMETERS.md`, under a short opening that says what the
document holds. Its subsections keep their headings: "Source hierarchy: what
may be cited as the authority for a value", "Where each stored value comes
from", "v0.2.0: isoflurane and desflurane" and "Delivery-limit and MAC
parameters".

1. Every citation of the section or a subsection now names the new document:
   in the code, the `sources` notes of the data files, the tests, the other
   documents, the rules and the open item briefs.
2. `docs/PARAMETERS.md` joined the specification documents in
   `docket.arming.SPECIFICATION_DOCS`, `tools/product_paths.py`,
   `docket.toml`'s path lists and the paths that owe a second blind review
   pass. `CLAUDE.md`, `.claude/rules/expert-review.md` and
   `.claude/rules/apparatus-standard.md` name it with the simulator, and
   `.claude/rules/document-readers.md` gives its readers.
3. `check_provenance` in `tools/doc_check.py` reads the provenance table from
   `docs/PARAMETERS.md`. Its tests still fail on a stored value with no row
   and on a row with no stored value.
4. `PL-4G3N` (#2212) changed a paragraph inside the moved section after this
   work began. That change is in `docs/PARAMETERS.md`.
5. `python3 tools/model_rewrite.py lost` against `origin/main` shows nothing
   held fewer times across the four specification documents.
6. `PL-N83Z` (sort the parameter document) now declares `docs/PARAMETERS.md`.

**Files checked** for a citation of the moved section, and for a sentence that
puts the provenance table, the source hierarchy or the source counts in
`docs/MODEL.md`: `CLAUDE.md`, `README.md`, `ROADMAP.md`, `docket.toml`,
`docs/MODEL.md`, `docs/INTERFACE.md`, `docs/VERIFICATION.md`,
`docs/ARCHITECTURE.md`, `docs/apparatus.md`, `docs/maintainer.md`,
`docs/worker.md`, `docs/resident-instructions.md`, `docs/machine-abstraction.md`,
`docs/machine-survey.md`, `docs/references/`, every rule, skill and agent under
`.claude/`, `subprojects/docket/src/docket/arming.py`, `tools/doc_check.py`,
`tools/product_paths.py`, `tools/source_tier_counts.py`, the `sources` notes of
the data files, the messages and docstrings under `src/anesthesia_sim/`, the
tests, and the open item briefs. The closed briefs, the release notes and the
completed milestones in `ROADMAP.md` record what was true when they were
written, and were left as they are. Mentions of `docs/MODEL.md` with no
section that mean an interface requirement are `PL-10BC`'s.
