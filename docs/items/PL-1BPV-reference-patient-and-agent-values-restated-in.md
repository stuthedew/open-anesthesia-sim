---
id: PL-1BPV
title: Reference-patient and agent values restated in MODEL.md prose are outside the provenance check
priority: P2
effort: M
status: done
classes: infra, docs
feature: model-spec-accuracy
milestone: v0.2.12
touches: tools/doc_check.py, docs/MODEL.md
added: 2026-09-02
closed: 2026-09-02
pr: 215
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def check_prose_provenance' tools/doc_check.py
---

**Problem.** `tools/doc_check.py`'s `check_provenance` holds `docs/MODEL.md`'s
provenance table to the data files in both directions — every key in
`data/patients/*.json` and `data/agents/*.json` has exactly one row, and every
row's value matches the file. It reads only that table. The same values are
also restated in the document's *prose*, where nothing checks them:

- line 343, added by PL-004, states $`V_A = 2.5`$ L and $`\dot V_A = 4`$ L/min
  and the 37.5 s ventilation-only turnover derived from them;
- line 345, same addition, states 20.7 s for
  $`V_A/(\dot V_A + Q\lambda_{b:g})`$, which additionally depends on
  `reference_adult.json` `default_cardiac_output_l_min` and on
  `sevoflurane.json` `blood_gas_partition_coefficient`;
- line 1009 states "5% delivered, 4 L/min fresh gas" as the reference point;
- line 1685 states "Default flows are 4 L/min fresh gas with the reference
  adult's default".

The gap predates PL-004; that item added two more instances of it.

**Why it matters.** Editing `reference_adult.json` or an agent file updates
the provenance table (the check forces it) and silently leaves the prose
wrong. A reader who trusts a stale "37.5 s at the reference adult" is reading
a number for a patient the simulator no longer ships, which is the
documentation-staleness failure `CLAUDE.md` calls a safety issue rather than
tidiness. Derived values are the worse half: 20.7 s depends on four data-file
keys at once, so it goes stale in ways no single-key search would surface.

**Where.** `tools/doc_check.py` (`check_provenance` at line 580; the row
parser and the data-file walk it already has are most of the machinery),
`docs/MODEL.md`.

**Decision needed.** Decide how a prose value declares what it restates, because
that is the whole design question and the rest is mechanical. A bare regex for
numerals cannot work — `2.5` also appears as a step size at line 633 and a
flow at line 1338 — so the check would have to guess, which is the
"do not script the judgment" line `CLAUDE.md` draws. Two candidates:

1. **An explicit marker.** Prose citing a data-file value writes it in a form
   the check can parse back to a key, e.g. a trailing HTML comment naming
   `reference_adult.json · alveolar_gas_volume_l`. Decidable, no guessing, but
   it only covers values someone remembered to mark.
2. **A named-constants pass.** Extract every `<number> <unit>` adjacent to a
   term the provenance table already maps, and require a match. Catches
   unmarked instances, but needs a suppression list for coincidental numerals
   and edges toward the judgment half.

Derived values (37.5 s, 20.7 s) need a third disposition either way, since no
data file holds them: either a marked formula the check evaluates, or an
explicit decision that derived figures are recomputed by hand at review time
and the check only covers direct restatements.

Weigh this against simply not restating values in prose — cross-referencing
the provenance table instead. That costs the reader a jump and makes the
alveolar limitation at line 345 much less concrete, which is most of why it
persuades, so it is probably the wrong trade; but it is the cheapest option
and should be rejected explicitly rather than by omission.

**Decision (2026-09-02, project owner): option 1, the explicit marker; option
3 rejected outright.** Cross-referencing the table instead of restating values
would cost the reader a jump and make the alveolar limitation much less
concrete, which is most of why that passage persuades.

**The derived-value disposition, which the owner did not settle and which
neither of the two candidates in this brief got right.** Marking a formula for
the tool to evaluate needs a safe arithmetic evaluator in `tools/`, which is a
mechanism larger than its job; leaving derived figures to hand-checking at
review time leaves nothing to prompt the check. The answer taken is neither:
a `derived:` marker **records the input values the figure was computed from**,
and the tool holds those to the data files. When an input moves, it reports
that the figure needs recomputing and names it; it never computes the new
figure. That is `CLAUDE.md`'s line between the decidable half and the judgment
half, and it needs no evaluator - one marker grammar serves both kinds.

**Two things this brief got wrong about its own scope, found while marking.**

- **Lines 1009 and 1685 are not restatements and must not be marked.** Both
  read "4 L/min fresh gas", and fresh gas flow is not
  `default_alveolar_ventilation_l_min`; no data file holds it. The reference
  adult's ventilation is 4 L/min too, so binding those to that key would have
  attached a marker to a coincidence - which is precisely the failure a
  numeral-scanning check would have made, and the strongest argument for
  markers over a scan.
- **The list was short by four sites.** Also restated, and now marked: the
  solubility ordering (`blood:gas 0.42 < 0.65 < 1.3`, three agent files), the
  vaporizer maxima (`sevoflurane 8%, isoflurane 5%, desflurane 18%`), the
  solubility-sensitivity table's coefficient column, and `2% is about 1 MAC of
  sevoflurane`.

**Built.** `check_prose_provenance` in `tools/doc_check.py`, registered in
`analyze`. Every marker's keys are held to the file; a `provenance:` marker is
additionally held to the prose it sits under, so neither side can drift alone.
A document with no markers at all is an error, because silence from a check
with nothing to check reads exactly like a pass. Seven tests in
`tests/unit/test_doc_check.py`, including one pinning that stacked markers each
read the paragraph rather than the nearest marker - that walk was wrong when
first written and passed silently.

**Done when.** Either `make check` fails on a `docs/MODEL.md` prose value that
disagrees with the data file it restates, or the item is dropped with the
reasoning for leaving prose values unchecked recorded here.
