---
id: PL-JDX0
title: State the coupled system's modal time constants in docs/MODEL.md, so the timescales the model resolves are readable
status: untriaged
added: 2026-09-05
classes: docs
feature: numerical-domain
touches: docs/MODEL.md
---

**Problem.** `docs/MODEL.md` states two single-mechanism time constants under
"Alveolar gas" — the ventilation-only turnover $`V_A/\dot V_A`$ = 37.5 s and
the ventilation-plus-perfusion relaxation $`V_A/(\dot V_A + Q\lambda_{b:g})`$
= 20.7 s — and then correctly says that neither is the time constant of the
coupled system, because "the alveolar trajectory is a sum of exponentials over
all six modeled compartments and no single constant describes it". It never
states what those six exponentials are. The document therefore says what the
timescale is *not*, and stops.

**Why it matters.** The spectrum is the quantity that answers every question
about temporal resolution: what integration step the physiology needs, what
recording cadence is enough, what a chart at a given time base can and cannot
show, and how stiff the system is. Without it, each of those has to be
re-derived — the project owner asked on 2026-09-05 whether the shipped 10 Hz
sampling is finer than the model needs, and the document could not answer it.
It is also standard practice for a linear compartmental model: the modal
decomposition is how such a model's behaviour is normally reported.

**The measurement (2026-09-05).** The homogeneous system matrix was assembled
from the "Governing equations" section and `data/patients/reference_adult.json`,
and its eigenvalues taken by QR iteration in pure stdlib. Time constants
$`\tau = -1/\lambda`$, in seconds, per agent:

| Settings | Agent | $`\tau_1`$ | $`\tau_2`$ | $`\tau_3`$ | $`\tau_4`$ | $`\tau_5`$ | $`\tau_6`$ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| default (FGF 4, $`\dot V_A`$ 4, Q 5) | sevoflurane | 12.73 | 15.86 | 63.42 | 362.41 | 10 342 | 166 739 |
| | isoflurane | 12.12 | 12.66 | 54.69 | 422.01 | 11 449 | 187 471 |
| | desflurane | 12.44 | 18.12 | 66.48 | 261.42 | 6 016 | 95 492 |
| envelope corner (FGF 10, $`\dot V_A`$ 12, Q 10) | sevoflurane | 6.18 | 6.29 | 27.34 | 159.54 | 4 892 | 81 340 |
| | isoflurane | 5.33 | 5.87 | 22.51 | 188.68 | 5 274 | 89 486 |
| | desflurane | 6.05 | 6.94 | 29.31 | 113.54 | 2 887 | 46 975 |

So the fastest mode is 12.1-12.7 s at the reference adult's defaults and
5.3-6.2 s at the fastest corner the four sliders can reach; the slowest is the
fat mode at 13 to 52 hours. The stiffness ratio is roughly $`10^4`$, which is
also why an exact step (`PL-GS5X`) is the right solver for this system.

**Where.** `docs/MODEL.md` § "Alveolar gas", immediately after the paragraph
that rejects any single-mechanism constant — that paragraph is what this
completes, so the table belongs beside it rather than in a section of its own.
Cross-reference from § "Supported simulation step", which currently justifies
the step entirely from solver error with no statement of the physical
timescales it is resolving.

**Done when.** `docs/MODEL.md` carries the six modal time constants at the
reference adult's defaults and at the settings-envelope corner, for every
shipped agent, with the assembly of the system matrix stated so a reader can
reproduce them from the equations already in the document; the derivation is
marked with the `<!-- derived: -->` provenance comments `tools/doc_check.py`
reads, so a change to the patient or agent files reports the table as needing
recomputation; and § "Supported simulation step" cites the fastest mode as the
physical timescale the step resolves.

**Sequencing.** Independent of `PL-GS5X` (replace the operator split with the
exact matrix exponential) but cheaper after it: that item assembles this very
matrix in `core/`, so the table can then be generated from shipped code rather
than from a transcription. Worth doing either way — the numbers do not move.
