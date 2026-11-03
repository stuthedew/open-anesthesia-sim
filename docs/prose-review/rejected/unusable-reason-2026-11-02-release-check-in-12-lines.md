---
kind: unusable-reason
file: docs/MODEL.md
rejected: 2026-11-02
---

## Paragraph

```text
**The release check, and why it allows 0.5%.** The model advances in fixed
steps of 0.1 s, and a shorter step should give almost the same result. Before
each release, a test reruns the first minute of the default sevoflurane
induction with steps of 0.1 s, 0.05 s and 0.025 s. Each run's alveolar,
vessel-rich and mixed-venous concentrations must be within 0.5% of the run with
the next shorter step. The 0.5% was set for the simulator's earlier calculation
method, at about ten times the 0.04% alveolar difference that method showed.
The current method's runs agree to better than one part in a trillion
(measured 2026-10-03), so the much tighter limits above are the ones that would
catch a real error. A compartment that holds almost no agent also passes if its
two values differ by less than 0.000001 vol%, because there a tiny difference
is a large percentage.
```

## The owner's words

"I guess it's overly verbose and I still struggle to understand the why behind
it or if I am a dev or someone who forked the project, how I would use this
info to modify these values for a particular goal" (project owner, 2026-11-02,
20:30Z, on the thread for #1950).

## Where it came from

The version cut from 21 lines to 12, posted at 20:20Z as `PL-70B2`'s commit
`b5e96f2b` (#1950), in `docs/MODEL.md` § "Step-refinement test". `PL-H76S`
holds the diagnosis.
