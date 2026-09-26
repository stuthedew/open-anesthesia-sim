---
id: PL-CWBJ
title: tools/doc_check.py's check_workflow_paths splits a CI step's run: script with its own quote-blind COMMAND_SPLIT_RE, beside docket's lexer and the hooks' shell_split.py, so a quoted path holding a space reads as another path - python3 "tools/my file.py" reads as tools/my
status: untriaged
feature: one-answer
added: 2026-09-26
---

**Problem.** tools/doc_check.py's check_workflow_paths splits a CI step's run: script with its own quote-blind COMMAND_SPLIT_RE, beside docket's lexer and the hooks' shell_split.py, so a quoted path holding a space reads as another path - python3 "tools/my file.py" reads as tools/my

**Found 2026-09-26 triaging `PL-P7J7`**, by sweeping `tools/`, `.claude/` and
docket for other spellings of how a shell command splits. On `70818cfc`,
`doc_check._command_paths('python3 "tools/my file.py"')` yields `tools/my`, and
`check_workflow_paths` would report it as a path the step runs that does not
exist. `COMMAND_SPLIT_RE` (`[\s;|&()<>]+`) cuts inside quotes, and each token
has its quotes stripped at its ends only.

**Generator check.** `PL-PVW2`'s fact - how a shell command splits - spelled a
fourth way, in `tools/`, which that head's done-when has importing
`subprojects/docket/src`. Whether it is that head's member, and whether a
workflow's multi-line `run:` script can take docket's one-line reader at all,
is triage's call.
