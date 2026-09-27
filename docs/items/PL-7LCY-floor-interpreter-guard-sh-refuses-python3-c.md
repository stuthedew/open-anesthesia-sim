---
id: PL-7LCY
title: floor-interpreter-guard.sh refuses python3 -c reading a JSON parameter file under src/anesthesia_sim/data/, because it matches the tree name in the command text rather than whether 3.14 source is parsed, so correct read-only work is refused (a false refusal, the opposite direction to PL-61FT's spelling gaps)
priority: P3
effort: S
status: ready
classes: defect
feature: bash-guard-bound
touches: .claude/hooks/floor-interpreter-guard.sh, tests/unit/test_floor_interpreter_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
payoff: a session reading a JSON parameter file under the data tree with a -c string is let through, since that parses no 3.14 source, while a -c string that compiles or runs a tree's Python is still refused
verify: grep -q 'def test_a_c_string_reading_a_data_file_under_a_tree_is_left_alone' tests/unit/test_floor_interpreter_guard.py
---

**Problem.** floor-interpreter-guard.sh refuses python3 -c reading a JSON parameter file under src/anesthesia_sim/data/, because it matches the tree name in the command text rather than whether 3.14 source is parsed, so correct read-only work is refused (a false refusal, the opposite direction to PL-61FT's spelling gaps)

**Met 2026-09-26 in ordinary work on `PL-WMCJ`:** `python3 -c "import json; d=json.load(open('src/anesthesia_sim/data/agents/sevoflurane.json')) ..."` was refused with the PEP 758 message, though it parses no Python source; the same read spelled as a heredoc passed moments earlier. Routed around with `grep`, so it blocked nothing. Evidence for `PL-61FT`'s open design decision, which records that none of its twelve members was met in ordinary work.

**Met again 2026-09-27**, by the triage pass that classed it: `python3 -c
"import json;
d=json.load(open('src/anesthesia_sim/data/patients/reference_adult.json'))
..."` was refused with the same message, and the same read went through as a
heredoc. Reproduced the same day by piping this item's own command to the hook:
`permissionDecision: deny`, with the PEP 758 text.

**Why it matters.** The refusal tells a session something false about its own
command - that it parses 3.14 source - and teaches it that the guard is a thing
to route around, which is the habit its true refusals rely on a session not
having. Both meetings were ordinary read-only work on the parameter files under
`src/anesthesia_sim/data/`, which every science item reads.

**Done when.** `floor-interpreter-guard.sh` lets through a `-c` string whose
tree paths each name a file that is not Python source - this item's
`json.load(open('src/anesthesia_sim/data/agents/sevoflurane.json'))` among them
- and still refuses one naming a tree directory or a `.py` file under it; a
test pins both, and the header's promise says which paths inside a `-c` string
it reads as a parse.

**Generator check.** An instance of `PL-61FT`'s fact - what a shell command
does when run, here whether a `-c` string parses 3.14 source - which that
head's brief already records as met the day its bound was set, to be worked at
its own rank. Its reopening number counts known-gap rows met, and this is a
false refusal inside the promise rather than a row, so it is a one-off.
