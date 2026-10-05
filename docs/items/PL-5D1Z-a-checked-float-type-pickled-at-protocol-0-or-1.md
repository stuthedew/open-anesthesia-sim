---
id: PL-5D1Z
title: A checked float type pickled at protocol 0 or 1 is rebuilt through float.__new__, skipping its check, so holding one is not proof for an unpickled value
status: untriaged
feature: parse-dont-validate
added: 2026-10-05
---

**Problem.** `pickle` at protocol 0 or 1 reduces a `float` subclass through
`copyreg._reduce_ex`, and loading rebuilds it with `copyreg._reconstructor`,
which calls `float.__new__(cls, value)`: the class's own `__new__`, which runs
the range check, never runs. So a hand-made protocol-0 or protocol-1 pickle of
`Fraction(1.5)` loads as a `Fraction` holding 1.5, passes `require_fraction`,
and is stored. Protocol 2 and later, `copy.copy` and `copy.deepcopy` rebuild
through `copyreg.__newobj__`, which calls `cls.__new__`, so they are checked.
Every checked type shares the hole - `SimulationStep`, `FreshGasFlow` and its
siblings in `core/supported_ranges.py`, `Fraction` and `Percent` - as
`PL-4R3W`'s close-out review measured on 2026-10-05.

**Why it is not live.** Nothing in `src/` pickles, and loading an untrusted
pickle already runs arbitrary code, so the hole matters only once a run is
saved by pickle and a saved file is edited by hand.

**What a fix probably wants.** A `__reduce__` on each type returning
`(type(self), (float(self),))`, or the integer form for a count, rebuilds
through the class at every protocol (checked on a scratch `Fraction` subclass
for protocols 0 to 5), and one parametrized test over every checked type and
protocol pins it. One fix for the pattern rather than for one type, since the
types are meant to be one pattern (`.claude/rules/core-domain.md`).
