---
kind: length
file: docs/MODEL.md
rejected: 2026-11-02
---

## Paragraph

```text
**The release check, and why it allows 0.5%.** The simulator moves the model
forward in fixed time steps, normally 0.1 s long. A shorter step should give
almost the same result. If it does not, the step is too long. Before each
release, the test runs the first minute of the default sevoflurane induction
three times, with steps of 0.1 s, 0.05 s and 0.025 s. In each run, the
alveolar, vessel-rich and mixed-venous concentrations must be within 0.5% of
the run with the next shorter step. The 0.5% margin was set for the
simulator's earlier calculation method. With that method, the alveolar
concentrations of the 0.1 s and 0.025 s runs differed by about 0.04%, so the
margin allowed about ten times that difference. The check compares each run
only with the next shorter step. Under the earlier method, a direct comparison
of the 0.1 s run with the 0.025 s run would have failed. Their mixed-venous
concentrations, which have barely begun to rise at one minute, differed by
0.55%. With the current method, the three runs agree to better than one part
in a trillion (measured 2026-10-03). So this check is now only a coarse safety
net. The much tighter limit in the paragraphs above is the one that would
catch a real error. One extra rule covers a compartment that still holds
almost no agent. There, a tiny difference can be a large percentage, so a
percentage means little. Two values for such a compartment also pass if they
differ by less than 0.000001 vol%, which is one part in a hundred million of
the gas.
```

## The owner's words

"Way too verbose" (project owner, 2026-11-02, 20:17Z, on the thread for
#1950).

## Where it came from

A rewrite for a clinician that replaced both the tolerance paragraph and the
paragraph giving its reason. It was posted at 20:10Z as `PL-70B2`'s commit
`7834b64a` (#1950), in `docs/MODEL.md` § "Step-refinement test". `PL-H76S`
holds the diagnosis.
