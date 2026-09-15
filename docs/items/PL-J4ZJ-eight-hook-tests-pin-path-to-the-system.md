---
id: PL-J4ZJ
title: Eight hook tests pin PATH to the system directories, so on a Mac whose /usr/bin/python3 is 3.9.6 they fail before the hook can answer and make check is red locally
priority: P3
effort: S
status: dropped
classes: test, infra
added: 2026-09-14
closed: 2026-09-15
reason: duplicate of PL-Y6W9, which shipped the fix in #584 - the same eight hook tests, the same two files, the same mechanism (bin/docket under macOS's 3.9.6 dying on datetime.UTC while both hooks swallow it). Confirmed 2026-09-15: both files now symlink bin/python3 to sys.executable and lead PATH with the checkout's bin/, and the thirteen tests pass. This is the third capture of one defect; PL-0QLX was the second and was dropped the same way
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

**Triaged 2026-09-15 into the top band**, above the other Mac-interpreter items,
on `CLAUDE.md`'s compounding-friction test rather than on size. This is the
"being routed around" case stated outright: `make check` is what every close-out
runs before every commit, it is red on the owner's own machine on every branch
for a reason no branch caused, and a suite that is red for an environmental
reason teaches a session to read past red - which spends the signal for every
genuine failure after it. `PL-LKGW` is the adjacent interpreter-floor item and
is the nicer error message rather than the red suite, so it sits below this one.

Both files pin `PATH` the same way - `tests/unit/test_docket_digest_hook.py:119`
and `tests/unit/test_docket_branch_guard.py:72` lead with the checkout's `bin/`
and then `/usr/bin:/bin:/usr/local/bin`, and `:154` pins the bare form - so the
fix belongs in both and the `touches` above names both.

**Dropped 2026-09-15 at triage, as a duplicate of `PL-Y6W9`.** Verified rather
than assumed: `tests/unit/test_docket_digest_hook.py:86` and
`tests/unit/test_docket_branch_guard.py:64` both now do
`(root / "bin" / "python3").symlink_to(sys.executable)` with `PATH` leading on
the checkout's `bin/`, which is exactly the first of the two fixes `PL-Y6W9`'s
brief proposed, and `uv run pytest` over both files passes thirteen tests here.
The digest hook's docstring at `:77` states the reasoning and cites `PL-Y6W9`.

**This is the third capture of one defect**, which is the part worth recording.
`PL-0QLX` was the second and was dropped for the same reason on 2026-09-14
(#586); this one was captured the same day from the same `make check` run on the
owner's Mac. All three describe the eight tests red under Apple's 3.9.6. Nothing
here is lost by the drop: `PL-LKGW` carries the separate, still-open half - that
`bin/docket` meets a below-floor interpreter with a traceback about `render.py`
rather than a sentence naming the floor - and it is the item to work.
