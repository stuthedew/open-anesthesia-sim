---
id: PL-0QLX
title: tests/unit/test_docket_branch_guard.py and test_docket_digest_hook.py pin PATH to /usr/bin:/bin:/usr/local/bin, so on a Mac whose /usr/bin/python3 is Apple's 3.9 bin/docket fails on datetime.UTC, both hooks exit 0 silently, and eight tests fail locally while CI is green
priority: P3
effort: S
status: dropped
classes: test, infra
added: 2026-09-14
closed: 2026-09-14
reason: duplicate of PL-Y6W9 - the same eight hook tests red under macOS's system python3 (Apple's 3.9.6 below the 3.11 floor, bin/docket dying on datetime.UTC), captured eight minutes apart on two live branches; PL-Y6W9 is the one worked, in #584, and PL-8KPD recorded that this one would be dropped once both branches had landed (project owner, 2026-09-14)
---

**Problem.** tests/unit/test_docket_branch_guard.py and test_docket_digest_hook.py pin PATH to /usr/bin:/bin:/usr/local/bin, so on a Mac whose /usr/bin/python3 is Apple's 3.9 bin/docket fails on datetime.UTC, both hooks exit 0 silently, and eight tests fail locally while CI is green

**Dropped 2026-09-14 as a duplicate of `PL-Y6W9`** (project owner). Both
items describe one defect: `tests/unit/test_docket_branch_guard.py` and
`tests/unit/test_docket_digest_hook.py` run the hooks under
`PATH=/usr/bin:/bin:/usr/local/bin`, which on macOS resolves `python3` to
Apple's 3.9.6, below the floor `subprojects/docket/pyproject.toml` declares, so
`bin/docket` fails on `datetime.UTC`, both hooks exit 0 as their contract says,
and eight tests are red on the owner's machine while green in CI. `PL-Y6W9`
carries the fix - the fixture links the suite's own `sys.executable` into the
checkout's `bin/` as `python3` and leads `PATH` with it, pinned by an identity
test per file - worked in #584. Nothing here is lost by dropping it.
