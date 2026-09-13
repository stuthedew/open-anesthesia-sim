---
id: PL-DBGT
title: desflurane.json points at 'the five other candidates ruled out' in a MODEL.md table that now has nine rows, and names tests/reference/test_published_wash_in.py, which does not exist
status: untriaged
added: 2026-09-13
---

**Problem.** desflurane.json points at 'the five other candidates ruled out' in a MODEL.md table that now has nine rows, and names tests/reference/test_published_wash_in.py, which does not exist

**Two stale references in one sentence**, in the Yasuda-1989 `sources` note in
`src/anesthesia_sim/data/agents/desflurane.json`:

> See docs/MODEL.md, 'Desflurane's residual, and why the parameter file was not
> changed', for the five other candidates ruled out and what is left open;
> tests/reference/test_published_wash_in.py asserts that a coefficient raised to
> the measurement's own ceiling still misses.

- **"the five other candidates"** - that table had eight rows before `PL-XWCY`
  and has nine after it, so the count was already wrong and is now further out.
  A reader following the pointer to check what has been excluded finds a
  different number of things than the sentence promised.
- **`tests/reference/test_published_wash_in.py` does not exist.** The file is
  `tests/reference/test_published_wash_in_and_elimination.py`. The assertion
  named is real -
  `test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination`
  - but the path does not resolve.

**Not fixed in `PL-XWCY`'s branch on purpose.** `desflurane.json` is outside
that item's declared `touches`, so `CLAUDE.md`'s fix-now rule refuses it on
test 2 and `bin/docket verify` would report the file as undeclared.

**Worth a moment's thought on the general case rather than only this
instance.** `tools/doc_check.py`'s dangling-citation check reads documentation
and source docstrings; whatever it reads, it did not catch a non-existent test
path inside a data file's `sources` note. Notes of this length are where such
references accumulate, and a hand-maintained count of table rows is the shape
`PL-GLBF` is already about for `ROADMAP.md`. Whether the checker should reach
into `sources` notes is the decidable question here; recounting the table by
hand is not a fix that stays fixed.
