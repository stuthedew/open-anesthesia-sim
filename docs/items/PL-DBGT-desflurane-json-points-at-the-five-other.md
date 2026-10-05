---
id: PL-DBGT
title: desflurane.json points at 'the five other candidates ruled out' in a MODEL.md table that now has nine rows, and names tests/reference/test_published_wash_in.py, which does not exist
priority: P2
effort: S
status: done
classes: docs, defect
feature: provenance
touches: src/anesthesia_sim/data/agents/desflurane.json, docs/MODEL.md
added: 2026-09-13
closed: 2026-10-05
pr: 1372
verify: ! grep -q 'test_published_wash_in.py' src/anesthesia_sim/data/agents/desflurane.json && ! grep -q 'five other candidates' src/anesthesia_sim/data/agents/desflurane.json && python3 tools/doc_check.py check
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
<!-- absent: tests/reference/test_published_wash_in.py -->

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

**Both claims verified 2026-09-14, and both hold.**

- `src/anesthesia_sim/data/agents/desflurane.json` sends the reader to
  `docs/MODEL.md`, "Desflurane's residual, and why the parameter file was not
  changed", "for the five other candidates ruled out". That section now reads
  "**Nine other candidates were tested or struck**" (`docs/MODEL.md:3134`). The
  count in the data file is four short.
- The same entry says "`tests/reference/test_published_wash_in.py` asserts that
  a coefficient raised to the measurement's own ceiling still misses". **No such
  file exists.** `tests/reference/` holds `test_canonical_evaluation.py`,
  `test_circuit_wash_in.py`, `test_control_resolution.py`,
  `test_coupled_dynamics.py`, `test_multi_agent.py`,
  `test_published_wash_in_and_elimination.py` and `test_sevo_patient.py`. The
  assertion is presumably in the last of those, under its longer name.
<!-- absent: tests/reference/test_published_wash_in.py -->

**Why it matters.** This is a parameter file's provenance note, and provenance
is the half of a stored value this project treats as safety-critical in its own
right: `CLAUDE.md` says the correct number with the wrong provenance is still a
safety failure. A reader auditing why desflurane's `vessel_rich` was not raised
is sent to a count that understates the work by four candidates, and to a test
file that does not exist - so the two things that would let them check the
reasoning both fail, while the number itself is right. `tools/doc_check.py`
cannot catch either: neither is a section citation.

**Done when.** `desflurane.json`'s note names the number of candidates
`docs/MODEL.md` actually rules out - or, better, stops restating a count that
goes stale and refers to the section instead - and names
`tests/reference/test_published_wash_in_and_elimination.py`, having confirmed
the assertion it describes is in that file. No stored value changes.

**Re-scoped 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
`check_citations` reaching a `sources` note is the work. The restated count is
**dropped rather than checked**, per the counts rule: a count in prose is
stated only where a check holds it to what it counts, or it is dated, and this
one is neither - the sentence states the rule without the number instead.

**Fixed 2026-10-05.** The Yasuda-1989 note in
`src/anesthesia_sim/data/agents/desflurane.json` now sends the reader to
`docs/MODEL.md`, "Desflurane's residual, and why the parameter file was not
changed", "for the other candidates tested or struck" - the section's own
verb, and no count - and names the assertion by its test,
`test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination`
in `tests/reference/test_published_wash_in_and_elimination.py`. Read before
naming it: the test raises desflurane's vessel-rich coefficient to its own
measured mean plus 2 SD, and to sevoflurane's, and asserts the elimination
still misses the published mean on the same side, which is what the note
says. The section still says what is left open ("So what is left is one
candidate, and this project cannot test it"). No stored value changed. The
`verify:` command now also refuses the old count.

**The `check_citations` half of the re-scope is not done here, and is
`PL-LNFG`.** `PL-PT7M`'s disposition of 2026-09-21, two days after the
re-scope, classed this item as a live-document repair rather than
check-building, and the repair is what closes it. Reaching the notes is new
checking rather than a fix to what `check_citations` reads: it reads code spans,
links and section marks, and the notes cite as bare paths and as
`docs/MODEL.md, 'Section'`, so it needs a reader of its own. That is a new
mechanism of the kind `CLAUDE.md` holds while a generator head is live, and
`PL-R417` is. Measured after this repair: the data files' 44 `note` strings
carry 48 bare path citations and the files 24 section citations, and every
one resolves, so the check would be preventive rather than corrective today.
