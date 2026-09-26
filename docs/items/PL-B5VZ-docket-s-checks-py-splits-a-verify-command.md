---
id: PL-B5VZ
title: docket's checks.py splits a verify: command three ways beside its own quote-aware _shell_words - str.split('&&'), which cuts inside a quoted argument, shlex.split, which keeps 't/a.py|tail' one word, and shlex's punctuation runs - so _redundant_pytest_clause and _k_selector_clause read one clause two ways
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/checks.py
added: 2026-09-26
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

**Generator check.** The same question `PL-PVW2` names - how a shell command
splits - answered again inside docket, which cannot import the hooks'
`.claude/hooks/shell_split.py`. Whether it is that head's member, or one docket
reader for `verify:` commands is its own smaller fix, is triage's call.
