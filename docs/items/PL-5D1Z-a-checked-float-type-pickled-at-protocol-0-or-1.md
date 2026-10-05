---
id: PL-5D1Z
title: A checked float type pickled at protocol 0 or 1 is rebuilt through float.__new__, skipping its check, so holding one is not proof for an unpickled value
priority: P2
effort: S
status: ready
classes: defect
feature: parse-dont-validate
touches: src/anesthesia_sim/core/checked_number.py, src/anesthesia_sim/core/concentration.py, src/anesthesia_sim/core/supported_ranges.py, src/anesthesia_sim/core/simulation_step.py, tests/unit/test_checked_number.py, tests/unit/test_concentration.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-05 triage pass
added: 2026-10-05
payoff: a checked value read back from a pickle at any protocol has passed its check, so holding the type stays proof of a supported value even for a saved file edited by hand
verify: grep -q 'def test_every_checked_type_unpickled_at_any_protocol_is_rebuilt_through_its_check' tests/unit/test_checked_number.py
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

**Reproduced 2026-10-05, at triage, for the `int` type too.** On Python
3.14.7, against `main` at `b67dace8`,

```bash
uv run python -c "import pickle, struct; from anesthesia_sim.core.concentration import Fraction; from anesthesia_sim.core.simulation_step import SimulationStep; from anesthesia_sim.core.supported_ranges import FreshGasFlow, StepCount; print([type(v).__name__ + ' ' + repr(v) for v in (pickle.loads(pickle.dumps(Fraction(0.5), protocol=0).replace(b'0.5', b'1.5')), pickle.loads(pickle.dumps(Fraction(0.5), protocol=1).replace(struct.pack('>d', 0.5), struct.pack('>d', 1.5))), pickle.loads(pickle.dumps(SimulationStep(0.05), protocol=0).replace(b'0.05', b'5.0')), pickle.loads(pickle.dumps(FreshGasFlow(5.0), protocol=1).replace(struct.pack('>d', 5.0), struct.pack('>d', 1000.0))), pickle.loads(pickle.dumps(StepCount(5), protocol=0).replace(b'I5', b'I-5')))]); pickle.loads(pickle.dumps(Fraction(0.5), protocol=2).replace(struct.pack('>d', 0.5), struct.pack('>d', 1.5)))"
```

printed `['Fraction 1.5', 'Fraction 1.5', 'SimulationStep 5.0', 'FreshGasFlow
1000.0', 'StepCount -5']` and then raised `SimulationConfigurationError:
fraction of 1.5 is outside 0 to 1` for the protocol-2 load. So `StepCount`, an
`int` subclass, has the hole as well, rebuilt through `int.__new__` at
protocol 0.

**Why it matters, and why `defect` at `P2` rather than `safety`.** Holding a
checked type is the proof its check ran, and a hand-edited file at protocol 0
or 1 hands back a fresh gas flow of 1000 L/min or a negative step count under
the type that says otherwise - which no `require_*` downstream will question.
It is not classed `safety` because no slip produces it: nothing in `src/`
writes or reads a pickle, every protocol from 2 up is checked and the default
is pinned by `test_a_pickle_edited_past_the_range_is_refused_when_it_is_loaded`,
and reaching it takes choosing a protocol nobody here uses and then editing the
bytes, which is deliberate rather than mistaken; a caller loading a pickle it
did not write can already run any code. It matters once a run is saved by
pickle, and is cheapest closed now, while the types are one pattern and a
single parametrized test can cover them all.

**Done when.** Every checked type - the three flows, `CaseInstant`,
`StepCount`, `SimulationStep`, `Fraction` and `Percent` - rebuilds through its
own constructor at every pickle protocol from 0 to `pickle.HIGHEST_PROTOCOL`,
so a value edited past its range is refused on load with the constructor's
own exception. A `__reduce__` per type or one shared in
`core/checked_number.py` is the implementer's call; a `Fraction` or `Percent`
rebuilt carries the type's default `name`, as protocol 2 rebuilds it today.
`tests/unit/test_concentration.py`'s copy test stops naming this item as
outstanding. A test in `tests/unit/test_checked_number.py` named
`test_every_checked_type_unpickled_at_any_protocol_is_rebuilt_through_its_check`,
parametrized over every checked type and protocol, pins it.
