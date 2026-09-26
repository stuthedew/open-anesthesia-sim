---
id: PL-B5VZ
title: docket's checks.py splits a verify: command three ways beside its own quote-aware _shell_words - str.split('&&'), which cuts inside a quoted argument, shlex.split, which keeps 't/a.py|tail' one word, and shlex's punctuation runs - so _redundant_pytest_clause and _k_selector_clause read one clause two ways
priority: P2
effort: S
status: done
classes: defect
feature: one-answer
milestone: v0.5.12
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py, docs/items/PL-PVW2-predicates-the-apparatus-asks-repeatedly-which.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; a member of PL-PVW2, docket's reading of a verify: command
added: 2026-09-26
closed: 2026-09-26
pr: 1095
payoff: every rule that reads a verify: command reads it through the one quote-aware reading the admitted shapes take, so no rule's answer turns on how a pipe is spaced or loses a clause behind a quoted &&
verify: grep -q 'def test_a_verify_clause_is_read_one_way' subprojects/docket/tests/test_checks.py
recurrences: 2026-09-26 PL-P7J7 withdrawn 2026-09-26 PL-P7J7
---

**Problem.** docket's checks.py splits a verify: command three ways beside its own quote-aware _shell_words - str.split('&&'), which cuts inside a quoted argument, shlex.split, which keeps 't/a.py|tail' one word, and shlex's punctuation runs - so _redundant_pytest_clause and _k_selector_clause read one clause two ways

**Found 2026-09-26 while building `PL-PVW2`'s shell splitter for the Bash
guard hooks**, by sweeping the tree for other copies of the split. Each reader,
on the standard library at the 3.11 floor:

    shlex.split('uv run pytest -q t/a.py|tail')
        ['uv', 'run', 'pytest', '-q', 't/a.py|tail']
    shlex.shlex(..., posix=True, punctuation_chars=True), whitespace_split
        ['uv', 'run', 'pytest', '-q', 't/a.py', '|', 'tail']
    "grep -q 'a && b' f && uv run pytest -q".split('&&')
        ["grep -q 'a ", " b' f ", ' uv run pytest -q']

`_redundant_pytest_clause` reads its clauses through `_pytest_targets`
(`shlex.split`) and `_k_selector_clause` through `_shell_tokens` (punctuation
runs), both after the raw `&&` split, while `_shell_words` already knows what
is quoted. No verify: command in the store is known to take a shape where the
readers disagree; this is the mechanism, not an observed wrong answer.

[superseded 2026-09-26: triaged below as `PL-PVW2`'s member] **Generator check.** The same question `PL-PVW2` names - how a shell command
splits - answered again inside docket, which cannot import the hooks'
`.claude/hooks/shell_split.py`. Whether it is that head's member, or one docket
reader for `verify:` commands is its own smaller fix, is triage's call.

**Reproduced 2026-09-26 against `c2be4070`**, each rule called on a
constructed command with this project's collected trees:

    uv run pytest -q tests/unit/test_a.py|tail && grep -q 'x' a.py
        _redundant_pytest_clause reports the pytest clause; with ` | ` spaced, nothing
    uv run pytest tests/unit/test_a.py --junitxml='a&&b.xml' && grep -q 'x' a.py
        _redundant_pytest_clause: nothing - the raw split cuts the quote, shlex refuses both halves
    uv run pytest tests/unit -k foo --junitxml='a&&b.xml' && grep -q 'x' a.py
        _k_selector_clause: nothing, for the same reason
    grep -q 'x' a.py && uv run pytest tests/unit/test_a.py # why
        _redundant_pytest_clause: nothing - shlex.split reads `#` and `why` as paths to run,
        where _k_selector_clause's lexer strips a comment as the shell does

So a quoted `&&` hides a run from both rules, one rule's answer turns on how a
pipe is spaced, and the two disagree about a comment. The admitted shapes refuse
every one of those commands wherever they bind, so what the misreadings reach is
the grandfathered commands, and a project that dates these two rules without the
list.

**Generator check, answered.** A member of `PL-PVW2`: its fact - how a shell
command splits - answered by docket's second and third readers of a `verify:`
command. Docket keeps an answer of its own rather than importing the hooks'
splitter, as that head's design has it, and for two reasons checked here:
`bin/docket` puts `subprojects/docket/src` alone on the path, so a standalone
tool would reach into one repository's harness directory; and
`shell_split.words` returns words with their quotes removed, where the admitted
shapes need to know what was quoted (`grep -q '$x' f` against `grep -q $x f`).
So the one reading inside docket is `_shell_words`.

**On the Fix generators project's list** (project owner, 2026-09-26, ratified,
over leaving it off the list).

**Why it matters.** Two refusing rules read one clause two ways, beside a third
reader that knows what is quoted: the same command is refused or passed on how
it is spaced, and a quoted `&&` hides a run from both. Each rule copied the
reading it met first, which is `PL-PVW2`'s mechanism, and the next rule over a
`verify:` would copy one of the three.

**Done when.** `_redundant_pytest_clause` and `_k_selector_clause` read their
clauses from `_shell_words`, the reading `verify_shape_refusal` takes, which
reads every operator rather than stopping at the first; `checks.py` keeps no
`shlex` and no `split("&&")` of a command; and
`test_a_verify_clause_is_read_one_way` in `subprojects/docket/tests/test_checks.py`
holds the inputs above.
