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

**Found rather than listed.** The guards are every `require_supported_*`
function the two modules define, so a guard added to either is drawn without
editing this file. A function is behind a guard when it takes a quantity the
guard bounds: the run's step by its type, `SimulationStep`, wherever the package
annotates it (`PL-0GJC`), and any other quantity by its name and the type it is
checked as, on the run's own classes. That type is the guard's own parameter
type or, where the quantity is built only through the guard as the three flows
are since `PL-0YYV`, the `float` subclass whose constructor names it. Matching
a flow by its type anywhere, as the step is matched, would reach the
compartments' own setters, which `RECEIVERS` cannot build - a compartment
stepped alone reports an infinite time constant at zero flow - so it waits
for `PL-51B7`'s last slice to decide. What is kept by hand is how to build
those classes at their defaults, `RECEIVERS`, and a function taking the step
that this cannot call fails the test by name rather than going untested. A
function that
takes a quantity under another name - `RunDefinition`'s `opened_at_s` - is
reached only through the ones that use the guard's. A constructor counts where
it checks or computes - written by hand, or a dataclass's with a
`__post_init__` - and not where it only stores, as `app/controller.py`'s
`ResumePoint` does.

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
from itertools import product

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import anesthesia_sim
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import SIMULATION_TICK_INTERVAL_S
from anesthesia_sim.app.playback import PlaybackRate
from anesthesia_sim.core import simulation_step, supported_ranges
from anesthesia_sim.core.exceptions import AnesthesiaSimulationError
from anesthesia_sim.core.run_definition import RunDefinition
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.simulation_step import (
    MAXIMUM_SIMULATION_STEP_S,
    MINIMUM_SIMULATION_STEP_S,
    SimulationStep,
)
from anesthesia_sim.core.supported_ranges import describe_count
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

GUARD_MODULES = (supported_ranges, simulation_step)

Function = Callable[..., object]


def _run_definition() -> RunDefinition:
    system = AgentUptakeSystem.default()

    return RunDefinition(system.equation_settings(), system.state_vector(), opened_at_s=0.0)


# How to build, at its defaults, each class whose methods a guard's quantity is
# looked for on. The one list kept by hand, and checked: a function taking the
# run's step that nothing here can call fails the test by name.
RECEIVERS: Mapping[type, Callable[[], object]] = {
    AgentUptakeSystem: AgentUptakeSystem.default,
    PlaybackRate: lambda: PlaybackRate(multiplier=1),
    RunDefinition: _run_definition,
    SimulationController: SimulationController,
    SimulationState: SimulationState,
}

# A value for a parameter the guard being drawn does not bound, where a
# function behind it takes one without a default: the shipped tick, and the
# count of a run that has not stepped.
TYPICAL: Mapping[str, object] = {"tick_interval_s": SIMULATION_TICK_INTERVAL_S, "step_count": 0}


def _without_none(annotation: object) -> object:
    """`X | None` read as `X`, the optional step a run has before it steps."""

    members = [member for member in typing.get_args(annotation) if member is not type(None)]
    is_union = (
        isinstance(annotation, types.UnionType) or typing.get_origin(annotation) is typing.Union
    )

    return members[0] if is_union and len(members) == 1 else annotation


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
    which is how the three flows are found."""

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

# The types a guard itself takes, which the package annotates wherever it
# passes them: a function is behind such a guard wherever it takes the type.
# A flow's type is not among them, since its guard takes the `float` it
# checks, so a flow is found by name on the run's own classes: by type it
# would reach the compartments' own setters, which `RECEIVERS` cannot build
# (`PL-51B7`'s last slice decides that).
TAKEN = frozenset(
    annotation
    for guard in GUARDS
    for annotation in _parameters(guard).values()
    if isinstance(annotation, type) and annotation.__module__ != "builtins"
)


def _takes(owner: type | None, function: Function, name: str, checked: type) -> bool:
    parameters = _parameters(function)

    if checked in TAKEN:
        return checked in parameters.values()

    return parameters.get(name) is checked and (owner is None or owner in RECEIVERS)


def _behind(guard: Function) -> tuple[tuple[type | None, Function], ...]:
    return tuple(
        (owner, function)
        for owner, function in CALLABLES
        if function is not guard
        and any(_takes(owner, function, name, CHECKED[name]) for name in _parameters(guard))
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


def _count_edges(step: SimulationStep) -> tuple[int, ...]:
    return tuple(
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
                *(span + offset for span in _spans(step) for offset in (-1, 0, 1)),
            }
        )
    )


def _counts(step: SimulationStep) -> st.SearchStrategy[int]:
    return st.one_of(
        st.integers(),
        st.sampled_from(_count_edges(step)),
        *(st.integers(min_value=-1, max_value=2 * span + 1) for span in _spans(step)),
    )


def _edges(annotation: object, step: SimulationStep) -> tuple[object, ...]:
    if annotation is SimulationStep:
        return (step,)

    if annotation is int:
        return _count_edges(step)

    if annotation is float:
        return FLOAT_EDGES

    pytest.fail(f"no edges for a guard parameter of type {annotation!r}")


def _drawn(annotation: object, step: SimulationStep) -> st.SearchStrategy[object]:
    if annotation is SimulationStep:
        return st.just(step)

    if annotation is int:
        return _counts(step)

    if annotation is float:
        return FLOATS

    pytest.fail(f"no strategy for a guard parameter of type {annotation!r}")


def _require_finite(value: object, function: Function) -> None:
    if isinstance(value, float):
        assert math.isfinite(value), f"{function.__qualname__} computed {value}"
    elif isinstance(value, (tuple, list)):
        for item in value:
            _require_finite(item, function)
    elif dataclasses.is_dataclass(value) and not isinstance(value, type):
        for field in dataclasses.fields(value):
            _require_finite(getattr(value, field.name), function)


def _arguments(
    function: Function, values: Mapping[str, object], step: SimulationStep
) -> dict[str, object]:
    """What to call `function` with: the guarded values under their own names,
    the run's step wherever its type is taken, and otherwise a default, or the
    shipped value `TYPICAL` holds."""

    annotations = _parameters(function)
    arguments: dict[str, object] = {}

    for name, parameter in inspect.signature(function).parameters.items():
        if name == "self":
            continue

        if name in values:
            arguments[name] = values[name]
        elif annotations.get(name) is SimulationStep:
            arguments[name] = step
        elif parameter.default is not inspect.Parameter.empty:
            continue
        elif name in TYPICAL:
            arguments[name] = TYPICAL[name]
        else:
            pytest.fail(
                f"{function.__qualname__} takes {name}, which this guard does not draw and "
                f"TYPICAL holds no value for"
            )

    return arguments


def _step(built: object, step: SimulationStep) -> None:
    """Take a step on whatever was just built or set, and read what it reports,
    which is where a value set rather than computed is computed with."""

    for owner, function in CALLABLES:
        if owner is type(built) and function.__name__ != "__init__":
            if SimulationStep in _parameters(function).values():
                _require_finite(
                    getattr(built, function.__name__)(**_arguments(function, {}, step)), function
                )

    for name, member in vars(type(built)).items():
        if isinstance(member, property) and not name.startswith("_") and member.fget is not None:
            if typing.get_type_hints(member.fget).get("return") is float:
                _require_finite(getattr(built, name), member.fget)


def _computes_with(
    owner: type | None, function: Function, values: Mapping[str, object], step: SimulationStep
) -> None:
    arguments = _arguments(function, values, step)

    try:
        if owner is not None and function.__name__ == "__init__":
            built: object | None = owner(**arguments)
            result: object = None
        elif owner is not None:
            built = RECEIVERS[owner]()
            result = getattr(built, function.__name__)(**arguments)
        else:
            built = None
            result = function(**arguments)

        _require_finite(result, function)

        if built is not None:
            _step(built, step)
    except AnesthesiaSimulationError:
        pass


@contextmanager
def _naming(guard: Function, values: Mapping[str, object], step: SimulationStep) -> Iterator[None]:
    try:
        yield
    except BaseException as failure:
        shown = ", ".join(
            f"{name}={describe_count(value) if type(value) is int else repr(value)}"
            for name, value in values.items()
        )
        failure.add_note(f"{guard.__name__}({shown}), stepping at {step!r} s")
        raise


def _check(guard: Function, values: Mapping[str, object], step: SimulationStep) -> None:
    """The property, for one draw: a refusal is the simulator's own error, and
    an admitted value is one every function behind the guard computes with."""

    with _naming(guard, values, step):
        try:
            guard(**values)
        except AnesthesiaSimulationError:
            return

        admitted = {name: CHECKED[name](value) for name, value in values.items()}
        step = next(
            (value for value in admitted.values() if isinstance(value, SimulationStep)), step
        )

        for owner, function in _behind(guard):
            _computes_with(owner, function, admitted, step)


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
