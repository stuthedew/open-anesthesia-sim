---
id: PL-B043
title: Let a detector fill the queue with the mechanical findings nobody thinks to file
status: needs-decision
priority: P2
effort: M
classes: infra, session-cost
touches: tools/
added: 2026-08-25
---

**Problem.** A category of real, valuable work is invisible to the queue
because nobody has an idea that produces it. The untested guards surfaced only
because a coverage report was run; PL-69J3's ten inert `noqa` directives
surfaced only because `ruff --select RUF100` was run; PL-JL24 surfaced only
because a hash was orphaned in front of someone. Nobody sits down and thinks
"I should file an item about untested capacity guards."

**Why it matters.** This category has a second property: findings enumerable by
a command are exactly the findings provable by a command, which makes them the
natural supply for the delegation tier. But the value does not depend on
delegation — a detector that lists what needs doing is worth having whether a
cheap model or the strongest one works the result.

**What it might cover.** Uncovered `raise`/`except` branches; `noqa` directives
naming rules the project does not enable, and enabled-rule suppressions with no
recorded reason; recorded `commit:` hashes that are unreachable (PL-68XK,
PL-JL24); open items declaring no `touches`, which `concurrent` reports as
unanalysed rather than safe; documentation citations that resolve to nothing
(already done by `tools/doc_check.py`, which is the model to copy).

**Decision needed.** Whether a detector *files* items or merely *reports* them.
Filing automatically risks a queue nobody chose, and `docket new` is cheap
enough that the reporting half may be the whole value. Also whether this is one
tool or several — `doc_check.py` sets the precedent of one script per subject
rather than a general framework.

**Note on scope discipline.** This must not become a machine for manufacturing
delegable work. The test for anything built here is whether its output would be
worth having if no cheap model ever ran it. If the answer is no, the finding is
not real and the detector is generating homework.

**Done when.** Scoped into items, or dropped with the reason recorded.
