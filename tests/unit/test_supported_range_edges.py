"""Each supported-range guard admits only what the functions behind it compute.

A guard in `core/supported_ranges.py` or `core/simulation_step.py` stands in
front of the model's arithmetic, and the defect it exists to stop was found one
function at a time (`PL-YZ17`, `PL-5F76`, `PL-BPRK`): a guard admitted a value
the function behind it could not compute with, or refused one by raising a
Python error rather than the simulator's own. Each was found by somebody trying
the value after the function had shipped, because each guard's tests reached
for the edges its author thought of (`PL-V10T`).

So this draws the values instead, for every guard, and checks one property:
every value a guard refuses, it refuses with the simulator's own error, and
every value it admits, each function behind it computes with - a finite result,
or the simulator's own error. An `OverflowError`, a `ValueError`, a
`ZeroDivisionError` or a non-finite number escaping is what fails it.

**Found by type rather than listed.** The guards are every `require_supported_*`
function the two modules define, so a guard added to either is drawn without
editing this file. Each guard's quantity has one type once it is checked: the
run's step and its step count, which the guards take as `SimulationStep` and
`StepCount` (`PL-0GJC`, `PL-CN5S`), and for a quantity a guard takes as a bare
`float`, the `float` subclass built only through that guard - the three flows
since `PL-0YYV`, and the case instant since `PL-CN5S`. A function is behind a
guard wherever it takes that type, under any name and on any class, so
`RunDefinition`'s `opened_at_s` is drawn although its guard names the quantity
`instant_s`, and a record is drawn through its constructor:
`UptakeEquationSettings`'s three flows are drawn at their edges, in the record
a run is built from and the way in `PL-HSFV` went through (`PL-51B7`). A
constructor counts where it checks or computes - written by hand, or a
dataclass's with a `__post_init__` - and not where it only stores, as
`app/controller.py`'s `ResumePoint` does. An instant a run is only *read* at -
`state_at` and `segment_at`, which the run's own opening and reach bound - is a
plain `float` and behind no guard here; and a collection of instants, which a
function is handed whole, is handed the one in `TYPICAL`.

**Every place, every edge.** A function is handed the drawn value where it
first takes the quantity's type, and where it takes the type again, each edge
the type admits in turn: a step's span is two instants, and a crossing inside
it is computed only where they differ.

**What is kept by hand is how to build what is found, and each part fails by
name rather than going untested.** `RECEIVERS` builds each class a method is
found on, and the record a constructor is built from with only its drawn fields
replaced; `TYPICAL` holds a value for a parameter no guard draws, where a
function takes one without a default; and `TIED` builds a record whose own
check ties a drawn field to others, as `UptakeEquationSettings` ties cardiac
output to the tissue flows that sum to it. A constructor is held to more than
the rest: nothing else it is handed has moved off a value it accepts, so it
builds at every value its guard admits, and a record refusing one is named.
That is what stops a tie nothing here keeps from drawing nothing at all.

**One infinity is the domain's own.** A time constant is infinite where nothing
flows, which `core/__init__.py` has each compartment return rather than divide
by zero, and where so little flows that the quotient overflows, `inf` is the
same answer over any span a run can reach. `INFINITE_WHERE_NOTHING_FLOWS` names
the properties it may come from; nothing else may compute `inf`, and nothing at
all `-inf` or `nan`.

**Drawn, and the edges every time.** Hypothesis draws each value across and
beyond every bound the two modules declare, derandomized, so a red run
reproduces exactly and the suite stays deterministic. The IEEE 754 edges - the
infinities, NaN, signed zero, the subnormals, the largest float - each bound and
its two neighbours, and an integer one digit past what CPython will print
(`sys.get_int_max_str_digits`), are checked on every run, whatever Hypothesis
draws.
"""

from __future__ import annotations

import dataclasses
import importlib
import inspect
import math
import pkgutil
import sys
import types
import typing
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from functools import cache
from itertools import product

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import anesthesia_sim
from anesthesia_sim.app.bookmarks import BookmarkCrossing, BookmarkSet, TimeBookmark
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import SIMULATION_TICK_INTERVAL_S
from anesthesia_sim.app.playback import PlaybackRate
from anesthesia_sim.core import simulation_step, supported_ranges
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.exceptions import AnesthesiaSimulationError
from anesthesia_sim.core.governing_equations import UptakeEquationSettings
from anesthesia_sim.core.patient import PatientCompartments
from anesthesia_sim.core.run_definition import Keyframe, RunDefinition
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.simulation_step import (
    MAXIMUM_SIMULATION_STEP_S,
    MINIMUM_SIMULATION_STEP_S,
    SimulationStep,
)
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    CardiacOutput,
    CaseInstant,
    StepCount,
    describe_count,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

GUARD_MODULES = (supported_ranges, simulation_step)

Function = Callable[..., object]


def _run_definition() -> RunDefinition:
    system = AgentUptakeSystem.default()

    return RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )


def _equation_settings_at(cardiac_output_l_min: CardiacOutput) -> UptakeEquationSettings:
    """The settings a run is built from at this cardiac output, each tissue's
    flow its share of it, as the patient's own are (`PatientCompartments`)."""

    system = AgentUptakeSystem.default()
    system.set_cardiac_output(cardiac_output_l_min)

    return system.equation_settings()


def _patient_at(cardiac_output_l_min: CardiacOutput) -> PatientCompartments:
    """A patient at this cardiac output, set rather than copied: its constructor
    refuses compartments perfused at another output, which a copy made with
    `dataclasses.replace` hands it (`PL-Z0T3`)."""

    patient = AgentUptakeSystem.default().patient
    patient.set_cardiac_output(cardiac_output_l_min)

    return patient


# A time bookmark has no default, so the one the bookmark classes are built
# with marks the middle of the span, where a step can reach it from either side.
MARK = TimeBookmark(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S / 2))

# How to build each class a guard's quantity is found on, and the record a
# constructor is built from with only its drawn fields replaced: at its
# defaults where it has them, and a bookmark set holding the one mark, and a
# crossing naming it, since a crossing names at least one. Kept by hand, and
# checked: a method found on a class missing here fails the test by name.
RECEIVERS: Mapping[type, Callable[[], object]] = {
    AgentUptakeSystem: AgentUptakeSystem.default,
    AlveolarCompartment: lambda: AgentUptakeSystem.default().alveoli,
    BookmarkCrossing: lambda: BookmarkCrossing(MARK.instant_s, time_bookmarks=(MARK,)),
    BookmarkSet: lambda: BookmarkSet(time_bookmarks=(MARK,)),
    BranchedCase: lambda: BranchedCase(SimulationController()),
    BreathingCircuit: lambda: AgentUptakeSystem.default().circuit,
    Keyframe: lambda: _run_definition().segments[0].opening,
    PatientCompartments: lambda: AgentUptakeSystem.default().patient,
    PlaybackRate: lambda: PlaybackRate(multiplier=1),
    RunDefinition: _run_definition,
    SimulationController: SimulationController,
    SimulationState: SimulationState,
    TimeBookmark: lambda: MARK,
    UptakeEquationSettings: lambda: AgentUptakeSystem.default().equation_settings(),
}

# How to build a record at a drawn value where its own check ties that field to
# others, so that the field replaced alone would be refused at every value but
# the one it holds: the tissue flows sum to cardiac output.
TIED: Mapping[tuple[type, type], Callable[[typing.Any], object]] = {
    (UptakeEquationSettings, CardiacOutput): _equation_settings_at,
    (PatientCompartments, CardiacOutput): _patient_at,
}

# A value for a parameter the guard being drawn does not bound, where a
# function behind it takes one without a default: the shipped tick, the count
# of a run that has not stepped and the state it opens at, and a bookmark
# set's view of a run that has reached no mark, has crossed no height and is
# neither at its cap nor failed.
TYPICAL: Mapping[str, object] = {
    "after": {},
    "before": {},
    "initial_state": AgentUptakeSystem.default().state_vector(),
    "reached_crossings": frozenset(),
    "reached_instants_s": frozenset(),
    "run_failed": False,
    "step_count": StepCount(0),
    "stopped_at_cap": False,
    "tick_interval_s": SIMULATION_TICK_INTERVAL_S,
}

# The properties that may compute `inf`: a time constant where nothing flows,
# or so little that the quotient overflows. The tissues' and the venous pool's
# say the same, and are not here because nothing drawn builds one alone.
INFINITE_WHERE_NOTHING_FLOWS: frozenset[object] = frozenset({BreathingCircuit.time_constant_s})


def _without_none(annotation: object) -> object:
    """`X | None` read as `X`, the optional step a run has before it steps."""

    members = [member for member in typing.get_args(annotation) if member is not type(None)]
    is_union = (
        isinstance(annotation, types.UnionType) or typing.get_origin(annotation) is typing.Union
    )

    return members[0] if is_union and len(members) == 1 else annotation


@cache
def _parameters(function: Function) -> dict[str, object]:
    """Each annotated parameter's type, in signature order, `self` excluded."""

    hints = typing.get_type_hints(function)

    return {
        name: _without_none(hints[name])
        for name in inspect.signature(function).parameters
        if name in hints
    }


def _modules() -> Iterator[types.ModuleType]:
    for found in pkgutil.walk_packages(anesthesia_sim.__path__, f"{anesthesia_sim.__name__}."):
        yield importlib.import_module(found.name)


def _checks_or_computes(owner: type, name: str) -> bool:
    if name != "__init__":
        return not name.startswith("_")

    return not dataclasses.is_dataclass(owner) or hasattr(owner, "__post_init__")


def _callables() -> Iterator[tuple[type | None, Function]]:
    """Every public function in the package, and every public method and
    every constructor that checks or computes, with the class it is on."""

    for module in _modules():
        for name, value in vars(module).items():
            if getattr(value, "__module__", None) != module.__name__:
                continue

            if inspect.isfunction(value) and not name.startswith("_"):
                yield None, value
            elif inspect.isclass(value):
                for member_name, member in vars(value).items():
                    if inspect.isfunction(member) and _checks_or_computes(value, member_name):
                        yield value, member


GUARDS: tuple[Function, ...] = tuple(
    function
    for module in GUARD_MODULES
    for name, function in vars(module).items()
    if name.startswith("require_supported_")
    and inspect.isfunction(function)
    and function.__module__ == module.__name__
)

CALLABLES = tuple(_callables())


def _built_types() -> dict[str, type]:
    """The `float` subclass each guarded quantity is built as, by the name its
    constructor gives it: `FreshGasFlow(fresh_gas_flow_l_min)` names the
    quantity `require_supported_fresh_gas_flow` bounds (`PL-0YYV`)."""

    return {
        name: value
        for module in GUARD_MODULES
        for value in vars(module).values()
        if inspect.isclass(value)
        and issubclass(value, float)
        and value is not float
        and value.__module__ == module.__name__
        for name in _parameters(value.__new__)
    }


def _checked_types() -> dict[str, type]:
    """The type each guarded quantity has once checked: the narrowest any
    guard gives its name, so the run's step is `SimulationStep` although its
    own guard, which builds that type, takes a `float`; and for a quantity
    no guard takes as more than a `float`, the type built through its guard,
    which is how the three flows and the case instant are found."""

    checked: dict[str, type] = {}
    built = _built_types()

    for guard in GUARDS:
        for name, annotation in _parameters(guard).items():
            assert isinstance(annotation, type)

            if name in built and issubclass(built[name], annotation):
                annotation = built[name]

            if name not in checked or issubclass(annotation, checked[name]):
                checked[name] = annotation

    return checked


CHECKED = _checked_types()


def _behind(guard: Function) -> tuple[tuple[type | None, Function], ...]:
    """Every function taking a type the guard's quantities are checked as,
    whatever it names the parameter and whatever class it is on."""

    checked = {CHECKED[name] for name in _parameters(guard)}

    return tuple(
        (owner, function)
        for owner, function in CALLABLES
        if function is not guard and not checked.isdisjoint(_parameters(function).values())
    )


BOUNDS = sorted(
    {
        value
        for module in GUARD_MODULES
        for name, value in vars(module).items()
        if name.startswith(("MINIMUM_", "MAXIMUM_")) and type(value) is float
    }
)

TOO_LONG_TO_PRINT = 10 ** sys.get_int_max_str_digits()


def _neighbours(value: float) -> tuple[float, float, float]:
    return math.nextafter(value, -math.inf), value, math.nextafter(value, math.inf)


FLOAT_EDGES = tuple(
    {
        repr(value): value
        for value in (
            math.inf,
            -math.inf,
            math.nan,
            0.0,
            -0.0,
            5e-324,
            -5e-324,
            math.nextafter(sys.float_info.min, 0.0),
            sys.float_info.min,
            -sys.float_info.min,
            sys.float_info.max,
            -sys.float_info.max,
            *(edge for bound in BOUNDS for edge in _neighbours(bound)),
        )
    }.values()
)


def _admitted_step(seconds: float) -> SimulationStep | None:
    try:
        return SimulationStep(seconds)
    except AnesthesiaSimulationError:
        return None


STEP_EDGES = tuple(step for step in map(_admitted_step, FLOAT_EDGES) if step is not None)

# The finest and the coarsest step, which every edge is stepped at. The step's
# own neighbours are its guard's edges, and reach every function behind it
# from there.
EDGE_STEPS = (min(STEP_EDGES), max(STEP_EDGES))

STEPS = st.floats(min_value=MINIMUM_SIMULATION_STEP_S, max_value=MAXIMUM_SIMULATION_STEP_S).map(
    SimulationStep
)

FLOATS = st.one_of(
    st.floats(),
    *(
        st.floats(min_value=bound - max(1.0, abs(bound)), max_value=bound + max(1.0, abs(bound)))
        for bound in BOUNDS
    ),
)


def _spans(step: SimulationStep) -> list[int]:
    """How many steps reach each bound, which is where a count guard's own
    bound falls: every count here is a span of steps."""

    return [math.floor(bound / step) for bound in BOUNDS if bound > 0]


def _admitted_count(count: int) -> StepCount | None:
    try:
        return StepCount(count)
    except AnesthesiaSimulationError:
        return None


def _count_edges(step: SimulationStep) -> tuple[StepCount, ...]:
    """The counts a count guard's edges fall on, as `StepCount` admits them.

    The negative edges are offered to the type, which refuses them with the
    simulator's own error or fails this test, and reach no guard: a count is
    checked whole and nonnegative once, where it is built (`PL-CN5S`).
    """

    edges = {
        0,
        1,
        -1,
        2**53,
        2**53 + 1,
        2**63,
        TOO_LONG_TO_PRINT,
        -TOO_LONG_TO_PRINT,
        *(span + offset for span in _spans(step) for offset in (-1, 0, 1)),
    }

    return tuple(count for count in map(_admitted_count, sorted(edges)) if count is not None)


def _counts(step: SimulationStep) -> st.SearchStrategy[StepCount]:
    return st.one_of(
        st.integers(min_value=0),
        st.sampled_from(_count_edges(step)),
        *(st.integers(min_value=0, max_value=2 * span + 1) for span in _spans(step)),
    ).map(StepCount)


def _edges(annotation: object, step: SimulationStep) -> tuple[object, ...]:
    if annotation is SimulationStep:
        return (step,)

    if annotation is StepCount:
        return _count_edges(step)

    if annotation is float:
        return FLOAT_EDGES

    pytest.fail(f"no edges for a guard parameter of type {annotation!r}")


def _drawn(annotation: object, step: SimulationStep) -> st.SearchStrategy[object]:
    if annotation is SimulationStep:
        return st.just(step)

    if annotation is StepCount:
        return _counts(step)

    if annotation is float:
        return FLOATS

    pytest.fail(f"no strategy for a guard parameter of type {annotation!r}")


@cache
def _pools(guard: Function, step: SimulationStep) -> dict[type, tuple[object, ...]]:
    """Each of the guard's quantities, every edge its type admits at this step,
    built as that type: what a place that takes the type again is handed."""

    pools: dict[type, tuple[object, ...]] = {}

    for name, annotation in _parameters(guard).items():
        admitted = []

        for edge in _edges(annotation, step):
            try:
                admitted.append(CHECKED[name](edge))
            except AnesthesiaSimulationError:
                continue

        pools[CHECKED[name]] = tuple(admitted)

    return pools


def _require_finite(value: object, function: Function) -> None:
    if isinstance(value, float):
        assert math.isfinite(value), f"{function.__qualname__} computed {value}"
    elif isinstance(value, (tuple, list)):
        for item in value:
            _require_finite(item, function)
    elif dataclasses.is_dataclass(value) and not isinstance(value, type):
        for field in dataclasses.fields(value):
            _require_finite(getattr(value, field.name), function)


def _drawings(
    function: Function,
    values: Mapping[type, object],
    pools: Mapping[type, tuple[object, ...]],
    step: SimulationStep,
) -> Iterator[dict[str, object]]:
    """Each way to hand `function` what was drawn: the drawn value where it
    first takes the value's type, every value of the type's pool in turn where
    it takes the type again, and the run's step wherever it takes a step."""

    first: dict[str, object] = {}
    again: dict[str, tuple[object, ...]] = {}

    annotations = _parameters(function)

    for name, annotation in annotations.items():
        if annotation in values:
            if any(annotations[taken] is annotation for taken in first):
                again[name] = pools[typing.cast(type, annotation)]
            else:
                first[name] = values[typing.cast(type, annotation)]
        elif annotation is SimulationStep:
            first[name] = step

    for chosen in product(*again.values()):
        yield {**first, **dict(zip(again, chosen, strict=True))}


def _arguments(function: Function, drawing: Mapping[str, object]) -> dict[str, object]:
    """What to call `function` with: what was drawn for it, and otherwise a
    default, the shipped value `TYPICAL` holds, or the class `RECEIVERS`
    builds."""

    annotations = _parameters(function)
    arguments: dict[str, object] = {}

    for name, parameter in inspect.signature(function).parameters.items():
        if name == "self":
            continue

        if name in drawing:
            arguments[name] = drawing[name]
        elif parameter.default is not inspect.Parameter.empty:
            continue
        elif name in TYPICAL:
            arguments[name] = TYPICAL[name]
        elif annotations.get(name) in RECEIVERS:
            arguments[name] = RECEIVERS[typing.cast(type, annotations[name])]()
        else:
            pytest.fail(
                f"{function.__qualname__} takes {name}, which this guard does not draw and "
                f"TYPICAL holds no value for"
            )

    return arguments


def _build(
    owner: type, function: Function, values: Mapping[type, object], drawing: Mapping[str, object]
) -> object:
    """`owner` built with what was drawn for its constructor: through `TIED`
    where it ties the drawn field to others, from the record `RECEIVERS` holds
    with only the drawn fields replaced, or from the constructor's defaults."""

    for drawn, value in values.items():
        if (owner, drawn) in TIED:
            return TIED[owner, drawn](value)

    if dataclasses.is_dataclass(owner) and owner in RECEIVERS:
        record: typing.Any = RECEIVERS[owner]()

        return dataclasses.replace(record, **drawing)

    return owner(**_arguments(function, drawing))


def _step(built: object, step: SimulationStep) -> None:
    """Take a step on whatever was just built or set, and read what it reports,
    which is where a value set rather than computed is computed with."""

    for owner, function in CALLABLES:
        if owner is type(built) and function.__name__ != "__init__":
            if SimulationStep in _parameters(function).values():
                for drawing in _drawings(function, {}, {}, step):
                    _require_finite(
                        getattr(built, function.__name__)(**_arguments(function, drawing)), function
                    )

    for name, member in vars(type(built)).items():
        if isinstance(member, property) and not name.startswith("_") and member.fget is not None:
            returned = typing.get_type_hints(member.fget).get("return")

            if isinstance(returned, type) and issubclass(returned, float):
                value = getattr(built, name)

                if not (member in INFINITE_WHERE_NOTHING_FLOWS and value == math.inf):
                    _require_finite(value, member.fget)


@contextmanager
def _naming(called: str, values: Mapping[str, object], step: SimulationStep) -> Iterator[None]:
    try:
        yield
    except BaseException as failure:
        shown = ", ".join(
            f"{name}={describe_count(value) if isinstance(value, int) else repr(value)}"
            for name, value in values.items()
        )
        failure.add_note(f"{called}({shown}), stepping at {step!r} s")
        raise


def _computes_with(
    owner: type | None,
    function: Function,
    values: Mapping[type, object],
    pools: Mapping[type, tuple[object, ...]],
    step: SimulationStep,
) -> None:
    """One function behind a guard, handed what the guard admitted: a finite
    result or the simulator's own refusal - and a constructor builds."""

    for drawing in _drawings(function, values, pools, step):
        with _naming(function.__qualname__, drawing, step):
            if owner is not None and function.__name__ == "__init__":
                try:
                    built: object | None = _build(owner, function, values, drawing)
                except AnesthesiaSimulationError as refusal:
                    pytest.fail(
                        f"{owner.__qualname__} refused what its guard admits, with nothing else "
                        f"moved: {refusal}. A record whose own check ties the drawn field to "
                        "others is built through TIED"
                    )

                result: object = None
            else:
                built = RECEIVERS[owner]() if owner is not None else None
                call = function if built is None else getattr(built, function.__name__)

                try:
                    result = call(**_arguments(function, drawing))
                except AnesthesiaSimulationError:
                    continue

            _require_finite(result, function)

            if built is not None:
                try:
                    _step(built, step)
                except AnesthesiaSimulationError:
                    continue


def _check(guard: Function, values: Mapping[str, object], step: SimulationStep) -> None:
    """The property, for one draw: a refusal is the simulator's own error, and
    an admitted value is one every function behind the guard computes with."""

    with _naming(guard.__name__, values, step):
        try:
            guard(**values)
        except AnesthesiaSimulationError:
            return

        admitted = {CHECKED[name]: CHECKED[name](value) for name, value in values.items()}
        step = typing.cast(SimulationStep, admitted.get(SimulationStep, step))

        for owner, function in _behind(guard):
            _computes_with(owner, function, admitted, _pools(guard, step), step)


@pytest.mark.parametrize("guard", GUARDS, ids=lambda guard: guard.__name__)
def test_each_guard_admits_only_what_its_functions_compute(guard: Function) -> None:
    behind = _behind(guard)
    uncallable = [
        function.__qualname__
        for owner, function in behind
        if owner is not None and function.__name__ != "__init__" and owner not in RECEIVERS
    ]

    assert behind, f"{guard.__name__} has no function behind it that this test can find"
    assert not uncallable, f"no way to build the class behind {uncallable}: add it to RECEIVERS"

    annotations = _parameters(guard)

    for step in EDGE_STEPS:
        edges = [_edges(annotation, step) for annotation in annotations.values()]

        for values in product(*edges):
            _check(guard, dict(zip(annotations, values, strict=True)), step)

    @settings(derandomize=True, database=None, deadline=None, max_examples=50)
    @given(st.data())
    def drawn(data: st.DataObject) -> None:
        step = data.draw(STEPS, label="step")
        values = {
            name: data.draw(_drawn(annotation, step), label=name)
            for name, annotation in annotations.items()
        }

        _check(guard, values, step)

    drawn()
