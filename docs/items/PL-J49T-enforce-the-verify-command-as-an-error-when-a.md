---
id: PL-J49T
title: "Enforce the verify: command as an error when a grandfathered item is closed, so the burn-down stops depending on anyone reading an advisory"
status: done
priority: P3
effort: S
classes: infra, session-cost
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/config.py, subprojects/docket/tests/test_checks.py, docket.toml, .claude/skills/docket/SKILL.md
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_closing_a_grandfathered_item_demands_the_command_the_ready_gate_never_could' subprojects/docket/tests/test_checks.py
added: 2026-09-03
closed: 2026-09-03
---

**Problem.** 22 `ready` items predate `verify_required_from` and name no
`verify:` command. `PL-5YK8` narrowed the resulting advisory to the one or two
items `docket next` is about to offer, which fixed the nag. It did not make
the burn-down happen: the advisory only *asks*, and nothing detected an item
leaving the grandfathered set without gaining a command. The set shrank when a
session chose to read three lines of `make check` output and act.

**Why it matters.** `CLAUDE.md` says to find the decidable part of a mechanism
and put it in code, and not to script the judgment. This advisory had both
halves tangled into one signal:

- *Judgment*: what the command should be. Unscriptable, and `PL-5YK8`
  established why - a command written away from its work is wrong, which all
  six wrong ones in this store's history demonstrate.
- *Decidable*: whether a closed item carries one. A yes/no on a frontmatter
  field.

The decidable half was delivered as prose that repeats every run and works
only if read. Demonstrated on 2026-09-03: a session filtered `make check`
through `grep` for summary lines and read "1 advisory" across several runs
without reading the advisory, while the item count moved 116 to 118. The
content had not changed, so nothing was lost - but the method would not have
noticed if it had, which is the failure mode `CLAUDE.md` predicts.

**Decision needed.** *Answered by the project owner, 2026-09-03: option 1.*
An error at close, with no grandfather exemption - which is the whole point,
since exempting them is what leaves the 22 untouched. The alternatives were to
exempt them anyway (preserving the promise and fixing nothing) or to leave the
advisory alone and let the set drain on its own.

**Done when.** Closing an item without a command fails `docket check` with a
message naming the field and the `not-delegable:` alternative, and a test
covers both the refusal and the escape.

**Done.** `verify_required_at_close_from` in `docket.toml`, read by
`config.py` and enforced by `_verify_required_at_close` in `checks.py`: an
item with `status: done` whose `closed:` falls on or after the date must name
a `verify:` or a `not-delegable:` reason. `dropped` is excluded - an item
that will not be done carries a `reason`, not a command for work nobody did.

**Keyed on `closed:` rather than `added:`, which is the entire design.** That
is what lets it reach items the opening gate grandfathers: they are exempt at
`ready` and stay exempt however long they sit there, and closing one is the
first moment its command can be written *having been run*, which is the
objection that earned the exemption. At that moment the objection lapses, so
the exemption lapses with it.

**Set to the day it landed, so it touches nothing already closed.** Measured
before choosing the date: 182 items are `done` and 54 of them carry no
command, several closed as recently as the day before. Backfilling those would
mean writing commands with nothing left to run them against - the failure
`PL-5YK8` refused at the other end of the item's life - so history is left
alone and the rule applies forward only.

Five tests in `subprojects/docket/tests/test_checks.py`. The one that carries
the claim,
`test_closing_a_grandfathered_item_demands_the_command_the_ready_gate_never_could`,
was watched failing with the gate reverted and the config left in place, so
the failure is the missing rule rather than a missing attribute. The other
four are the escapes and the off-cases - `not-delegable:`, a pre-cutover
closure, a `dropped` item, and a project that declares no cutover - and pass
either way by design, pinning what the rule must *not* do.

This item is the first one its own rule holds: captured and closed on
2026-09-03, so `docket check` required the command above before it could be
marked done.
