---
id: PL-1SL4
title: tools/model_rewrite.py repoint rewrites citations inside test fixtures, and re-points by body text a section that was rewritten rather than moved
status: untriaged
added: 2026-11-22
---

**Problem.** tools/model_rewrite.py repoint rewrites citations inside test fixtures, and re-points by body text a section that was rewritten rather than moved

**Found 2026-11-22**, while building `PL-48MX`. `python3 tools/model_rewrite.py
repoint docs/MODEL.md docs/VERIFICATION.md` was run after the clinician's text
replaced the old sections of `docs/MODEL.md`. Two things went wrong, and every
change it made was reverted by hand.

1. It edited string fixtures in `tests/unit/test_doc_check.py` and
   `tests/unit/test_model_rewrite.py`, because `paths` defaults to every
   tracked text file. A fixture that quotes `docs/MODEL.md` § "..." is input
   for a test, not a citation, and the rewrite made those tests fail.
2. It re-pointed a citation of "Governing equations" to `docs/VERIFICATION.md`.
   The old heading was in neither document, and the moved developer text in
   `docs/VERIFICATION.md` held the words, so the second rule of `repoint`
   applied. The equations stay in `docs/MODEL.md`. The rule
   assumes the section moved whole, and a section rewritten in place breaks
   that assumption. "Model boundary" was re-pointed the same way.

**What would fix it.** Leave the test trees out of the default `paths`, or
leave out string literals. Refuse the body-text rule where the source
document lost the heading without the destination gaining it, and report the
citation as unplaced instead.
