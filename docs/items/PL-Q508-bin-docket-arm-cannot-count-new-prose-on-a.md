---
id: PL-Q508
title: bin/docket arm cannot count new prose on a branch that changes src/anesthesia_sim/app_metadata.py or layout/store.py in a cloud container, because docket.toml's prose_count_command runs bare python3 (3.13 here) and those files use Python 3.14's unparenthesized except syntax (PEP 758), so arm holds correct work
status: untriaged
added: 2026-10-19
---

**Problem.** bin/docket arm cannot count new prose on a branch that changes src/anesthesia_sim/app_metadata.py or layout/store.py in a cloud container, because docket.toml's prose_count_command runs bare python3 (3.13 here) and those files use Python 3.14's unparenthesized except syntax (PEP 758), so arm holds correct work

**Found 2026-10-19 on #1661.** `bin/docket arm` held the branch with
"`python3 tools/new_prose.py --count` exited 2: new_prose: not read:
src/anesthesia_sim/app_metadata.py: multiple exception types must be
parenthesized, line 92". Line 92 is `except OSError,
subprocess.SubprocessError:`, which `main` already carries. The same command
run with Python 3.14.7 (`uv python find 3.14`) first on `PATH` printed `21`.
`PL-JQJQ` records why a bare `python3` here is older than the simulator's
interpreter. Either the command in `docket.toml` names an interpreter that
can parse `src/`, or `new_prose.py` falls back to the tokenizer as `PL-TC2D`
did for `docket verify`.
