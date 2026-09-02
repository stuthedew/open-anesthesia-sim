---
id: PL-KQKM
title: MODEL.md says a failed step is abandoned; the code leaves partial state
priority: P3
effort: S
status: done
classes: docs
feature: model-spec-accuracy
milestone: v0.2.11
touches: docs/MODEL.md
added: 2026-08-30
closed: 2026-09-02
pr: 204
verify: python3 tools/doc_check.py check
---

**Problem.** `docs/MODEL.md:564-566` says that when a step fails, "the step is
abandoned, simulation time does not advance, and the caller must stop the run
rather than read the partially applied state as a result". Only the second
clause is true. `AgentUptakeSystem.advance`'s own docstring
(`core/uptake_system.py:132-135`) says the opposite of the first:
"Compartment state is left partway through the step and must not be read as a
simulation result." Time is not advanced; the compartments are.

**Why it matters.** "Abandoned" reads as transactional — as though the failure
left a clean state a caller could inspect, log, or resume from. It cannot. The
document and the docstring disagree on the one point that determines what a
caller may safely do after a halt, and the document is the one a reader of the
model reaches first.

**Where.** `docs/MODEL.md:564-566`; `core/uptake_system.py:132-135`.

**Approach.** Correct the document to match the docstring: the step is
*abandoned as a result* — time does not advance and the state must not be read
— while compartment state is left partway through. Cite PL-026 (make the
simulation step transactional so a halt leaves no partial state) there as the
work that would make the original wording true, so the correction records why
the weaker guarantee is the current one rather than reading as a lowered bar.

**Scope note.** An instance of the class PL-036 describes; per that item's
Decided scope it is fixed here and cited there as evidence, not folded into it.

**Done when.** `docs/MODEL.md`'s failed-step paragraph states what the
implementation actually guarantees and names PL-026 as the item that would
strengthen it.

**Outcome (2026-09-02).** Resolved in the other direction, by `PL-026` (make
the simulation step transactional), on the same branch and in the same commit.
This item planned to weaken the document to match the code — "the step is
abandoned *as a result*, while compartment state is left partway through" —
and to cite `PL-026` as the work that would make the original wording true.
`PL-026` landed first, so the document was corrected upward instead:
`AgentUptakeSystem.advance()` now captures every dynamic value before the step
and restores it on failure, and the paragraph says the step is rolled back in
full and the caller is left holding the last completed step. There is no
weaker guarantee left to record, and nothing to cite `PL-026` as future work
for.

`docs/MODEL.md` also gained a "Step atomicity" section stating the contract in
one place, which is what the document had been missing: the failed-step
paragraph was carrying a guarantee that belonged to the numerical method, in a
section about the capacity guard.
