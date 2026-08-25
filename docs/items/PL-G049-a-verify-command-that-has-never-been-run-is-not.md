---
id: PL-G049
title: A `verify:` command that has never been run is not a specification, and nothing currently requires running one
status: untriaged
added: 2026-08-25
---

**Problem.** All six guard-coverage items shipped with a `verify:` command
that had never been executed, and all six were wrong in the same two ways:
`--cov=` was given a file path where `pytest-cov` expects a module name, and
the run was scoped to a single test file, which makes lines covered by the
rest of the suite read as uncovered and puts `--cov-fail-under=100` out of
reach. Nothing caught it. `docket check` validated the field's shape, not
whether the command runs or means anything.

**Why it matters.** In the delegation design the `verify:` command *is* the
specification — it is what makes an item safe to hand to a cheaper model
without reading the diff. An unrun command is a specification nobody has
tested, and it fails at the worst moment: after a worker has done the work,
where it costs a round trip and the owner's attention. Here it cost both, and
the only reason it was not worse is that the broken form exits non-zero rather
than reporting a false pass.

**Where.** `subprojects/docket/src/docket/checks.py`, or PL-D7JQ's
`docket verify`.

**Decision needed.** Whether anything can check this without running arbitrary
commands from item files, which is a real hazard and not one to wave through.
Options worth weighing: `docket verify` refusing an item whose command has no
recorded successful run; a `verify-checked:` date field the commissioning
session sets by hand; or accepting that this is judgment and putting it in the
skill's commissioning step instead of in code.

**Note.** The failure was caught by a worker following the stop-rule in
`docs/worker.md` rather than guessing — which is the design working, but only
after the cost had been paid.

**Done when.** Either a mechanism prevents an unrun `verify:` command reaching
a worker, or the commissioning step requires running it and that is written
down where a session will read it.
