---
id: PL-QMN0
title: gate-status-guard.sh unwraps uv run only where the program follows it directly, so a gate after uv run's own options - uv run --with pytest-xdist pytest -n 4 2>&1 | tail - is read as a command named --with and loses its status unrefused
status: untriaged
added: 2026-09-26
---

**Problem.** gate-status-guard.sh unwraps uv run only where the program follows it directly, so a gate after uv run's own options - uv run --with pytest-xdist pytest -n 4 2>&1 | tail - is read as a command named --with and loses its status unrefused

**Found 2026-09-26 triaging `PL-TRMN`**: on `6d92df95` the hook passes
`uv run --with pytest-xdist pytest -n 4 2>&1 | tail` and refuses the same
command without `--with pytest-xdist`. `strip_prefixes` drops `uv run` and then
reads the next word as the program. Neither the `Makefile` nor the workflows
spell `uv run` with options, so it is unobserved here; reaching it means
reading uv's own option grammar, which `PL-TRMN` does for the wrappers it
names and deliberately not for `uv run`.
