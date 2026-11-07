---
kind: unclear
file: docs/MODEL.md
rejected: 2026-11-07
---

## Paragraph

```text
**The three maxima come from two classes of vaporizer.** The sevoflurane and isoflurane maxima
are those of variable-bypass dials. Desflurane's is the top of the Tec 6's range, and a Tec 6 is
a heated gas–vapour blender. The model fixes ambient pressure at 760 mmHg (§ "Assumptions"). At
that pressure, the same dial setting on either class gives the same partial pressure, so the model
does not need to know which class a limit came from. The classes would differ only at reduced
ambient pressure, which is not modelled (§ "Known limitations").
```

## The owner's words

"“The three maxima come from two classes of vaporizer.” what does that mean?" and, asked
whether to log it as a rejected paragraph, "Yes. Reject" (project owner, 2026-11-07, 21:59Z
and 22:04Z, in the thread "Fix the copy editor dropping requirements").

## Where it came from

The copy editor's edit of `docs/MODEL.md` § "Delivery-limit and MAC parameters", as the
section stood before `#2049`, in `PL-F0Q2`'s third debug run of that section (the project's
shared folder, `v0.7.0/copy-editor-f0q2/runs/fix3-p043/edited.md`). The owner had approved the
section at 20:13Z, before asking about this paragraph. The copy editor kept the bold lead's
first clause from the original, cut its second ("which this model would need to tell apart
only away from sea level"), and cut the three values from the next sentence. The lead never
says that the maxima are the dial maxima, and the paragraph never says how the two classes
differ.
