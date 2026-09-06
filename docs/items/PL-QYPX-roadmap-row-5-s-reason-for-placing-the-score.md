---
id: PL-QYPX
title: ROADMAP row 5's reason for placing the score architecture in v0.5.0 conflates forking's element-wise property with the sample store's memory cost
priority: P3
effort: S
status: done
classes: docs, defect
touches: ROADMAP.md
added: 2026-09-06
closed: 2026-09-06
verify: python3 tools/doc_check.py check && grep -qF 'stops being a property a test has to establish' ROADMAP.md
---

**Problem.** "The timeline" row 5 justified placing the score architecture in
v0.5.0 partly like this: item 12's required property - a branch reproduces its
parent element-wise at every recorded sample - "is nearly free once a run is a
closed-form function of its control timeline, and expensive against a recorded
sample store."

The second half is not true. v0.4.0's own "Designed for forking" subsection
already preserves that property against the sample store it shipped with:
elapsed time is the step count times the run's step, the run loop never catches
up to the wall clock, and the control-input timeline makes a point between
samples reachable. On top of that, a branch that simply copies its parent's
recorded samples up to the branch point satisfies the property trivially,
because the values are the same values.

**Why it matters.** The placement is right and the argument for it was wrong,
which is the harder kind of error to catch: nobody re-examines a conclusion
they agree with. What is actually expensive against a recorded sample store is
holding *two* of them - `PL-011`'s dropped growth debt doubled by comparison -
and what the score architecture uniquely buys is that a branch's prefix is not
a copy at all but the parent's own score, so the property has no test surface
to get wrong. Stated correctly the placement is better supported than it was.

**Where.** `ROADMAP.md`, "The timeline" row 5.

**Done when.** Row 5 states the memory cost as the expense and the
same-object property as what the score architecture uniquely provides, and no
longer claims the element-wise property is unreachable against a sample store.

**Closed 2026-09-06** in the change that scoped v0.5.0. Row 5 now carries the
correction and marks the superseded sentence, so a reader meeting the old
argument elsewhere can see it was withdrawn rather than forgotten.
