---
id: PL-1BPV
title: Reference-patient and agent values restated in MODEL.md prose are outside the provenance check
status: untriaged
added: 2026-09-02
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

**First step.** Decide how a prose value declares what it restates, because
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

**Done when.** Either `make check` fails on a `docs/MODEL.md` prose value that
disagrees with the data file it restates, or the item is dropped with the
reasoning for leaving prose values unchecked recorded here.
