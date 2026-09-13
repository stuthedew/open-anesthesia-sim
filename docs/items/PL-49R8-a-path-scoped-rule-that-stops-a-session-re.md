---
id: PL-49R8
title: A path-scoped rule that stops a session re-introducing a sample store once the run is a closed-form function of its definition
priority: P2
effort: S
status: ready
classes: docs
feature: numerical-domain
touches: .claude/rules
added: 2026-09-05
verify: test -f .claude/rules/run-is-its-definition.md && grep -q 'cannot be re-derived' .claude/rules/run-is-its-definition.md
---

**Problem.** "Record each sample as the simulation steps" is the obvious
design, and it is what this project did for nine releases. After `PL-T691` it
is wrong, but nothing in the tree says so at the moment a session would make
the mistake — and a session that re-introduces a sample store will do it while
believing it is being helpful, because every instinct it has points that way.

**Why it matters.** This is the one architectural regression that would undo
the whole of `PL-T691` while every test still passed: a cache of samples beside
a closed-form sampler is correct, plausible, and a second source of truth for
the same trace. `CLAUDE.md` treats a second divergent source for a displayed
clinical value as a safety failure rather than a design preference.

**The disposition, and why it is a path-scoped rule.** `CLAUDE.md`'s four
dispositions rank a `.claude/rules/*.md` with `paths:` frontmatter third:
right for a rule that matters only in part of the tree, wrong for one that must
fire before a first write. This one fires on a *read* of the sampler and chart
modules, which is exactly when a session is about to add storage to them.
Resident in `CLAUDE.md` is wrong — `PL-JK0M` has just finished cutting that
file down, and a rule about one module does not belong in the 548 lines every
session loads.

Paths: the sampler entry point from `PL-T691`, `app/chart_series.py`, and
whatever replaces `app/simulation_view.py`'s frame path.

**What it says**, as a precondition rather than a prohibition:

> The run is its definition — patient, agents and the ordered control-input
> timeline. Every compartment value at every instant is a closed-form function
> of it, so the chart evaluates rather than reads back, and there is no sample
> store to add to. Storage is warranted only for a series that **cannot be
> re-derived from its inputs**, which nothing in the simulator produces. If you
> have one, `PL-8LXM` records the prior M4 implementation, its citation, and
> the analysis of what it does and does not guarantee.

**The M4 pointer rides on the rule; it is not the reason for it.** A rule whose
only job is remembering a deleted file fires forever and changes no decision,
which is what `CLAUDE.md` calls a defect in the check. This one earns its place
every time it fires, because the regression it prevents is likelier than the
recovery it enables.

**Unblocked 2026-09-13: `PL-ZX12` landed and this item took its name.** The
rule file, the `verify:` command and the precondition's opening sentence above
now read `definition` rather than `score`, so the rule is written in the
vocabulary the tree uses rather than being born carrying the retired term - the
one thing the sequencing existed to prevent. The file to write is
`.claude/rules/run-is-its-definition.md`; nothing else about this item moved.

**Done when.** The rule exists, is scoped to those paths, states the
precondition before the pointer, and `make check`'s resident-line accounting is
unaffected because nothing was added to `CLAUDE.md`.

**Re-pointed 2026-09-08.** `PL-2FM6` has landed, so the architecture this rule
describes now exists and that blocker is satisfied. The remaining wait is
`PL-ZX12`, the `RunScore` rename: this item's rule file and its `verify:`
command both name `run-is-its-score.md`, and writing it before that rename
lands would put the retired term in the one file whose job is explaining the
architecture to a future session.
