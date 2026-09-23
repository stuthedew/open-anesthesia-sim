---
id: PL-1P5V
title: verify: is an opaque shell string, so each non-discriminating shape is refused by its own rule after it fails: PL-6TP8's contract did not stop the mechanism, and PL-09G9, PL-205P, PL-J3WK, PL-RR1N and PL-R812 arrived after it closed
priority: P2
effort: M
status: done
classes: defect, infra
feature: verify-command-meaning
milestone: v0.5.8
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, docket.toml, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_vcs_silence.py, subprojects/docket/README.md, .claude/skills/docket/modes/triage.md, ROADMAP.md, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the first 2026-09-23 triage pass
added: 2026-09-22
closed: 2026-09-23
pr: 949
payoff: a new way for a verify: command to prove nothing is refused when it is written, instead of costing a red main, a dead command or a misread before it earns a rule of its own
verify: grep -q 'def test_a_verify_command_outside_the_prescribed_shapes_is_refused' subprojects/docket/tests/test_checks.py
root-cause-of: PL-0QRP, PL-CWD4, PL-09G9, PL-RR1N, PL-205P, PL-J3WK, PL-R812
generator: spent - a verify: written from 2026-09-24 is one of the admitted shapes or is refused when it is written, on the branch that writes it, so a new shape joins the list by an argument in checks.py instead of by failing first; the per-shape rules guard the grandfathered commands until they drain
---

**Problem.** verify: is an opaque shell string, so each non-discriminating shape is refused by its own rule after it fails: PL-6TP8's contract did not stop the mechanism, and PL-09G9, PL-205P, PL-J3WK, PL-RR1N and PL-R812 arrived after it closed

**Reproduced 2026-09-23.** `git log --diff-filter=A` on each member's file
dates all seven after `PL-6TP8`'s close commit `cb83dcb1` (2026-09-18 23:59
-0500, `#684`), the earliest 66 minutes after it. The mechanism stands on
today's tree: `bin/docket check` exits 0 with seven per-shape predicates over
the string in place - `_redundant_pytest_clause`, `_k_selector_clause`,
`never_fails`, `_check_shared_verify`, `reaches_outside_tree`,
`reenters_verify`, `reads_check_output` - and a shape none of them reads still
passes: fed a pytest node id ahead of or behind a `grep`, both pytest rules
return `None` (`PL-R812`'s probe).

**The members, confirmed 2026-09-23 against each brief.** Each is a shape the
string admits and no rule read until it misreported:

| Item | Added | The shape | What it cost before it had a rule |
| --- | --- | --- | --- |
| `PL-0QRP` | 09-19, `#692` | counts a symbol (`grep -c … -ge N`) | `PL-R0P3`'s passed with none of the work done |
| `PL-CWD4` | 09-19, `#692` | a target that vanished, so it can never pass | `PL-4PC5` carried a dead command five days |
| `PL-09G9` | 09-19, `#711` | a pytest run beside the discriminator | 82 of 180 open commands; 59% of the replay |
| `PL-RR1N` | 09-20, `#748` | a phrase the document's wrapping splits | `PL-FG9D`'s finished work read as absent |
| `PL-205P` | 09-20, `#753` | reads the remote | `main` red on ten commits in two spans |
| `PL-J3WK` | 09-20, `#802` | a literal `true`; one command on three items | three placeholders passed locally, failed CI |
| `PL-R812` | 09-22, `#907` | a pytest node id | exit 4 before the work; no rule reads it |

The title named five; `PL-0QRP` and `PL-CWD4` join them and none is dropped.
`PL-J3WK` is also `PL-0HPV`'s, for its `make check`-against-CI half. Left out:
`PL-BX1C` and `PL-23C7` (a dropped item's command still being run is the
consumer's lifecycle, not the command's shape), `PL-FZ58` (a clause's cost,
which `PL-6TP8` itself left out), and the `docket verify` diff-check items
(`PL-G21K`'s).

**Why it matters.** A list of refused shapes never closes. Each rule refuses
the shape that has just failed, and the next one costs its own red `main`, dead
command or misread first: seven items in four days, after the head meant to
settle the field had closed. The `-k` rule names its own successor - its
docstring leaves `-m` unread because "no command in this store has ever carried
one".

**Generator check.** Head, recording a closed head's mechanism still
producing: seven instances of `PL-6TP8`'s (what a `verify:` exit proves), all
filed after it closed. `PL-6TP8` settled what an exit may be read to mean; it
left what a command may *be* to a table in the skill, and that half is what
keeps producing members.

**The fix at the mechanism: refuse by default, not after the fact.** From a
cutover date, `docket set` and `docket check` accept a `verify:` only in the
shapes the triage table already prescribes ("Copy one of these shapes rather
than inventing one"): a `grep -q` for the `def` of a test the work adds, a
`grep -qF` for a phrase it adds, several of those joined by `&&`, and the
whole-suite `--cov` run. Anything else is refused unless the item says in
`not-delegable:` why no such command can prove it. A new shape is then refused
when it is written, and no new per-shape rule is needed; the seven existing
ones keep guarding the grandfathered commands until they drain. Measured over
the 215 open commands on 2026-09-23: 163 (76%) are already one or more of the
two `grep` shapes once a legacy trailing clause is stripped, about 25 (12%)
assert an absence with `! grep`, and about 25 (12%) are pytest runs, tool calls
or scripts. Building it is one parser and cutover date (`checks.py`,
`config.py`, `docket.toml`), the refusal in `docket set`, its tests, and the
README contract and the triage table reworded from "copy one of these" to "only
these". It is a new check, which `CLAUDE.md`'s pause allows because it fixes a
live generator; it adds no field.

The alternative is a **structured field**: typed entries (`adds-test:
path::name`, `adds-text: file: phrase`, `coverage: module`) that the tool
evaluates itself, which would also match across line-wrapping (`PL-RR1N`) and
see a vanished target statically (`PL-CWD4`). It re-specifies a field the
owner ratified on 2026-09-19 (`PL-6TP8`'s shape half) and touches every
consumer in `verify.py` and `checks.py` and every open command, and over the
allowlist it buys mainly those two members.

**Decision needed.** Which fix to build: the allowlist on today's string, or
the structured field.

**Recommended: the allowlist.** It stops new shapes arriving for the cost of
one parser, keeps the ratified contract, and repairs the old commands as each
is started, as `PL-09G9` and `PL-Q8RQ` already do. A structured field can
follow if the allowed shapes turn out to need the tool rather than the shell to
evaluate them. Whether `! grep` is allowed is the work's to settle, not the
decision's: 25 open commands use it, and `PL-J3WK` found it passes on any typo
in its pattern.

**Done when.** A `verify:` shape nobody has argued for is refused when it is
written rather than found after it misreports, and the open members -
`PL-0QRP`, `PL-CWD4`, `PL-RR1N` - are re-pointed at the fix or dropped against
it.

**Decided 2026-09-23: the allowlist** (project owner, 2026-09-23, ratified,
over a structured `verify:` field). Build the parser that accepts the shapes
the triage table prescribes and refuses any other shape at write time unless
`not-delegable:` says why none fits. Settle `! grep` as part of that work, as
the recommendation says.

**Built 2026-09-23.** `checks.verify_shape_refusal` reads the command with a
quote-aware lexer - `shlex` drops whether a character was quoted, which is the
difference between searching for `$x` and searching for what the shell holds
in `x` - and admits `grep -q` clauses, `! grep -q` clauses, several joined by
`&&`, or `uv run pytest --cov=<dotted.module> --cov-fail-under=<N>` alone. A
`grep` may carry `-F`, `-E`, `-r`, `-i`, and with `-r` an `--include=` or
`--exclude=` ahead of the pattern; a path may glob. Anything else is refused,
with the first thing found named, unless `not-delegable:` says why none fits.

**`! grep` is admitted, on the direction it fails in.** Every way it goes wrong
- a typo, a line another branch reworded, a file another branch deleted - makes
it *pass*, and a passing open command is already an error the changed-path
replay reports on the branch that caused it. The positive shape's failures are
the quiet ones (`PL-RR1N`, `PL-CWD4`). It is also the one shape for the
commonest removal, a stale sentence, that does not dictate the fix's wording.

**Two anchors, where the brief named one.** `verify_allowlist_from =
2026-09-24` binds items captured from that date, as the dated rules before it
do. But a capture date cannot say when a command was written, and a cutover
read from it alone leaks the triage of every older item and the repair of every
legacy command as its item starts - most of what is written in the weeks after
it. So a command a branch writes or rewrites for an older item is held to the
list there: `check` reads it from git (`vcs.commands_written_here`), `set`
knows it as it writes. A command a branch leaves as the base had it stays
grandfathered.

**Measured 2026-09-23 over the 220 open commands:** 103 fit as they stand, 93
more once their legacy trailing health clause is stripped, and 24 are other
shapes - tool runs, pipes, `-k`, `test -f`, one `--include=` after its pattern,
which BSD `grep` would read as a file.

**Members.** `PL-0QRP` dropped against this: the counting clause is outside the
list. `PL-CWD4` and `PL-RR1N` re-pointed: the list narrows each and settles
neither, and each brief now says where its fix goes.
