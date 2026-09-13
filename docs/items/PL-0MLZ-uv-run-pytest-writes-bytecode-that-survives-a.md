---
id: PL-0MLZ
title: uv run pytest writes bytecode that survives a source restore, so a mutation test can silently keep running the mutated build
status: untriaged
added: 2026-09-13
---

**Problem.** uv run pytest writes bytecode that survives a source restore, so a mutation test can silently keep running the mutated build

**Observed 2026-09-13, while mutation-testing `PL-DJYF`'s new pins.** The
sequence was: back up `src/anesthesia_sim/core/alveolar.py`, change
`gas_volume_l: float = 2.5` to `2.6`, run `uv run pytest
tests/unit/test_alveolar.py` (2 failed - correct), `cp` the backup back, run
again. The restored source read `2.5` and
`uv run python -c "...AlveolarCompartment().gas_volume_l"` printed `2.6`,
importing from `/home/user/open-anesthesia-sim/src/anesthesia_sim/core/alveolar.py`
- the file that says `2.5`. `src/anesthesia_sim/core/__pycache__/alveolar.cpython-314.pyc`
was the copy actually running. Deleting every `__pycache__` outside `.venv/`
fixed it; `uv run --reinstall-package anesthesia-sim` did not.

**Why the usual invalidation did not fire.** A restored file gets a *newer*
mtime than the `.pyc`, which should force a recompile, so the observed
behaviour points at hash-based invalidation (PEP 552) in the unchecked mode,
where the interpreter trusts the cached file without comparing anything. That
is a hypothesis from the symptom rather than something checked - reading the
16-byte `.pyc` header flag word would settle it and was not done.

**Why it matters more than an ordinary cache annoyance.** It makes a
*verification step* lie, in the direction of a false pass. Both mutations here
were caught, so the finding cost nothing; the failure mode that costs
something is the mirror - restore a file, watch a suite go green, and conclude
a test bites when what actually ran was bytecode from a build where it did
not. `CLAUDE.md`'s safety-critical standard requires a regression test that
would have caught the bug, and this is a way to believe one exists when it
does not.

**Where the existing guard stops short.** `PYTHONDONTWRITEBYTECODE` is
exported at `Makefile:21`, so `make check` and `make test` are covered.
`uv run pytest` invoked directly - which is what `verify:` commands in this
store do, what the `docket` skill's iteration advice recommends
(`pytest -q` while iterating), and what a session reaches for by hand - is
not. So the protection exists and is bypassed by the most common invocation.
`PL-H9GV` is adjacent but is about that variable having shipped untested, not
about its coverage being narrower than the workflows that need it.

**Candidate dispositions, cheapest first.** Set the variable somewhere
`uv run` reads it rather than somewhere `make` does - `[tool.uv] env` or
`env_file` in `pyproject.toml`, or `PYTHONDONTWRITEBYTECODE` in
`.env`/`uv.toml` - so the guarantee follows the interpreter instead of the
entry point. `-p no:cacheprovider` does not help; this is interpreter bytecode,
not pytest's cache. Worth checking whether `pytest`'s own
`--import-mode=importlib` changes the picture before choosing.
