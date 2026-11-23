"""Each supported-range guard accepts only values that the functions behind it can compute with.

A guard in `core/supported_ranges.py` sits in front of the model's
arithmetic. The defect that a guard exists to stop was
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
`require_supported_*` function that the module defines, so a guard added to
the module is drawn without editing this file. Each guard's quantity has one
type once it is checked. The run's step count has the type that its guards
take, `StepCount` (`PL-CN5S`). A quantity that a guard takes as a bare `float`
or a bare `int` has the subclass that is built only through that guard. Those
are the three flows since `PL-0YYV`, which are floats, and the case instant
since `PL-CN5S`, which is a whole number of seconds. A function is behind a
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

**A run steps by one second and no other step** (`core/simulation_step.py`,
`PL-SZ6G`). So no step is drawn. Whatever is built or set is stepped by its
own `advance()`, which takes no argument.

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
beyond every bound that the module declares. Every ordinary run draws the
same values, so a failing run reproduces exactly, and a weekly run draws new
ones (`tests/hypothesis_profiles.py`). Some
edges are checked on every run, whatever Hypothesis draws. For a `float` they
are the IEEE 754 edges (the infinities, NaN, signed zero, the subnormals and
the largest float), and each bound and its two neighbours. For a count or an
instant they are each whole-number bound and the whole numbers beside it, and
an integer one digit longer than CPython will print
(`sys.get_int_max_str_digits`).
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
from anesthesia_sim.app.chart_frame import ChartFrame, RunInput, assemble_chart_frame
from anesthesia_sim.app.chart_time_base import SELECTABLE_TIME_BASES
from anesthesia_sim.app.control_record import ControlChange, ControlInput
from anesthesia_sim.app.control_timeline import ControlAdjustment
from anesthesia_sim.app.controller import (
    BranchedCase,
    RunRecord,
    RunSettings,
    SimulationController,
    SimulationSnapshot,
)
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES
from anesthesia_sim.core import supported_ranges
from anesthesia_sim.core.agent_simulation_validation import UNCOMPENSATED, AgentSimulationValidator
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.blood import VenousBloodCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.concentration import Fraction
from anesthesia_sim.core.exceptions import AnesthesiaSimulationError
from anesthesia_sim.core.governing_equations import UptakeEquationSettings
from anesthesia_sim.core.patient import PatientCompartments
from anesthesia_sim.core.run_definition import RunDefinition
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.stored_states import Keyframe, StoredStates
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    CardiacOutput,
    CaseInstant,
    StepCount,
    describe_count,
)
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

GUARD_MODULES = (supported_ranges,)

Function = Callable[..., object]


def _run_definition() -> RunDefinition:
    system = AgentUptakeSystem.default()

    return RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))


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
MARK = TimeBookmark(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S // 2))


def _chart_runs() -> tuple[RunInput, ...]:
    """One run that has not started, as a frame of the charts reads it."""

    controller = SimulationController()

    return (RunInput("Run 1", controller, controller.snapshot(), ()),)


def _chart_frame() -> ChartFrame:
    """The frame one tick draws for a run that has not started, at the narrowest width.

    A frame records the instant its window was held at and the run's newest
    instant (`PL-Z7LY`), so its constructor is drawn at both.
    """

    return assemble_chart_frame(
        _chart_runs(),
        SELECTABLE_TIME_BASES[0],
        COMPARTMENT_QUANTITIES,
        plot_width_px=CHART_PLOT_WIDTH_PX,
        held_start_s=None,
    )


# The width of a chart's plot, in logical pixels, for a frame drawn here. Any
# positive width gives the frame a column for each pixel.
CHART_PLOT_WIDTH_PX = 600.0


# How to build each class that a guard's quantity is found on, and the record
# that a constructor is built from, with only its drawn fields replaced. Each
# is built at its defaults where it has them. The bookmark set holds the one
# mark, and the crossing names it, because a crossing names at least one mark.
# This map is kept by hand, and checked: a method found on a class missing
# here fails the test by name.
RECEIVERS: Mapping[type, Callable[[], object]] = {
    AgentUptakeSystem: AgentUptakeSystem.default,
    ChartFrame: _chart_frame,
    AlveolarCompartment: lambda: AgentUptakeSystem.default().alveoli,
    BookmarkCrossing: lambda: BookmarkCrossing(MARK.instant_s, time_bookmarks=(MARK,)),
    BookmarkSet: lambda: BookmarkSet(time_bookmarks=(MARK,)),
    BranchedCase: lambda: BranchedCase(SimulationController()),
    BreathingCircuit: lambda: AgentUptakeSystem.default().circuit,
    ControlAdjustment: lambda: ControlAdjustment(
        ControlInput.FRESH_GAS_FLOW, CaseInstant(0), CaseInstant(0), 6.0, 2.0, 1
    ),
    ControlChange: lambda: ControlChange(
        CaseInstant(0), 1, ControlInput.FRESH_GAS_FLOW, 6.0, 2.0, "L/min"
    ),
    Keyframe: lambda: Keyframe(CaseInstant(0), AgentUptakeSystem.default().case_state()),
    PatientCompartments: lambda: AgentUptakeSystem.default().patient,
    RunDefinition: _run_definition,
    # A run's settings, record and snapshot check that a failure's reason and its
    # kind are recorded together (`PL-XWCH`), so their constructors are drawn.
    RunRecord: lambda: SimulationController().record(),
    RunSettings: lambda: SimulationController().settings(),
    SimulationController: SimulationController,
    SimulationSnapshot: lambda: SimulationController().snapshot(),
    SimulationState: SimulationState,
    StoredStates: lambda: StoredStates(
        AgentUptakeSystem.default().case_state(), CaseInstant(0), UNCOMPENSATED
    ),
    TimeBookmark: lambda: MARK,
    TissueGroup: lambda: AgentUptakeSystem.default().patient.fat,
    UptakeEquationSettings: lambda: AgentUptakeSystem.default().equation_settings(),
    VenousBloodCompartment: lambda: AgentUptakeSystem.default().patient.venous_blood,
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
# count of a run that has not stepped and the state it opens at, and the
# narrowest width that the chart's selector offers. A chart frame is assembled
# for one run that has not started, with every compartment shown, and a
# window is stepped from one that starts at zero. The venous pool
# stepped on its own takes a one-second step towards a tissue return of zero.
# The other values give a bookmark set's view of a run that has reached no
# mark, has crossed no height and is neither at its cap nor failed. The squarings
# are those of a shipped agent's step, which needs none. A prediction at chosen
# seconds is given none, so it predicts nothing past its opening.
TYPICAL: Mapping[str, object] = {
    "adjustment_count": 0,
    "after": {},
    "before": {},
    "compensation": UNCOMPENSATED,
    "initial_state": AgentUptakeSystem.default().state_vector(),
    "name": "Branch 1",
    "opening": AgentUptakeSystem.default().case_state(),
    "plot_width_px": CHART_PLOT_WIDTH_PX,
    "reached_crossings": frozenset(),
    "run_failed": False,
    "runs": _chart_runs(),
    "seconds": (),
    "shown": COMPARTMENT_QUANTITIES,
    "squarings": 0,
    "start_s": 0.0,
    "simulation_step_s": 1.0,
    "snapshot": None,
    "step_count": StepCount(0),
    "stopped_at_cap": False,
    "time_base": SELECTABLE_TIME_BASES[0],
    "tissue_return_partial_pressure_fraction": Fraction(0.0),
}

# These are the properties and methods that may compute `inf`. Each is a time
# constant that is `inf` where nothing flows, or where so little flows that the
# quotient overflows. The venous pool's time constant takes the cardiac output,
# so it is drawn (`PL-GKG4`). A tissue's time constant behaves the same way. It
# is not listed here because it takes a `BloodFlow`, which no guard in these
# modules builds.
INFINITE_WHERE_NOTHING_FLOWS: frozenset[object] = frozenset(
    {BreathingCircuit.time_constant_s, VenousBloodCompartment.time_constant_s}
)


def _without_none(annotation: object) -> object:
    """Return `X` for `X | None`, such as a chart frame's optional branch point."""

    members = [member for member in typing.get_args(annotation) if member is not type(None)]
    is_union = (
        isinstance(annotation, types.UnionType) or typing.get_origin(annotation) is typing.Union
    )

    return members[0] if is_union and len(members) == 1 else annotation


@cache
def _parameters(function: Function) -> dict[str, object]:
    """Return each annotated parameter's type, in signature order, excluding `self`.

    A method of a generic class, such as `class _RunWidgets[W: QWidget]`, names
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
    """Return the `float` or `int` subclass that each guarded quantity is built as.

    Each subclass is keyed by the name that its constructor gives the
    quantity. For example, `FreshGasFlow(fresh_gas_flow_l_min)` names the
    quantity that `require_supported_fresh_gas_flow` bounds (`PL-0YYV`), and
    `CaseInstant(instant_s)` names the one that
    `require_supported_case_instant` bounds.
    """

    return {
        name: value
        for module in GUARD_MODULES
        for value in vars(module).values()
        if inspect.isclass(value)
        and issubclass(value, (float, int))
        and value.__module__ == module.__name__
        for name in _parameters(value.__new__)
    }


def _checked_types() -> dict[str, type]:
    """Return the type that each guarded quantity has once it is checked.

    That type is the narrowest type that any guard gives the quantity's name.
    A quantity that no guard takes as more than a `float` or an `int` gets the
    type that is built through its guard. That is how the three flows and the
    case instant are found.
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

# The bounds that the module declares as whole numbers: the supported run
# length in seconds, and the count of one-second steps that reaches it.
WHOLE_BOUNDS = sorted(
    {
        value
        for module in GUARD_MODULES
        for name, value in vars(module).items()
        if name.startswith(("MINIMUM_", "MAXIMUM_")) and type(value) is int
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

FLOATS = st.one_of(
    st.floats(),
    *(
        st.floats(min_value=bound - max(1.0, abs(bound)), max_value=bound + max(1.0, abs(bound)))
        for bound in BOUNDS
    ),
)

# The whole numbers at a count's or an instant's edges: zero and the numbers
# beside it, each whole-number bound and the numbers beside it, the first
# integers that a `float` cannot hold exactly, and an integer too long to print.
WHOLE_EDGES = tuple(
    sorted(
        {
            0,
            1,
            -1,
            2**53,
            2**53 + 1,
            2**63,
            TOO_LONG_TO_PRINT,
            -TOO_LONG_TO_PRINT,
            *(bound + offset for bound in WHOLE_BOUNDS for offset in (-1, 0, 1)),
        }
    )
)

WHOLE_NUMBERS = st.one_of(
    st.integers(),
    st.sampled_from(WHOLE_EDGES),
    *(st.integers(min_value=-bound, max_value=2 * bound + 1) for bound in WHOLE_BOUNDS),
)


def _admitted_count(count: int) -> StepCount | None:
    try:
        return StepCount(count)
    except AnesthesiaSimulationError:
        return None


# The counts at a count guard's edges, as `StepCount` accepts them. The
# negative edges are offered to the type, which must refuse them with the
# simulator's own error or this module fails to import. They are never passed
# to a guard, because a count is checked for being whole and nonnegative once,
# where it is built (`PL-CN5S`).
COUNT_EDGES = tuple(count for count in map(_admitted_count, WHOLE_EDGES) if count is not None)

COUNTS = st.one_of(
    st.integers(min_value=0),
    st.sampled_from(COUNT_EDGES),
    *(st.integers(min_value=0, max_value=2 * bound + 1) for bound in WHOLE_BOUNDS),
).map(StepCount)


def _edges(annotation: object) -> tuple[object, ...]:
    if annotation is StepCount:
        return COUNT_EDGES

    if annotation is float:
        return FLOAT_EDGES

    if annotation is int:
        return WHOLE_EDGES

    pytest.fail(f"no edges for a guard parameter of type {annotation!r}")


def _drawn(annotation: object) -> st.SearchStrategy[object]:
    if annotation is StepCount:
        return COUNTS

    if annotation is float:
        return FLOATS

    if annotation is int:
        return WHOLE_NUMBERS

    pytest.fail(f"no strategy for a guard parameter of type {annotation!r}")


@cache
def _pools(guard: Function) -> dict[type, tuple[object, ...]]:
    """Return, for each of the guard's quantities, every edge that its type accepts.

    Each edge is built as the quantity's type. A place that takes the type
    again is handed these values.
    """

    pools: dict[type, tuple[object, ...]] = {}

    for name, annotation in _parameters(guard).items():
        admitted = []

        for edge in _edges(annotation):
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
    function: Function, values: Mapping[type, object], pools: Mapping[type, tuple[object, ...]]
) -> Iterator[dict[str, object]]:
    """Yield each way to hand `function` what was drawn.

    The drawn value goes where the function first takes the value's type.
    Where the function takes the type again, it gets every value of the
    type's pool in turn.
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


def _takes_only_self(function: Function) -> bool:
    return list(inspect.signature(function).parameters) == ["self"]


def _step(built: object) -> None:
    """Take a step on whatever was just built or set, and read what it reports.

    Stepping and reading the reports is where a value that was set, rather
    than computed, is used in a computation. A run is stepped by its own
    `advance()`, which takes no argument, because a run moves only by the
    one-second step. A compartment's own `advance` takes a step and its
    inputs, and it is not called here.
    """

    for owner, function in CALLABLES:
        if owner is type(built) and function.__name__ == "advance" and _takes_only_self(function):
            _require_finite(getattr(built, function.__name__)(), function)

    for name, member in vars(type(built)).items():
        if isinstance(member, property) and not name.startswith("_") and member.fget is not None:
            returned = typing.get_type_hints(member.fget).get("return")

            if (
                isinstance(returned, type)
                and issubclass(returned, (float, int))
                and returned is not bool
            ):
                value = getattr(built, name)

                if not (member in INFINITE_WHERE_NOTHING_FLOWS and value == math.inf):
                    _require_finite(value, member.fget)


@contextmanager
def _naming(called: str, values: Mapping[str, object]) -> Iterator[None]:
    try:
        yield
    except BaseException as failure:
        shown = ", ".join(
            f"{name}={describe_count(value) if isinstance(value, int) else repr(value)}"
            for name, value in values.items()
        )
        failure.add_note(f"{called}({shown})")
        raise


def _computes_with(
    owner: type | None,
    function: Function,
    values: Mapping[type, object],
    pools: Mapping[type, tuple[object, ...]],
) -> None:
    """Call one function behind a guard with what the guard accepted.

    The function must return a finite result or raise the simulator's own
    refusal, and a constructor must build.
    """

    for drawing in _drawings(function, values, pools):
        with _naming(function.__qualname__, drawing):
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

            if not (function in INFINITE_WHERE_NOTHING_FLOWS and result == math.inf):
                _require_finite(result, function)

            if built is not None:
                try:
                    _step(built)
                except AnesthesiaSimulationError:
                    continue


def _check(guard: Function, values: Mapping[str, object]) -> None:
    """Check the property for one draw.

    A refusal must be the simulator's own error, and every function behind
    the guard must compute with an accepted value.
    """

    with _naming(guard.__name__, values):
        try:
            guard(**values)
        except AnesthesiaSimulationError:
            return

        admitted = {CHECKED[name]: CHECKED[name](value) for name, value in values.items()}

        for owner, function in _behind(guard):
            _computes_with(owner, function, admitted, _pools(guard))


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
    edges = [_edges(annotation) for annotation in annotations.values()]

    for values in product(*edges):
        _check(guard, dict(zip(annotations, values, strict=True)))

    @settings(max_examples=50)
    @given(st.data())
    def drawn(data: st.DataObject) -> None:
        values = {
            name: data.draw(_drawn(annotation), label=name)
            for name, annotation in annotations.items()
        }

        _check(guard, values)

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
