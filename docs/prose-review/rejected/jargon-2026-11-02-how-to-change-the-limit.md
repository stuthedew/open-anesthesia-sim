---
kind: jargon
file: docs/MODEL.md
rejected: 2026-11-02
---

## Paragraph

```text
- **How to change it.** A fork with an approximate method fails 1e-14 even
  when its arithmetic is correct: a first-order method shows gaps near
  1.4e-11. Relax 1e-14, and 0.5% becomes the working check. Set it above the
  method's own gaps at these steps and below a difference a learner could
  see. The constants are in `tests/reference/test_sevo_patient.py`.
```

## The owner's words

"And the last paragraph is starting to be unintelligible again" (project
owner, 2026-11-02, 20:40Z, quoted in `PL-H76S`).

## Where it came from

The third bullet of the fifth version, a three-bullet list drafted for
`docs/MODEL.md` § "Step-refinement test" on `PL-70B2`'s branch (#1950) and
never committed. It was written for a developer who wants to change the
limit. `PL-H76S` holds the diagnosis, and the project's shared folder, at
`v0.7.0/pl-zt47/pl-70b2-paused-version6.patch`, holds the bullet as it stood.
