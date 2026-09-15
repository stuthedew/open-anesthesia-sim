---
id: PL-LSTW
title: tools/ignore_check.py is named for .gitignore but evaluates type: ignore directives, so a session looking for the gitignore check finds it and a session looking for the mypy one does not
priority: P3
effort: S
status: ready
classes: infra
touches: tools/ignore_check.py, Makefile
added: 2026-09-15
verify: python3 tools/type_ignore_check.py --help >/dev/null && ! test -e tools/ignore_check.py
---

**Problem.** tools/ignore_check.py is named for .gitignore but evaluates type: ignore directives, so a session looking for the gitignore check finds it and a session looking for the mypy one does not

**Why it matters.** The name is the only index a session has. This repository
carries fifteen checks under `tools/`, and a session reaching for one reads the
filename rather than the module docstring - so `ignore_check.py` costs a wrong
open in both directions: a session looking for the `.gitignore` check finds it
and has to read 40 lines of docstring to learn it is about mypy, and a session
looking for the mypy-suppression check does not find it under any name it would
guess. Observed 2026-09-15 while working `PL-RFGY`: this session opened it
expecting a `.gitignore` check, which is exactly the wrong open the name
invites.

The cost is small per instance and permanent, and it grows rather than decays -
`PL-MXSL` puts a genuine ignore-related check into `doc_check.py`, so the
repository now has ignore-rule logic in a file *not* called `ignore_check.py`
and mypy logic in one that is.

**Done when.** No file under `tools/` is named for a thing it does not check.
The proposed rename is `tools/type_ignore_check.py`, which says what it
evaluates in the same shape as its neighbours (`import_boundary_check.py`,
`core_vocabulary_check.py`); the name is a proposal rather than a finding, and
any name that does not read as `.gitignore` satisfies the item. `Makefile`'s
invocation moves with it, and `git mv` keeps the history.
