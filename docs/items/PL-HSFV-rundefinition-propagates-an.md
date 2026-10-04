---
id: PL-HSFV
title: RunDefinition propagates an UptakeEquationSettings whose flows are outside the supported ranges - cardiac output 1000 L/min, a hundred times the supported maximum, ran on 2026-10-04 - because the settings record checks only that the tissue flows sum to cardiac output, and the range guards run only in the compartments' constructors and setters, which a run built from a settings record never calls
status: untriaged
feature: numerical-domain
added: 2026-10-04
---

**Problem.** RunDefinition propagates an UptakeEquationSettings whose flows are outside the supported ranges - cardiac output 1000 L/min, a hundred times the supported maximum, ran on 2026-10-04 - because the settings record checks only that the tissue flows sum to cardiac output, and the range guards run only in the compartments' constructors and setters, which a run built from a settings record never calls

**Recommended fix, 2026-10-04: slice 1 of `PL-51B7`, not a check of its
own.** **Recommendation:** close this with `PL-51B7`'s first slice. That slice
types `UptakeEquationSettings`'s three flow fields, so a record holding an
out-of-range flow cannot be built. The narrow alternative, recommended when
this was filed, was a range check added to the record's `__post_init__`. It
is withdrawn, because the typed fields would delete it, and this project does
the durable fix once rather than the cheap one twice. Until the slice lands,
the gap stands. The application never builds a run this way, since its flows
come through the compartments' checked setters, but a notebook or a test can,
and it gets finite, plausible numbers from outside the range the model is
claimed over.
