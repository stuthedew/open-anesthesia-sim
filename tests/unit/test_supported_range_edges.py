"""Each supported-range guard accepts only values that the functions behind it can compute with.

A guard in `core/supported_ranges.py` or `core/simulation_step.py` sits in
front of the model's arithmetic. The defect that a guard exists to stop was
found one function at a time (`PL-YZ17`, `PL-5F76`, `PL-BPRK`). A guard
accepted a value that the function behind it could not compute with, or
refused a value by raising a Python error rather than the simulator's own
error. Each defect was found by somebody trying the value after the function
had shipped, because each guard's tests covered only the edges that its
author thought of (`PL-V10T`).

So this module draws the values instead, for every guard, and checks one
property. Every value that a guard refuses, it refuses with the simulator's
own error. Every function behind a guard can compute with every value that
the guard accepts, giving either a finite result or the simulator's own
error. The test
fails if an `OverflowError`, a `ValueError`, a `ZeroDivisionError` or a
non-finite number escapes.

**Found by type rather than listed.** The guards are every
`require_supported_*` function that the two modules define, so a guard added
to either module is drawn without editing this file. Each guard's quantity
has one type once it is checked. The run's step and its step count have the
types that the guards take, `SimulationStep` and `StepCount` (`PL-0GJC`,
`PL-CN5S`). A quantity that a guard takes as a bare `float` has the `float`
subclass that is built only through that guard. Those are the three flows
since `PL-0YYV`, and the case instant since `PL-CN5S`. A function is behind a
guard wherever it takes that type, under any name and on any class. So
`RunDefinition`'s `opened_at_s` is drawn, although its guard names the
quantity `instant_s`. A record is drawn through its constructor. So
`UptakeEquationSettings`'s three flows are drawn at their edges, in the
record that a run is built from. That record is how flows outside the
supported ranges reached a run in `PL-HSFV` (`PL-51B7`). A constructor
counts where it checks or computes. That includes a constructor written by
hand, and a dataclass's constructor when the dataclass has a `__post_init__`
or a `__setattr__` of its own, which checks each field as the constructor
writes it (`PL-19Y0`). A constructor does not count where it only stores,
as `app/controller.py`'s `ResumePoint` does. An instant at which a run is
only *read*, as in `state_at` and `segment_at`, is a plain `float` and is
behind no guard here. The run's own opening and reach bound those instants.
A function that is handed a collection of instants whole is handed the one
in `TYPICAL`.

**Every place, every edge.** A function is handed the drawn value where it
first takes the quantity's type. Where it takes the type again, it is handed
each edge that the type accepts, in turn. For example, a step's span is two
instants, and a crossing inside the span is computed only where the two
differ.

**What is kept by hand is how to build what is found, and each part fails by
name rather than going untested.** `RECEIVERS` builds each class that a
method is found on. It also builds the record that a constructor is built
from, with only its drawn fields replaced. `TYPICAL` holds a value for a
parameter that no guard draws, where a function takes one without a default.
`TIED` builds a record whose own check ties a drawn field to other fields, as
`UptakeEquationSettings` ties cardiac output to the tissue flows that sum to
it. A constructor is held to a stricter rule than the rest. Nothing else that
it is handed has moved off a value it accepts, so it must build at every
value its guard accepts, and a record that refuses one is named. That rule
stops a tie that `TIED` does not list from silently drawing nothing at all.

**One infinity is the domain's own.** A time constant is infinite where
nothing flows. `core/__init__.py` has each compartment return infinity there
rather than divide by zero. Where so little flows that the quotient
overflows, `inf` is the same answer over any span that a run can reach.
`INFINITE_WHERE_NOTHING_FLOWS` names the properties that may compute this infinity.
Nothing else may compute `inf`, and nothing at all may compute `-inf` or
`nan`.

**Drawn, and the edges every time.** Hypothesis draws each value across and
beyond every bound that the two modules declare. The draw is derandomized, so
a failing run reproduces exactly and the suite stays deterministic. Some
edges are checked on every run, whatever Hypothesis draws. They are the IEEE
754 edges (the infinities, NaN, signed zero, the subnormals and the largest
float), each bound and its two neighbours, and an integer one digit longer
than CPython will print (`sys.get_int_max_str_digits`).
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
from anesthesia_sim.app.chart_time_base import SELECTABLE_TIME_BASES
from anesthesia_sim.app.control_record import ControlChange, ControlInput
from anesthesia_sim.app.control_timeline import ControlAdjustment
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import SIMULATION_TICK_INTERVAL_S
from anesthesia_sim.app.playback import PlaybackRate
from anesthesia_sim.core import simulation_step, supported_ranges
from anesthesia_sim.core.agent_simulation_validation import AgentSimulationValidator
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.blood import VenousBloodCompartment
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
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

GUARD_MODULES = (supported_ranges, simulation_step)

Function = Callable[..., object]


def _run_definition() -> RunDefinition:
    system = AgentUptakeSystem.default()

    return RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )


def _equation_settings_at(cardiac_output_l_min: CardiacOutput) -> UptakeEquationSettings:
    """Return the settings that a run is built from at this cardiac output.

    Each tissue's flow is its share of the output, as the patient's own flows
    are (`PatientCompartments`).
    """

    system = AgentUptakeSystem.default()
    system.set_cardiac_output(cardiac_output_l_min)

    return system.equation_settings()


# A time bookmark has no default. So the bookmark that the bookmark classes are
# built with marks the middle of the span, where a step can reach it from
# either side.
MARK = TimeBookmark(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S / 2))

# How to build each class that a guard's quantity is found on, and the record
# that a constructor is built from, with only its drawn fields replaced. Each
# is built at its defaults where it has them. The bookmark set holds the one
# mark, and the crossing names it, because a crossing names at least one mark.
# This map is kept by hand, and checked: a method found on a class missing
# here fails the test by name.
RECEIVERS: Mapping[type, Callable[[], object]] = {
    AgentUptakeSystem: AgentUptakeSystem.default,
    AlveolarCompartment: lambda: AgentUptakeSystem.default().alveoli,
    BookmarkCrossing: lambda: BookmarkCrossing(MARK.instant_s, time_bookmarks=(MARK,)),
    BookmarkSet: lambda: BookmarkSet(time_bookmarks=(MARK,)),
    BranchedCase: lambda: BranchedCase(SimulationController()),
    BreathingCircuit: lambda: AgentUptakeSystem.default().circuit,
    ControlAdjustment: lambda: ControlAdjustment(
        ControlInput.FRESH_GAS_FLOW, CaseInstant(0.0), CaseInstant(0.0), 6.0, 2.0, "L/min", 1
    ),
    ControlChange: lambda: ControlChange(
        CaseInstant(0.0), 1, ControlInput.FRESH_GAS_FLOW, 6.0, 2.0, "L/min"
    ),
    Keyframe: lambda: _run_definition().segments[0].opening,
    PatientCompartments: lambda: AgentUptakeSystem.default().patient,
    PlaybackRate: lambda: PlaybackRate(multiplier=1),
    RunDefinition: _run_definition,
    SimulationController: SimulationController,
    SimulationState: SimulationState,
    TimeBookmark: lambda: MARK,
    TissueGroup: lambda: AgentUptakeSystem.default().patient.fat,
    UptakeEquationSettings: lambda: AgentUptakeSystem.default().equation_settings(),
}

# How to build a record at a drawn value where the record's own check ties
# that field to other fields. Replacing that field alone would be refused at
# every value except the one it already holds. Here, the tissue flows must sum
# to cardiac output.
TIED: Mapping[tuple[type, type], Callable[[typing.Any], object]] = {
    (UptakeEquationSettings, CardiacOutput): _equation_settings_at
}

# A value for each parameter that the guard being drawn does not bound, where
# a function behind the guard takes one without a default. The values are the
# shipped tick, the count of a run that has not stepped and the state it opens
# at, and the narrowest width that the chart's selector offers. The other
# values give a bookmark set's view of a run that has reached no mark, has
# crossed no height and is neither at its cap nor failed.
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
    "time_base": SELECTABLE_TIME_BASES[0],
}

# The properties that may compute `inf`: a time constant where nothing flows,
# or where so little flows that the quotient overflows. The time constants of
# the tissues and of the venous pool behave the same way. They are not listed
# here because nothing drawn builds a tissue or the venous pool on its own.
INFINITE_WHERE_NOTHING_FLOWS: frozenset[object] = frozenset({BreathingCircuit.time_constant_s})


def _without_none(annotation: object) -> object:
    """Return `X` for `X | None`, such as the optional step that a run has before it steps."""

    members = [member for member in typing.get_args(annotation) if member is not type(None)]
    is_union = (
        isinstance(annotation, types.UnionType) or typing.get_origin(annotation) is typing.Union
    )

    return members[0] if is_union and len(members) == 1 else annotation


@cache
def _parameters(function: Function) -> dict[str, object]:
    """Return each annotated parameter's type, in signature order, excluding `self`.

    A method of a generic class, such as `class _RunCopies[W: QWidget]`, names
    the class's type parameters in its annotations. Those parameters are not
    module globals, so they are passed in from the class the method is on.
    """

    owner: object = sys.modules[function.__module__]

    for part in function.__qualname__.split(".")[:-1]:
        owner = getattr(owner, part, None)

    type_parameters = getattr(owner, "__type_params__", ())
    hints = typing.get_type_hints(
        function, localns={parameter.__name__: parameter for parameter in type_parameters}
    )

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

    return (
        not dataclasses.is_dataclass(owner)
        or hasattr(owner, "__post_init__")
        or _checks_every_write(owner)
    )


def _checks_every_write(owner: type) -> bool:
    """Return whether a dataclass's constructor checks through a `__setattr__` of its own.

    `PL-19Y0` moved five records' checks out of `__post_init__` and into the
    write, which the constructor makes like any other write. While this test
    looked only for a `__post_init__`, those constructors dropped out of the
    draw and nothing failed. Among the checks lost were `BreathingCircuit`'s
    fresh gas flow and `AlveolarCompartment`'s ventilation. The `__setattr__`
    that a frozen dataclass is given refuses every write after construction
    and checks nothing, so it does not count. A frozen dataclass cannot define
    its own.
    """

    return (
        "__setattr__" in vars(owner)
        and not typing.cast(typing.Any, owner).__dataclass_params__.frozen
    )


def _callables() -> Iterator[tuple[type | None, Function]]:
    """Yield the public callables in the package, each with the class it is on.

    They are every public function, every public method, and every
    constructor that checks or computes.
    """

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
    """Return the `float` subclass that each guarded quantity is built as.

    Each subclass is keyed by the name that its constructor gives the
    quantity. For example, `FreshGasFlow(fresh_gas_flow_l_min)` names the
    quantity that `require_supported_fresh_gas_flow` bounds (`PL-0YYV`).
    """

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
    """Return the type that each guarded quantity has once it is checked.

    That type is the narrowest type that any guard gives the quantity's name.
    So the run's step is `SimulationStep`, although its own guard, which
    builds that type, takes a `float`. A quantity that no guard takes as more
    than a `float` gets the type that is built through its guard. That is how
    the three flows and the case instant are found.
    """

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
    """Return every function that takes a type the guard's quantities are checked as.

    The function may give the parameter any name, and may be on any class.
    """

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

# The finest and the coarsest step, at which every edge is stepped. The step's
# own neighbours are its guard's edges, and from there they are handed to every
# function behind the guard.
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
    """Return how many steps reach each bound.

    That is where a count guard's own bound falls, because every count here
    is a span of steps.
    """

    return [math.floor(bound / step) for bound in BOUNDS if bound > 0]


def _admitted_count(count: int) -> StepCount | None:
    try:
        return StepCount(count)
    except AnesthesiaSimulationError:
        return None


def _count_edges(step: SimulationStep) -> tuple[StepCount, ...]:
    """Return the counts at a count guard's edges, as `StepCount` accepts them.

    The negative edges are offered to the type, which must refuse them with
    the simulator's own error or this test fails. They are never passed to a
    guard, because a count is checked for being whole and nonnegative once,
    where it is built (`PL-CN5S`).
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
    """Return, for each of the guard's quantities, every edge its type accepts at this step.

    Each edge is built as the quantity's type. A place that takes the type
    again is handed these values.
    """

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
    """Yield each way to hand `function` what was drawn.

    The drawn value goes where the function first takes the value's type.
    Where the function takes the type again, it gets every value of the
    type's pool in turn. The run's step goes wherever the function takes a
    step.
    """

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
    """Return the arguments to call `function` with.

    Each argument is what was drawn for it. Otherwise it is the parameter's
    default, the shipped value that `TYPICAL` holds, or the class that
    `RECEIVERS` builds.
    """

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
    """Build `owner` with what was drawn for its constructor.

    The record is built through `TIED` where its check ties the drawn field
    to other fields. Otherwise it is built from the record that `RECEIVERS`
    holds, with only the drawn fields replaced, or from the constructor's
    defaults.
    """

    for drawn, value in values.items():
        if (owner, drawn) in TIED:
            return TIED[owner, drawn](value)

    if dataclasses.is_dataclass(owner) and owner in RECEIVERS:
        record: typing.Any = RECEIVERS[owner]()

        return dataclasses.replace(record, **drawing)

    return owner(**_arguments(function, drawing))


def _step(built: object, step: SimulationStep) -> None:
    """Take a step on whatever was just built or set, and read what it reports.

    Stepping and reading the reports is where a value that was set, rather
    than computed, is used in a computation.
    """

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
    """Call one function behind a guard with what the guard accepted.

    The function must return a finite result or raise the simulator's own
    refusal, and a constructor must build.
    """

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
    """Check the property for one draw.

    A refusal must be the simulator's own error, and every function behind
    the guard must compute with an accepted value.
    """

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


def test_the_records_that_check_every_write_are_drawn() -> None:
    """A constructor that checks through its record's `__setattr__` is drawn like a `__post_init__`.

    While the draw looked only for a `__post_init__`, it lost the five
    constructors whose checks `PL-19Y0` moved into the write, and every edge
    test still passed. So only this test shows that `_checks_every_write` is
    doing its work (found by `PL-19Y0`'s mutation review). `SimulationState`
    has checked in its `__setattr__` since `PL-8W1W`.
    """

    drawn = {owner for owner, function in CALLABLES if function.__name__ == "__init__"}

    assert {
        AgentSimulationValidator,
        AlveolarCompartment,
        BreathingCircuit,
        SimulationState,
        TissueGroup,
        VenousBloodCompartment,
    } <= drawn
