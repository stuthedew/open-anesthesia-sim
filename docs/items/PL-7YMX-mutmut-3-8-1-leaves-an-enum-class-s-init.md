---
id: PL-7YMX
title: mutmut 3.8.1 leaves an Enum class's __init__ unmutated, so app/display_units.py, left out of mutation runs because 3.8.0 wrapped DisplayUnit.__init__, may now be mutated
priority: P3
effort: S
status: ready
classes: infra
feature: tests-detect-wrong-values
touches: pyproject.toml, docs/mutation-testing.md
added: 2026-11-28
filed-pr: 2346
payoff: the display-unit table is mutation-tested like every other module that imports no Qt, so a function added to it later is checked by the tests' mutation run
---

**Problem.** mutmut 3.8.1 leaves an Enum class's __init__ unmutated, so app/display_units.py, left out of mutation runs because 3.8.0 wrapped DisplayUnit.__init__, may now be mutated

**Why it matters.** `app/display_units.py` holds the table of display units that the interface prints beside values, so a fault in it puts a wrong unit beside a correct number. It is left out of every mutation run (`do_not_mutate` and `[tool.diff_mutation.left_out]` in `pyproject.toml`) because mutmut 3.8.0 broke every import of it. That reason no longer holds under mutmut 3.8.1, which `pyproject.toml` now pins (`PL-LR03`). So a function added to the module later would go unmutated for a reason that is out of date, and `docs/mutation-testing.md` still says that mutmut cannot wrap an `Enum` that defines `__init__`.

**Reproduced 2026-11-28.** The installed mutmut 3.8.1 (`uv run --locked --group mutation`) defines `NEVER_MUTATE_ENUM_FUNCTION_NAMES = {"__init__", "_generate_next_value_"}` in `mutation/file_mutation.py`, and leaves those functions unmutated in any class whose base is `Enum`, `IntEnum`, `StrEnum`, `Flag` or `IntFlag`. `DisplayUnit.__init__` is the module's only function, so the module would now have no mutants, and nothing would wrap the code that `Enum` calls while it builds the class.

**Done when.** `app/display_units.py` is out of `do_not_mutate` and `[tool.diff_mutation.left_out]`. A mutation run that includes it starts and finishes, and its result is written in this brief. `docs/mutation-testing.md` no longer says that mutmut cannot wrap an `Enum` that defines `__init__`.

**Generator check.** A one-off: a workaround for one release of a tool, which the tool's next release made unneeded. No head's `misread:` names how a pinned tool's own behaviour changes between releases.
