---
id: PL-73G7
title: Explain desflurane's opposite-sign washout disagreement once rebreathing is removed
priority: P1
effort: M
status: done
classes: science, docs
feature: numerical-domain
milestone: v0.4.10
touches: src/anesthesia_sim/data/agents/desflurane.json, docs/MODEL.md, tests/reference/test_published_wash_in_and_elimination.py
blocked-by: PL-W21J
added: 2026-09-06
closed: 2026-09-08
pr: 464
verify: uv run pytest tests/reference/test_published_wash_in.py && grep -q 'def test_no_measured_tissue_solubility_reaches_desflurane_s_published_elimination' tests/reference/test_published_wash_in.py
---

**Problem.** Measured 2026-09-06 while building the elimination comparison in
`tests/reference/test_published_wash_in_and_elimination.py`: with rebreathing removed - the
inspired fraction held at zero through the elimination, which is a diagnostic
rather than a supported configuration - sevoflurane and isoflurane land at -0.25
and +0.54 SD of their published five-minute `F_A/F_A0`, while desflurane lands
at -2.40 SD. Desflurane washes out too *fast*, and it is the only agent whose
residual sits on the other side of the published mean.

**Why it matters.** It is the one signal in either direction that looks like a
parameter problem rather than an apparatus one, and it is in the direction no
gate here constrains. Desflurane is also the agent whose wash-in row has the
least room, at +0.79 SD against the tightest published spread of the three, so
a solubility or tissue-capacity change made to close the washout gap would have
to be checked against the wash-in comparison in the same pass.

**Blocked on.** `PL-W21J` (a test-only open-circuit driver for the elimination
comparison). Until the comparison can be run at an inspired fraction of zero
from `tests/reference/`, the -2.40 SD figure comes from a diagnostic that
writes circuit state directly, which is not a number to change a parameter on.
`#415` settled that it is a driver rather than a supported model mode, so the
path this waits on is a test fixture and the shipped simulator still cannot be
put in that condition - which is a limit on what the answer here can claim.

**Where.** `src/anesthesia_sim/data/agents/desflurane.json`,
`docs/MODEL.md` "Parameter provenance", and the elimination comparison in
`tests/reference/test_published_wash_in_and_elimination.py`.

**Done when.** The sign and size of desflurane's residual are either explained
against the primary literature or recorded in `docs/MODEL.md` as a known
disagreement with its cause named.
