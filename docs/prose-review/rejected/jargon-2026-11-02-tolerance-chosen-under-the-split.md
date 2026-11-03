---
kind: jargon
file: docs/MODEL.md
rejected: 2026-11-02
---

## Paragraph

```text
The 5e-3 relative tolerance was chosen when the simulator used the operator
split. At that time, the split showed a relative gap of 4e-4 in the alveolar
fraction between steps of 0.1 s and 0.025 s, and 5e-3 is about ten times that
gap. The tolerance is kept as a coarse check, because with the exact step the
same comparison gives gaps of about 1.4e-13 relative (measured 2026-10-03).
The 1e-8 absolute tolerance covers a fraction so close to zero that a relative
gap means little. For such a fraction, a negligible difference still passes.
```

## The owner's words

"this is still unintelligible to a human" (project owner, 2026-11-02, 20:03Z,
on the thread for #1950), and "was this written with the plain language
guidelines? This is still unintelligible" (20:04Z).

## Where it came from

A paragraph added to give the reason for the step-refinement tolerance,
posted for review at 20:02Z as `PL-70B2`'s commit `ba9f6759` (#1950), in
`docs/MODEL.md` § "Step-refinement test". `PL-H76S` holds the diagnosis.
