---
id: PL-SMM1
title: floor-interpreter-guard.sh refuses python3 -m json.tool on a data file under src/, reading every argument after -m as a tree to parse, and its header omits the heredoc and substitution gaps its own table records
priority: P2
effort: S
status: done
classes: defect
feature: guard-review-2026-11
milestone: v0.6.15
touches: .claude/hooks/floor-interpreter-guard.sh, tests/unit/test_floor_interpreter_guard.py
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-03
pr: 1989
payoff: a session can pretty-print an agent's data file without being refused, and the guard's header states every gap it has
verify: grep -q 'def test_json_tool_on_a_data_file_is_admitted' tests/unit/test_floor_interpreter_guard.py
reenters: PL-61FT
---

**Problem.** floor-interpreter-guard.sh refuses python3 -m json.tool on a data file under src/, reading every argument after -m as a tree to parse, and its header omits the heredoc and substitution gaps its own table records

**Reproduced 2026-11-03.** `floor-interpreter-guard.sh` refused `python3 -m
json.tool src/anesthesia_sim/data/agents/sevoflurane.json`. It reads every word
after `-m <module>` as a tree the interpreter parses, but inside a `-c` string
it already reads only a path naming a directory or Python source.

**Why it matters.** Pretty-printing a data file parses no 3.14 source, so the
refusal is false, and a session reading the agent data meets it. The header's
list of what is outside the promise also omits the heredoc and substitution
gaps that its own `KNOWN_GAPS` table records, so the header overstates the
promise.

**Done when.** A word after `-m <module>` is read as parsed only where it names
a directory or Python source, as a `-c` string's words are, so the
`json.tool` call is admitted and `-m pytest tests/` still refused, and the
header lists every gap the table records.

**Generator check.** A re-entry of `PL-61FT` (what a shell command does when
run). Fixed at its own rank.
