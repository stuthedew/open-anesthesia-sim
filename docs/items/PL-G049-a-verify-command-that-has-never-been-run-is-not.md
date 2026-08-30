---
id: PL-G049
title: A `verify:` command that has never been run is not a specification, and nothing currently requires running one
status: done
priority: P2
effort: S
classes: defect, infra, session-cost
feature: delegation
touches: .claude/skills/docket/SKILL.md, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/config.py, subprojects/docket/README.md, subprojects/docket/tests, docket.toml
added: 2026-08-25
closed: 2026-08-30
commit: 4f4c8f4
verify: uv run pytest subprojects/docket/tests/test_checks.py subprojects/docket/tests/test_config.py -k verify
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

**Decided (project owner, 2026-08-30), and built.** Both halves, because the
decision above asked the wrong question: nothing can safely execute a command
out of an item file, so the mechanism cannot test the command — it can only
insist one exists, and the commissioning step has to do the running.

- `docket check` now **requires** a `verify:` command at `status: ready`, and
  never at capture. `ready` is where the item has become a commitment to do
  work and where "what would prove this?" first has an answer;
  `checks.py`'s untriaged block is what keeps capture free.
- An item may record in `not-delegable:` why no command can prove it instead.
  `PL-674D` is the case that forced this: proving a release-time fix means
  cutting a release, so the honest state is "no command can", and a rule
  without this exit would have made an item carrying an invented command
  better-formed than one telling the truth.
- The requirement is anchored to `verify_required_from` in `docket.toml`
  (2026-08-30). All 47 ready items predate it; turning them into 47 errors on
  the day the rule lands makes `docket check` useless from its first run, so
  they are reported as one grooming advisory instead. Moving the date earlier
  is how that backlog is burned down.
- The skill's triage mode now carries three canonical recipe shapes — the
  coverage gate (whole suite, dotted module), a targeted test, and the
  docs-only check — with the instruction to run the command before writing it
  into the item. The second half of this item's problem was that an author
  invented a command; a shape to copy is what stops that.

**Independently captured.** The worker filed the same finding as PL-0275 on its
own branch, from the other side of the failure. That item is a bare capture
with no brief and is superseded by this one; its branch is being left in place
rather than deleted, so nothing is lost if anyone goes looking for it.

**Second half of the same failure, and the more instructive one.** The
corrected commands were sent to the worker in chat, with an explicit "you do
not need to pull". But `docs/worker.md` tells a worker to run *the item's*
`verify:` line, and the worker followed that standing written instruction over
the ad-hoc one — which is correct of it, and is the behaviour the design
depends on. A commission lives in the item file. Correcting one anywhere else
produces a worker that is right to ignore the correction.

