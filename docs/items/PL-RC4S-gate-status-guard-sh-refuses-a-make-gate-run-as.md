---
id: PL-RC4S
title: gate-status-guard.sh refuses a make gate run as a dry run - make --just-print check piped to tail - though --just-print runs no recipe and so has no gate status to lose; a session met it in PL-R417's link 23 sweep
status: untriaged
added: 2026-10-10
---

**Problem.** gate-status-guard.sh refuses a make gate run as a dry run - make --just-print check piped to tail - though --just-print runs no recipe and so has no gate status to lose; a session met it in PL-R417's link 23 sweep

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23): an auditor's
command of the form below was refused live.

```text
make -f Makefile.copy --just-print check 2>&1 | tail
```

`--just-print` (`-n`) prints the recipes without running them, so the
pipeline loses no status a gate produced. Nothing in `docs/items/` or the
guard's `KNOWN_GAPS` covers `-n` or `--just-print`; the guard's test file says
a row becomes an item once a session is seen writing it, and this one was.

**Generator check.** Not a member of `PL-R417`: one line, read whole.

**Done when.** A `make` run with `-n`, `--just-print`, `--dry-run` or `--recon`
is not refused as a gate whose status is lost, with a case in
`tests/unit/test_gate_status_guard.py`.
