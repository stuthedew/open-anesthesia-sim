---
id: PL-0NQ1
title: The reference patient's cited sources disagree on vessel-rich perfusion
status: untriaged
added: 2026-09-01
verify: python3 tools/doc_check.py check && grep -qF '75.8' src/anesthesia_sim/data/patients/reference_adult.json
---

**Problem.** `src/anesthesia_sim/data/patients/reference_adult.json` stores
tissue perfusion fractions 0.76 / 0.18 / 0.06 and its first `sources` entry
attributes them to the Gas Man Workbook, with the note recording "flow
percentages 76/18/6".

Table 1 of De Wolf et al. 2012 — the same table all twelve partition
coefficients come from — gives **Blood flow (%) 75.8 / 18 / 6**, and, in the
same table, the tissue volumes 6 / 33 / 14.5 L that this file also stores.
75.8 + 18 + 6 = 99.8, not 100. So one published table is the source of the
tissue volumes this file records and of a vessel-rich flow percentage that
differs from the one it records, and nothing in the file says so.

**A correction to the finding as relayed.** The review described this file as
citing "the Gas Man Workbook and the De Wolf paper". It does not: its two
sources are the Gas Man Workbook (`https://gasmanweb.com/Workbook.pdf`) and
Meybohm P, et al. 2021 (PMC7943506). De Wolf is cited in the three *agent*
files, not here. That makes the finding sharper rather than weaker — the table
carrying the discrepant number is one this file does not cite at all, while
three sibling data files do — but a session acting on this must check the
right table, so the correction is recorded rather than smoothed over.

**Compounding it, the schema cannot represent the published figure.**
`_ReferenceAdultPayload._perfusion_fractions_must_sum_to_one`
(`src/anesthesia_sim/core/parameters.py:274-286`) rejects any set whose sum
differs from 1.0 by more than `FLOW_FRACTION_TOLERANCE = 1e-12` (`:36`);
`core/patient.py:20,36` enforces the same bound independently. 0.758 + 0.18 +
0.06 = 0.998 fails both. So even a session that decided the published figure
was the right one could not enter it, and would rediscover that only after
editing the data file.

**Why it matters.** The numerical effect is negligible and should be recorded
as such: the vessel-rich time constant $`\tau = V_i/(Q_i\lambda)`$ scales
inversely with perfusion, so 0.76 against 0.758 moves it by 0.26% — far inside
any interpretation a learner would draw from the curve.

The provenance effect is what matters. One file cites two sources, attributes
a number to the one that cannot be checked from a URL, records a value a third
source contradicts in the same table that supplied its sibling parameters, and
has a hard schema constraint silently forcing the departure. `CLAUDE.md`
requires clinically meaningful transformations to be versioned with recorded
provenance and requires a reader to be able to determine why a constant exists.
A reader who pulls the one reachable citation here reaches a different number
and has nothing telling them the difference was noticed, decided, or forced.

**Where.**

- `src/anesthesia_sim/data/patients/reference_adult.json` — the stored
  fractions and the first `sources` entry's `note`.
- `src/anesthesia_sim/core/parameters.py:36,274-286` and
  `src/anesthesia_sim/core/patient.py:20,36` — the sum-to-one constraint,
  read not changed.
- `docs/MODEL.md` — the parameter provenance section, if the resolution needs
  a line there too.

**Approach.** Most likely one or two sentences in the `note`, no value change:
say which source 0.76 comes from, that De Wolf Table 1 publishes 75.8, that
75.8/18/6 sums to 99.8% and the schema requires exactly 1.0, and that 0.76 is
the normalized figure adopted for that reason. Add De Wolf as a third
`sources` entry if the volumes are in fact taken from that same table, since
the file would then be citing the paper it actually draws from.

Confirm against the Gas Man Workbook PDF
(`https://gasmanweb.com/Workbook.pdf`) if it can be reached, since the current
note's "76/18/6" is attributed to it and that attribution has not been
checked. If the Workbook genuinely prints 76, the two sources simply differ
and the note says so; if it prints 75.8 too, the note is wrong as well as
unreconciled, and the item is larger.

Do not relax `FLOW_FRACTION_TOLERANCE`. A schema that admitted a set summing
to 0.998 would let a real transcription error through silently, which is worth
more than representing a published rounding exactly.

**Found.** External multi-domain review, relayed by the project owner
2026-09-01. The file's actual `sources` list, the constraint and its
tolerance, and De Wolf Table 1's blood-flow row were confirmed against the
tree and against the PubMed Central full text (PMC3502091,
https://doi.org/10.1186/1471-2253-12-22) in this session.

**Done when.** `reference_adult.json`'s note records which source each
perfusion fraction comes from, that the published 75.8 sums to 99.8% and that
the sum-to-one constraint is why it was not used verbatim; the cited sources
match the numbers actually drawn from them; and no stored value changed.
