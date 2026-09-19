---
id: PL-09G9
title: Nothing refuses a new verify: command that re-runs a test file make check already collects, so PL-6TP8's contract is enforced by prose alone and 82 of 180 open commands carry the clause
priority: P2
effort: M
status: done
classes: defect
feature: verify-replay-cost
milestone: v0.4.29
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/config.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_config.py, docket.toml, subprojects/docket/README.md
added: 2026-09-19
closed: 2026-09-19
pr: 711
verify: grep -q 'def test_a_new_command_re_running_a_collected_test_file_is_refused' subprojects/docket/tests/test_checks.py
---

**Problem.** Nothing refuses a new verify: command that re-runs a test file make check already collects, so PL-6TP8's contract is enforced by prose alone and 82 of 180 open commands carry the clause

**Where it comes from.** `PL-6TP8` (project owner, 2026-09-19, ratified)
decided the `verify:` field records the discriminator only: the health check is
the consumers' to run, because `docket verify` runs `config.check_command` as
its own line, `docs/worker.md` runs `make check` after the command, and CI runs
the suite ahead of the replay. It also chose **repair-as-started** over a
one-pass strip of the 162 commands then carrying a prerequisite clause, so the
bill falls as the queue turns over.

Repair-as-started drains a *closed* set. Nothing closes it. Measured against
the open store on 2026-09-19:

| | |
| --- | --- |
| open items carrying a `verify:` | 180 |
| ...whose command runs pytest ahead of a separate discriminating clause | **82** |
| ...of those, whose pytest target `make check`'s own `testpaths` do not collect | **0** |
| written on 2026-09-14 alone | 23 of that day's 33 |
| written on 2026-09-13 | 18 of 30 |

The shape was being recorded about twenty times a day up to the week the
contract was decided, and what now prescribes the replacement is one table in
`.claude/skills/docket/SKILL.md`. `subprojects/docket/src/docket/checks.py`
holds nothing that reads the command's shape: `_check_selects_nothing` reads
pytest's exit code 5, and `_verify_required` reads only whether the field is
*present*. So the ratified contract is enforced by a session remembering to
read a skill table, against a store that records eighty-two counter-examples.

**Why it matters.** `PL-FZ58` measured what the clause costs while it stands:
three test files carry 59% of the replay's serial cost, each re-run once per
item whose command names it. That drains — the queue closed 672 items in the
last fourteen dated days, 48/day against 324 open — but only if inflow is zero,
and inflow is the half nothing measures or refuses.

This is `CLAUDE.md`'s "find the decidable part and put it in code". The
decidable part is exact and does not touch the judgment half: a clause that
runs pytest over a path `make check` already collects, standing beside a
*separate* discriminating clause, is provably redundant whatever the item's
work is — because the separate clause is what proves pytest is not the
discriminator. What stays judgment is everything the author must decide: which
test to pin, whether it discriminates on this item's own work, whether it reads
the tree `touches` declares.

**What this deliberately does not refuse.** The other 73 multi-clause commands,
whose first clause is `python3 tools/doc_check.py check` (58), `bin/docket
check` (7) or similar. `PL-6TP8`'s contract condemns those too, but which clause
is the prerequisite there is not decidable: an item whose work is *making
`doc_check` pass* has `doc_check.py check` as its discriminator, and two of the
73 (`test -f .claude/rules/run-is-its-definition.md && grep …`, `grep -q 'pip
install -U' docs/worker.md && …`) are two discriminators rather than a
prerequisite and a discriminator at all. Refusing those would be scripting the
judgment, which `CLAUDE.md` holds is worse than no tool. They stay prose.

**What would falsify the rule.** A pytest target `make check`'s suite does not
collect — `[tool.pytest.ini_options] testpaths` is `["tests",
"subprojects/docket/tests"]`, and the count above is 0 today — or `make check`
ceasing to run the whole suite. Both are nameable changes rather than silent
drift, and the check reads `testpaths` rather than carrying its own copy.

**Done when** `docket check` errors on a command of that shape written on or
after the cutover, the 82 already recorded are untouched and left to
repair-as-started, and the rule and its grandfathering are documented where
`verify_required_from` documents its own.
