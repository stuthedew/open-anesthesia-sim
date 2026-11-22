---
id: PL-S3VQ
title: Mark the interface's text for translation with gettext, and write each learner-facing message as one whole-sentence template
status: untriaged
feature: localization
touches: src/anesthesia_sim/app, src/anesthesia_sim/layout, src/anesthesia_sim/core
added: 2026-11-22
---

**Problem.** Mark the interface's text for translation with gettext, and write each learner-facing message as one whole-sentence template

`PL-SRP7` (the localization research) chose gettext for the project's own text, and one `QTranslator` for Qt's own dialog text. Its § 1 gives the sources. `core/` may not import Qt (`tools/import_boundary_check.py`), and `core/` raises refusal messages that a learner reads, so Qt's `tr()` cannot reach them and the standard library's `gettext` can.

**Scope.** Add one small module that gives `_`, `ngettext` and `pgettext` from a `gettext.NullTranslations`, so that every marked string still returns its English text and nothing a learner sees changes. Mark the learner-facing text in `app/`, `layout/` and the refusal messages in `core/`. Rewrite each learner-facing f-string as a whole-sentence template with named placeholders, filled in after the translation call. Write each count-dependent message as one `ngettext` call. Collect the marked text with `pybabel extract` into a `.pot` file, and add a test that the collected catalogue is current. No translation is shipped.

**Why now is cheaper than later.** On `main` at `a7eb53f`, an `ast` count finds 1,317 string literals of more than one word outside docstrings, and 755 f-strings, in `src/anesthesia_sim/`. Every new message written as an f-string or from joined fragments adds to the rewrite.

**What stays the same.** `tests/integration/approved_interface_strings.json` checks the English text word for word, with no catalogue loaded. Unit symbols come from `DisplayUnit` and are not translated, as the SI Brochure § 5.2 treats them as mathematical entities.

**Not in v0.7.0.** The owner said on 2026-11-22 that localization need not be built now (project owner, 2026-11-22).

**Generator check.** A one-off: planned work that the localization research (`PL-SRP7`) recommends, not a cause of other items.
