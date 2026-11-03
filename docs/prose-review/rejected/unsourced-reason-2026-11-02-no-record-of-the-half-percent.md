---
kind: unsourced-reason
file: docs/MODEL.md
rejected: 2026-11-02
---

## Paragraph

```text
- **Why 0.5%.** No record says how it was chosen. It dates from an earlier,
  approximate method, whose runs differed by about 0.04% in the alveolar
  concentration and by more in mixed venous. The same test also requires
  each gap to stay below 1e-14 as a fraction. Any gap that breaks 0.5% is at
  least 1e-8, so it breaks 1e-14 too. Today the 0.5% limit changes no outcome.
```

## The owner's words

"Second paragraph structure ok, but how do we not know where the 0.5% came
from? We should absolutely know where that came from" (project owner,
2026-11-02, 20:40Z, quoted in `PL-H76S`).

## Where it came from

The second bullet of the fifth version, a three-bullet list drafted for
`docs/MODEL.md` § "Step-refinement test" on `PL-70B2`'s branch (#1950) and
never committed. `git log -S 5e-3` finds where the value was set, so the
record the bullet says is missing exists. `PL-H76S` holds the diagnosis, and
the project's shared folder, at
`v0.7.0/pl-zt47/pl-70b2-paused-version6.patch`, holds the bullet as it stood.
