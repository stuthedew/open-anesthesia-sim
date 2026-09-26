---
id: PL-K9QL
title: The three Bash guards read a redirection written ahead of a command as the command's name, so 2>/dev/null make check | tail -5, 2>/dev/null python3 -m compileall -q src/ and 2>/dev/null git fetch --prune pass all three, though bash runs make, python3 and git
priority: P2
effort: S
status: done
classes: defect
touches: .claude/hooks/shell_split.py, .claude/hooks/gate-status-guard.sh, .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/no-prune-guard.sh, tests/unit/test_gate_status_guard.py, tests/unit/test_floor_interpreter_guard.py, tests/unit/test_no_prune_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-09-26
pr: 1109
payoff: a gate, a floor parse or a prune is refused however a redirection is placed around it - 2>/dev/null ahead of it, >x among a wrapper's words, 2>/dev/null among its own - so a red make check written that way no longer reaches a session as exit 0
verify: grep -q 'def test_a_redirection_is_not_a_word_of_the_command' tests/unit/test_gate_status_guard.py && grep -q 'def test_a_redirection_is_not_a_word_of_the_command' tests/unit/test_floor_interpreter_guard.py && grep -q 'def test_a_redirection_is_not_a_word_of_the_command' tests/unit/test_no_prune_guard.py
---

**Problem.** The three Bash guards read a redirection written ahead of a command as the command's name, so 2>/dev/null make check | tail -5, 2>/dev/null python3 -m compileall -q src/ and 2>/dev/null git fetch --prune pass all three, though bash runs make, python3 and git

**Found 2026-09-26 triaging `PL-TRMN`**, by piping each as a hook payload
into the three guards on `6d92df95`: all three pass. Bash 5.2.21 runs the
command after a leading redirection - `2>/dev/null echo ran` prints `ran` - and
POSIX.1-2017 XCU §2.9.1 reads a simple command as assignments and redirections
in any order, then the name. `shell_split.command_words` drops assignments but
not redirections, and the lexer returns `2>/dev/null` as the word `2`, the
operator `>` and the word `/dev/null`, so the guard reads `2` as the command.
Its docstring says it drops everything bash reads ahead of a command's name,
which is what `PL-0X0G` (done, #1093) made it do for reserved words.

**The same holds among a wrapper's words** (found 2026-09-26 closing
`PL-TRMN`). Bash lifts a redirection out of a simple command wherever it sits,
so `timeout 5 >x make check | tail`, `env 2>/dev/null git fetch --prune` and
`timeout 60 2>/dev/null python3 -m compileall -q src/` run `make`, `git` and
`python3`, and each passes all three guards, run as hook payloads on
`PL-TRMN`'s branch: `_run_by` in `.claude/hooks/shell_split.py` stops at the
`>` operator and reads no program. A fix in `command_words` alone leaves that
site, so both want one answer for which words a redirection takes.

**Reproduced 2026-09-26 on `de5f1c02`** (`PL-TRMN`'s merge), all six spellings
above as hook payloads: each passes all three guards, while the same command
without the redirection is refused by the guard it concerns. Against bash
5.2.21, a descriptor is a number or a `{name}` written against a `<` or `>`
operator: `timeout 5>x echo ran` fails with `invalid time interval 'echo'`,
where `timeout 5 >x echo ran` and `timeout '5'>x echo ran` run `echo`; and a
redirection among a program's own words is lifted too, `echo a 2>&1 b` printing
`a b`, so `bin/docket 2>/dev/null check | tail` loses the gate's status
unrefused as well.

**Why it matters.** Each guard refuses a spelling that has already cost this
project a round or a ref (`PL-2JRC`, `PL-JQJQ`, `PL-HKF4`), and each reads the
command through the one answer `shell_split.py` gives. Where that answer takes a
redirection for the command's name, the guard's pass reads as a verdict on a
command it never looked at, in all three guards at once.

**Done when.** `shell_split.py` reads a redirection - its descriptor where one
is written against it, its operator and the word it names - as no word of the
command, wherever bash lifts it from: ahead of the command's name, among a
wrapper's words, and among the program's own. The six spellings above are
refused, and so is `bin/docket 2>/dev/null check | tail`; a digit spaced from
its operator or quoted is still a word; `2>/dev/null set -o pipefail` keeps the
status a pipe after it would lose. A redirection's target is no argument, so the
floor guard stops refusing `python3 x.py > src/out.txt`, which parses nothing
there, and still refuses `python3 < src/a.py`, which parses the file it reads.
The three hook suites pin each.

**Generator check.** A re-entry of `PL-0X0G`: the same fact - which word bash
reads as a command's name, past what it reads ahead of it - at a sibling site
its fix should have covered, closed the same day. Not a head at the family
altitude either: this, `PL-0X0G`, `PL-TRMN`, `PL-9RSP` and `PL-QMN0` are gaps in
one reader that all three guards already consult (`PL-PVW2`), not one fact read
by several, and a redirection is the one part of POSIX's command prefix -
assignments and redirections, XCU §2.10.2 - that it did not read.
