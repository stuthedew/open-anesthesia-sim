---
id: PL-44R1
title: The headless worker host still resolves make to /usr/bin/make (GNU Make 3.81), so make check fails the two GNU make comparison tests in tests/unit/test_makefile_reference.py on every worker run after PL-TSH9 closed, and no worker there can report the gate green
status: untriaged
added: 2026-10-20
---

**Problem.** The headless worker host still resolves make to /usr/bin/make (GNU Make 3.81), so make check fails the two GNU make comparison tests in tests/unit/test_makefile_reference.py on every worker run after PL-TSH9 closed, and no worker there can report the gate green

Observed 2026-10-20 by the headless worker on `PL-70M6`. `make check` exited 2. pytest reported "2 failed, 10103 passed, 3 skipped". The two failures were `test_the_makefile_readers_read_generated_makefiles_as_make_does` and `test_the_makefile_readers_read_the_tracked_makefile_as_make_does`, and each said "AssertionError: /usr/bin/make is GNU Make 3.81; the comparison needs version 4 or newer". `PL-TSH9` made the test name the cause, and it asked `docs/maintainer.md` to say how to install current GNU make on the Mac. The bash half of `PL-TSH9` is fixed on this host, because the shell tests passed. The make half is not: `make` on the worker's `PATH` is still Apple's 3.81.
