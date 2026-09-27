---
id: PL-0MLZ
title: uv run pytest writes bytecode that survives a source restore, so a mutation test can silently keep running the mutated build
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: pyproject.toml, Makefile, tests/unit/test_tools_portability.py
added: 2026-09-13
verify: uv run python -c "import sys; raise SystemExit(0 if sys.dont_write_bytecode else 1)"
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

**Verified 2026-09-14.** `grep -rn PYTHONDONTWRITEBYTECODE` across `Makefile`,
`pyproject.toml`, `uv.toml`, `.env` and `.claude/` returns exactly one hit:
`Makefile:21`. So the guard is set by the *entry point* and not by the
interpreter, and every invocation that does not go through `make` writes
bytecode - which is `uv run pytest` directly, the form this store's own
`verify:` commands use, the form the `docket` skill recommends while iterating
(`pytest -q`), and the form a session reaches for by hand.

**Why it matters.** It makes a verification step lie, in the direction of a
false pass. The observed sequence in the brief above caught both mutations, so
it cost nothing; the failure that costs something is the mirror - restore a
file, watch the suite go green, and conclude that a test bites when what
actually ran was bytecode from a build where it did not. `CLAUDE.md`'s
safety-critical standard requires a regression test that would have caught each
safety bug, and this is a way to believe such a test exists when it does not.
That is also `CLAUDE.md`'s first compounding-friction test exactly - a check
passing while the guarantee it stands for is void - so it is worth doing ahead
of ordinary queue order rather than in it.

**Done when.** `PYTHONDONTWRITEBYTECODE` is set where the interpreter reads it
rather than where `make` does, so a bare `uv run pytest` inherits it -
`[tool.uv]`'s `env` or `env-file` in `pyproject.toml` is the cheapest candidate -
and a source restore is therefore never shadowed by a stale `.pyc`. The
`Makefile` export may stay or go, but no workflow depends on it being the only
carrier. The hypothesis in the brief above about PEP 552 hash-based invalidation
is either confirmed by reading the 16-byte `.pyc` header flag word or dropped
from the brief; the fix does not depend on which.

**Re-shaped at pickup, 2026-09-27.** Three measurements move the fix; the end
state does not move.

- **The hash hypothesis is dropped.** The cache the reproduction below left
  has flag word 0: a timestamp `.pyc`, not a PEP 552 hash one. In CPython
  3.14's `importlib._bootstrap_external`, `SourceLoader.get_code` takes `int()`
  of the source's mtime and `_validate_timestamp_pyc` accepts the cache when
  that and the size match what it recorded, so an equal-length edit compiled
  and reverted inside one whole second validates against the reverted file.
  Reproduced: of 12 cycles of mutating `gas_volume_l` from 2.5 to 2.6 in
  `src/anesthesia_sim/core/alveolar.py`, importing it with `uv run python`,
  copying the original back and importing again, 11 ran 2.6 while the file
  said 2.5. Pinning the restored file's mtime into the mutated one's second
  with `touch -d` reproduces it every time. `--import-mode=importlib` cannot
  change this: it decides how pytest imports test modules, and `src/` loads
  through the ordinary source loader under every mode.
- **The candidate carrier does not exist.** uv 0.12.19 warns that `env` and
  `env-file` under `[tool.uv]` are unknown fields and applies neither, and it
  reads a `.env` only under `--env-file` or `UV_ENV_FILE`. No file in the
  checkout can make a bare `uv run` export a variable.
- **`.claude/settings.json`'s `env` does not reach this project's threads.**
  That file sets `CLAUDE_CODE_SUBAGENT_MODEL`, which is unset in the shell of
  the thread that took this item: the project configures two repositories, so
  a thread starts in the directory above the checkout and never loads it.

**Carrier taken: the root `conftest.py`**, which pytest resolves however it is
started - the reason the git-configuration lines already live there. It sets
`sys.dont_write_bytecode` for the run and exports `PYTHONDONTWRITEBYTECODE` to
the interpreters the suite starts, so it covers every invocation this brief
names - a `verify:` command, a session iterating, a hand run, CI - and leaves
the app's own startup alone. It does not cover a bare `uv run python`. The one
carrier that reaches that is a dev-group package installing a `.pth` into the
virtualenv: a new package and lock entry, and a slower launch for every
`uv run anesthesia-sim`, for an invocation that is not how a test result is
read. It stops a write, not a read: a cache written from mutated source by
something other than a test run, and restored inside the same second, still
shadows the restored file. The `Makefile` export stays for the recipes that
are not pytest runs, and `PL-H9GV` owes it a test.

**Done when**, restated for this carrier: a pytest run writes no bytecode
however it was started, and a same-second restore runs the restored source.
`tests/unit/test_bytecode_guard.py` holds both, with CPython's own behaviour as
the control that shows the second test discriminates. The commissioned
`verify:` asked whether a bare `uv run python` writes bytecode, which this
carrier deliberately does not reach, so it gives way to the grep for the
regression test.
