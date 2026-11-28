---
id: PL-7YMX
title: mutmut 3.8.1 leaves an Enum class's __init__ unmutated, so app/display_units.py, left out of mutation runs because 3.8.0 wrapped DisplayUnit.__init__, may now be mutated
status: untriaged
added: 2026-11-28
filed-pr: 2346
---

**Problem.** mutmut 3.8.1 leaves an Enum class's __init__ unmutated, so app/display_units.py, left out of mutation runs because 3.8.0 wrapped DisplayUnit.__init__, may now be mutated
