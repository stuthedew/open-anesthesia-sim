---
id: PL-73G7
title: Explain desflurane's opposite-sign washout disagreement once rebreathing is removed
status: untriaged
added: 2026-09-06
---

**Problem.** Measured 2026-09-06 while building the elimination comparison in
`tests/reference/test_published_wash_in.py`: with rebreathing removed - the
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

**Blocked on.** `PL-W21J` (a non-rebreathing elimination mode). Until the model
can be run at an inspired fraction of zero through a supported path, the -2.40
SD figure comes from a diagnostic that writes circuit state directly, which is
not a number to change a parameter on.

**Where.** `src/anesthesia_sim/data/agents/desflurane.json`,
`docs/MODEL.md` "Parameter provenance", and the elimination comparison in
`tests/reference/test_published_wash_in.py`.

**Done when.** The sign and size of desflurane's residual are either explained
against the primary literature or recorded in `docs/MODEL.md` as a known
disagreement with its cause named.
