---
id: PL-J4ZJ
title: Eight hook tests pin PATH to the system directories, so on a Mac whose /usr/bin/python3 is 3.9.6 they fail before the hook can answer and make check is red locally
status: untriaged
added: 2026-09-14
---

**Problem.** Eight hook tests pin PATH to the system directories, so on a Mac whose /usr/bin/python3 is 3.9.6 they fail before the hook can answer and make check is red locally

**Found 2026-09-14 while closing `PL-FWJF`**, on the project owner's own
machine (macOS on Apple Silicon). `make check` reported eight failures - five
in `tests/unit/test_docket_digest_hook.py`, three in
`tests/unit/test_docket_branch_guard.py` - on a diff that touched neither file
nor either hook.

**Mechanism, measured.** `_run_hook` runs the hook with `PATH` pinned to
`/usr/bin:/bin:/usr/local/bin`. On this machine `/usr/bin/python3` is 3.9.6
and `/usr/local/bin/python3` is absent, because Homebrew installs to
`/opt/homebrew/bin` on Apple Silicon. `bin/docket` execs `python3 -m docket`,
and `docket.config` imports `tomllib`, which 3.9 does not have - run by hand
under that PATH: `ModuleNotFoundError: No module named 'tomllib'`, `3.9.6`.
`.claude/hooks/docket-digest.sh` is written to fail silently (`command -v
python3 || exit 0`, `2>/dev/null || true`), so the test receives an empty
string and asserts on a line that was never printed. CI runs on Linux with a
modern interpreter and is unaffected, so `main` is green while the owner's
local `make check` is red on every branch.

**Why it matters.** `make check` is what a close-out runs before every commit,
and a suite that is red for an environmental reason on the owner's machine
trains a session to read past red - `CLAUDE.md`'s "a check earns its place
every run". It also fails the apparatus floor: the eight tests report a hook
defect that is not there.

**Candidate fix.** Put the directory of `sys.executable` at the head of the
pinned `PATH` in `_run_hook`, so the hook runs the interpreter the tests run
under while the rest of the environment stays bare; or have `bin/docket`
refuse loudly on an interpreter below the floor `docs/ARCHITECTURE.md` states,
so the assertion is on that message rather than on silence. Either way the
same assertion should hold on macOS and in CI.

**Done when** `uv run pytest tests/unit/test_docket_digest_hook.py
tests/unit/test_docket_branch_guard.py` passes on a Mac whose
`/usr/bin/python3` is 3.9.6 with no `/usr/local/bin/python3`, and CI still
passes.
