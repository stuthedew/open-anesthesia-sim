"""The dashboard, driven headless against real runs.

These tests cover that every slot touching a run passes the halt, and that every run-state surface
is restated on it.

`simulation_view_support.py` describes the whole suite.
"""

import ast
import inspect
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from functools import cache, partial
from pathlib import Path
from typing import Any, Final, NoReturn

import pytest
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut
from PySide6.QtWidgets import (
    QAbstractButton,
    QAbstractItemView,
    QAbstractSlider,
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QLabel,
    QLineEdit,
    QScrollArea,
    QScrollBar,
    QWidget,
)

from anesthesia_sim.app import run_view as run_view_module
from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.bookmarks import MacTarget, TimeBookmark
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import FORK_NOTHING_SELECTED_TEXT, STATUS_FAILED_TEXT
from anesthesia_sim.app.halt_gate import halt_gate, passes_halt_gate
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.concentration import MacMultiple
from anesthesia_sim.core.supported_ranges import CaseInstant
from tests.integration.simulation_view.simulation_view_support import (
    _branched_case,
    _case_view,
    _failing_assembly,
    _fork_panel,
    _marks_panel,
    _opened_bookmark_dialog,
    _paused_run_with_history,
    _select_agent,
    _settle,
    _shown_view,
    _steps,
    _take_fork,
    _widget_attributes,
    _widget_state,
    _with_stale_tissue_flows,
)

#: The containers whose controls a halt leaves unchanged, each with the reason. The test
#: below requires every other control on the dashboard, including one added later, to sit
#: in one of two places. One is a `RunView`, which restates its own widgets (`PL-X7D5`).
#: The other is a panel that `SimulationView.halt_restatements` lists. A control in
#: neither keeps offering its action over a run that every other control says has failed,
#: as the branch panel did (`PL-MMNX`) and the bookmark panel did (`PL-YHR3`). The keys
#: are class names, because the dashboard builds each kind of container once per Area or
#: once per dashboard.
#:
#: The test also checks the other direction. An entry that matches no control on the
#: built dashboard fails the test, because nothing then needs the exemption.
NOT_RESTATED_ON_A_HALT: dict[str, str] = {
    "WorkspaceTabs": (
        "the Workspace tabs choose and rename layouts. A layout is the reader's "
        "arrangement of Areas, so it acts on no run."
    ),
    "ViewChooser": ("an Area's View chooser picks what the Area shows, which acts on no run."),
    "TimeBaseSelector": (
        "a chart's time base is the chart's own drawing setting. It touches no "
        "simulation state, and it is never disabled (`PL-012`)."
    ),
    "TraceLegend": (
        "the legend's boxes ask the dashboard which compartments to draw. The "
        "selection is the dashboard's display state and acts on no run (`PL-VN6M`)."
    ),
}

#: The widget types a reader acts through. A scroll bar is left out: it moves
#: the widget that holds it, and that widget's own container is what is checked.
_CONTROL_TYPES = (
    QAbstractButton,
    QComboBox,
    QAbstractSlider,
    QAbstractSpinBox,
    QLineEdit,
    QAbstractItemView,
)


def _controls(root: QWidget) -> list[QWidget]:
    """Every control under `root` that a reader can act through, except a combo box's popup."""

    found: list[QWidget] = []

    for widget in root.findChildren(QWidget):
        if not isinstance(widget, _CONTROL_TYPES) or isinstance(widget, QScrollBar):
            continue

        ancestor = widget.parentWidget()

        while ancestor is not None and not isinstance(ancestor, QComboBox):
            ancestor = ancestor.parentWidget()

        if ancestor is None:
            found.append(widget)

    return found


def _ancestry(widget: QWidget) -> list[QWidget]:
    """The widget and every widget above it, nearest first."""

    chain: list[QWidget] = []
    current: QWidget | None = widget

    while current is not None:
        chain.append(current)
        current = current.parentWidget()

    return chain


#: Each entry is a callback that a view connects to a signal or passes to another call without
#: the halt gate. Its key is the view class's name and the callback's source text, and its value
#: is the reason the callback does not need the gate. Qt or a view calls every callback not
#: listed here from the event loop, so an exception raised inside it is lost unless it passes
#: the gate (`PL-HJKN`). The test fails on an entry if its callback is no longer connected or
#: passed on, or if the callback now passes the gate, so the list stays accurate.
_HANDED_OUT_WITHOUT_THE_HALT_GATE: Final[dict[tuple[str, str], str]] = {
    ("RunView", "dialog.deleteLater"): (
        "it is Qt's own slot, which deletes the dialog once it closes, and it reads no run"
    ),
    ("SimulationView", "self._trunk_reset_question"): (
        "it returns the question that the trunk's Reset asks, and the trunk's own gated "
        "Reset slot calls it"
    ),
    ("SimulationView", "self._a_question_is_open"): (
        "it returns whether a question is open, and each run's own gated step_tick calls it"
    ),
    ("SimulationView", "self._branch_control_shown"): (
        "it returns whether an Area shows a branch control, for the banner of a stopped run, "
        "and it reads widget visibility and no run"
    ),
    ("SimulationView", "self._open_runs"): (
        "it returns the open runs' identities to the tab strip, and it reads no snapshot"
    ),
    ("SimulationView", "self._restate_fork_panel"): (
        "it runs inside the halt path, which a gate would enter again, and HaltRestatement "
        "requires that it not raise"
    ),
    ("SimulationView", "self._restate_bookmark_panel"): (
        "it runs inside the halt path, which a gate would enter again, and HaltRestatement "
        "requires that it not raise"
    ),
    ("SimulationView", "lambda: self.workspaces"): (
        "it returns the Workspaces as the Areas draw them, for the tab strip to duplicate "
        "or save, and it reads no run"
    ),
}


def _own_method(node: ast.expr, view_class: type) -> str | None:
    """Return `<name>` when `node` is `self.<name>` for a method of `view_class`, else None.

    A property does not count as a method, because `self.<name>` then gives the property's
    value, not a method.
    """

    if not (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
    ):
        return None

    member = inspect.getattr_static(view_class, node.attr, None)

    if member is None or isinstance(member, property) or not callable(member):
        return None

    return node.attr


#: This set names the calls that take a slot as a positional argument after the first one,
#: as `QTimer.singleShot(msec, slot)`, `QShortcut(key, parent, slot)` and
#: `QMenu.addAction(text, slot)` do. The check treats those arguments as it treats a slot
#: passed to `.connect` (coverage review of `PL-HJKN`).
_CALLS_THAT_TAKE_A_SLOT: Final = frozenset({"singleShot", "callLater", "addAction", "QShortcut"})


@cache
def _qt_signal_names() -> frozenset[str]:
    """Return the name of every signal that a class in QtCore, QtGui or QtWidgets declares.

    PySide6 lets a constructor connect a signal. A keyword argument named after the signal
    connects that signal to the argument's value, as in `QPushButton("Pause", clicked=slot)`.
    So a keyword argument with a signal's name passes a slot.
    """

    return frozenset(
        name
        for module in (QtCore, QtGui, QtWidgets)
        for _, member in inspect.getmembers(module, inspect.isclass)
        for name, value in vars(member).items()
        if isinstance(value, QtCore.Signal)
    )


def _elements(node: ast.expr) -> Iterator[ast.expr]:
    """Yield `node`, or each element of it when it is a tuple, list, set, dict or starred value."""

    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        for element in node.elts:
            yield from _elements(element)
    elif isinstance(node, ast.Dict):
        for value in node.values:
            yield from _elements(value)
    elif isinstance(node, ast.Starred):
        yield from _elements(node.value)
    else:
        yield node


def _callback_bypass(
    callback: ast.expr,
    view_class: type,
    local_functions: set[str],
    *,
    position: str,
    run_at_once: bool,
) -> str | None:
    """Return why `callback` bypasses the halt gate, or None if it does not.

    `position` says how the call takes `callback`. It is "connect" for the argument of
    `.connect`. It is "slot" for a positional argument after the first of a call named in
    `_CALLS_THAT_TAKE_A_SLOT`, and for the value of a keyword argument named after a signal.
    It is "argument" for any other argument. `run_at_once` is True when the call is to one
    of the view's own methods. Such a method runs the callback at once, inside the slot
    that makes the call.

    A method of the view passes the gate when it is gated, in any position. A lambda or a
    local function bypasses the gate in every position, unless one of the view's own methods
    runs it at once. In the "connect" and "slot" positions, every other callback bypasses
    the gate too. That includes a slot of another object, such as `run.controller.pause`,
    and a slot reached through an attribute of the view, such as `self.controller.pause`.
    In the "slot" position, though, a name, a constant, a call or one of the view's own
    attributes is a value and not a callback. An example is the parent widget that
    `QShortcut` takes. In the "argument" position, anything else is a value too. This
    function returns None for a value.
    """

    method = _own_method(callback, view_class)

    if method is not None:
        gated = passes_halt_gate(inspect.getattr_static(view_class, method))

        return None if gated else f"{method} does not pass the gate"

    local = isinstance(callback, ast.Lambda) or (
        isinstance(callback, ast.Name) and callback.id in local_functions
    )

    if position == "argument":
        if local and not run_at_once:
            return "a lambda or a local function that the callee may call from the event loop"

        return None

    if local:
        return "a lambda or a local function, which cannot pass the gate"

    if position == "connect" and isinstance(callback, ast.Name):
        return "a function named bare, which cannot pass the gate"

    held_by_the_view = (
        isinstance(callback, ast.Attribute)
        and isinstance(callback.value, ast.Name)
        and callback.value.id == "self"
    )

    if position == "slot" and (
        held_by_the_view or isinstance(callback, (ast.Name, ast.Constant, ast.Call))
    ):
        return None

    names_self = any(
        isinstance(node, ast.Name) and node.id == "self" for node in ast.walk(callback)
    )

    if names_self:
        return "a slot reached through the view that is not its own method"

    return "a slot of another object, which may read or change a run outside the gate"


def _unwrapped_partial(node: ast.expr) -> ast.expr:
    """Return the function that `node` wraps when it is a `partial` call, or `node` itself.

    Both `partial(...)` and `functools.partial(...)` count.
    """

    if (
        isinstance(node, ast.Call)
        and (
            (isinstance(node.func, ast.Name) and node.func.id == "partial")
            or (isinstance(node.func, ast.Attribute) and node.func.attr == "partial")
        )
        and node.args
    ):
        return node.args[0]

    return node


def _assigned_names(function: ast.AST) -> dict[str, list[ast.expr | None]]:
    """Return each name that `function` binds, with every value a plain assignment gives it.

    A plain assignment, such as `callback = self._apply` or `callback: Slot = self._apply`,
    gives the name its value. Any other binding of the name adds None, which says the name
    may also hold something that no assignment shows. A parameter, a loop target, a `with`
    or `except` target, an unpacking, `:=`, `+=` and an import are such bindings.
    """

    assigned: dict[str, list[ast.expr | None]] = {}
    plain_targets: set[int] = set()

    for node in ast.walk(function):
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        else:
            continue

        for target in targets:
            if isinstance(target, ast.Name):
                plain_targets.add(id(target))
                assigned.setdefault(target.id, []).append(value)

    otherwise: set[str] = set()

    for node in ast.walk(function):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if id(node) not in plain_targets:
                otherwise.add(node.id)
        elif isinstance(node, ast.arg):
            otherwise.add(node.arg)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            otherwise.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            otherwise.update((alias.asname or alias.name).split(".")[0] for alias in node.names)

    for name in otherwise:
        assigned.setdefault(name, []).append(None)

    return assigned


def _followed(node: ast.expr, assigned: Mapping[str, list[ast.expr | None]]) -> list[ast.expr]:
    """Return the callbacks that `node` stands for, following a local variable to its values.

    A name that the enclosing function assigns stands for each value assigned to it, so
    `callback = self._apply; button.clicked.connect(callback)` is judged as a connection of
    `self._apply`. A name that is also bound some other way, such as a parameter or a loop
    target, stands for itself as well. A `partial` stands for the function that it wraps.
    A conditional expression stands for both of its values, and a tuple, list or set
    assigned to a name stands for each of its elements. Any other node stands for itself.
    """

    pending, seen, found = [node], set[str](), list[ast.expr]()

    while pending:
        current = _unwrapped_partial(pending.pop())

        if isinstance(current, ast.Name) and current.id in assigned:
            if current.id not in seen:
                seen.add(current.id)

                for value in reversed(assigned[current.id]):
                    if value is None:
                        found.append(current)
                    else:
                        pending.extend(reversed(list(_elements(value))))
        elif isinstance(current, ast.IfExp):
            pending.extend((current.orelse, current.body))
        else:
            found.append(current)

    return found


def _passed_callbacks(
    call: ast.Call, assigned: Mapping[str, list[ast.expr | None]]
) -> list[tuple[ast.expr, str]] | None:
    """Return each callback that `call` passes on, with its position, or None for a disconnect.

    The positions are those that `_callback_bypass` describes. Each callback is followed
    through `_followed`, so a variable stands for the value assigned to it.
    """

    if isinstance(call.func, ast.Attribute):
        called: str | None = call.func.attr
    else:
        called = call.func.id if isinstance(call.func, ast.Name) else None

    if called == "disconnect":
        return None

    if called == "connect":
        (slot,) = call.args
        return [(callback, "connect") for callback in _followed(slot, assigned)]

    slots = call.args[1:] if called in _CALLS_THAT_TAKE_A_SLOT else []
    passed = [(argument, any(argument is slot for slot in slots)) for argument in call.args]
    passed += [(keyword.value, keyword.arg in _qt_signal_names()) for keyword in call.keywords]
    positioned: list[tuple[ast.expr, str]] = []

    for value, takes_a_slot in passed:
        if takes_a_slot:
            positioned.extend((callback, "slot") for callback in _followed(value, assigned))
        else:
            positioned.extend(
                (callback, "argument")
                for element in _elements(value)
                for callback in _followed(element, assigned)
            )

    return positioned


def _calls_with_their_assignments(
    body: list[ast.stmt],
) -> Iterator[tuple[ast.Call, dict[str, list[ast.expr | None]]]]:
    """Yield each call in `body` with the names its top-level function assigns.

    `body` is a class's or a module's statements, and each class in it is read the same
    way. A call in a function nested inside a method sees the names the whole method
    assigns. A call outside any function sees none.
    """

    for statement in body:
        if isinstance(statement, ast.ClassDef):
            yield from _calls_with_their_assignments(statement.body)
            continue

        assigned = (
            _assigned_names(statement)
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef))
            else {}
        )

        for node in ast.walk(statement):
            if isinstance(node, ast.Call):
                yield node, assigned


@dataclass(frozen=True)
class _HaltGateReading:
    """What `_halt_gate_bypasses` found in one view's source."""

    #: Each call that passes on a callback bypassing the gate, or each method that overrides
    #: Qt's own without the gate, as its source text and why.
    bypasses: list[tuple[str, str]]
    #: Each key of the exemptions whose callback passes the gate, so the entry is stale.
    exempt_but_gated: list[tuple[str, str]]
    #: Each key of the exemptions whose callback the source passes on.
    exemptions_handed_out: set[tuple[str, str]]
    #: How many `.connect` calls the source makes.
    connections: int


def _halt_gate_bypasses(
    view_class: type, exemptions: Mapping[tuple[str, str], str]
) -> _HaltGateReading:
    """Find each call in `view_class`'s source whose callback bypasses the halt gate.

    The halt gate is `halt_gate` in `app/halt_gate.py`. The class's source holds every
    connection the class makes, including the ones it makes when it later builds a dialog.
    Each callback is followed through `_followed`, so a `partial` is treated as the method
    that it wraps, and a local variable as the values assigned to it. A method that
    overrides one of Qt's own, such as `keyPressEvent`, is called by Qt directly, so it must
    pass the gate too. Each key in `exemptions` pairs the class's name with the callback's
    source text, or with `def <name>` for such a method. A callback listed there is not
    reported as a bypass, but its entry is reported as stale when the callback passes the gate.

    `_outside_bypasses` reads the rest of `app/` for view methods that other code connects.
    """

    (class_node,) = ast.parse(inspect.getsource(view_class)).body
    assert isinstance(class_node, ast.ClassDef), f"{view_class.__name__}'s source is not a class"
    methods = [node for node in class_node.body if isinstance(node, ast.FunctionDef)]
    local_functions = {
        node.name
        for method in methods
        for node in ast.walk(method)
        if isinstance(node, ast.FunctionDef) and node is not method
    }
    qt_bases = [base for base in view_class.__mro__ if base.__module__.startswith("PySide6")]
    judged: list[tuple[str, str, str | None]] = []

    for method in methods:
        if not method.name.startswith("__") and any(
            hasattr(base, method.name) for base in qt_bases
        ):
            gated = passes_halt_gate(inspect.getattr_static(view_class, method.name))
            reason = None if gated else "it overrides a Qt method, which Qt calls directly"
            judged.append((f"def {method.name}", f"def {method.name}", reason))

    connections = 0

    for call, assigned in _calls_with_their_assignments(class_node.body):
        positioned = _passed_callbacks(call, assigned)

        if positioned is None:
            continue

        if isinstance(call.func, ast.Attribute) and call.func.attr == "connect":
            connections += 1

        run_at_once = _own_method(call.func, view_class) is not None

        for callback, position in positioned:
            reason = _callback_bypass(
                callback, view_class, local_functions, position=position, run_at_once=run_at_once
            )
            judged.append((ast.unparse(call), ast.unparse(callback), reason))

    bypasses: list[tuple[str, str]] = []
    exempt_but_gated: list[tuple[str, str]] = []
    exemptions_handed_out: set[tuple[str, str]] = set()

    for text, callback_text, reason in judged:
        key = (view_class.__name__, callback_text)

        if key in exemptions:
            exemptions_handed_out.add(key)

            if reason is None:
                exempt_but_gated.append(key)
        elif reason is not None:
            bypasses.append((text, reason))

    return _HaltGateReading(bypasses, exempt_but_gated, exemptions_handed_out, connections)


def _view_methods(views: Sequence[type]) -> dict[str, list[tuple[type, bool]]]:
    """Map each method name that the views define in this project to the views that define it.

    Each entry pairs a view with whether its method of that name passes the halt gate.
    A method that a view takes from PySide6, such as `update` or `close`, is left out,
    because its name says nothing about which object a call reaches. So is a property.
    """

    methods: dict[str, list[tuple[type, bool]]] = {}

    for view in views:
        names = {
            name
            for base in view.__mro__
            if base.__module__.startswith("anesthesia_sim") or base.__module__ == __name__
            for name in vars(base)
            if not name.startswith("__")
        }

        for name in sorted(names):
            member = inspect.getattr_static(view, name)

            if isinstance(member, property) or not callable(member):
                continue

            methods.setdefault(name, []).append((view, passes_halt_gate(member)))

    return methods


def _outside_bypasses(
    modules: Mapping[str, ast.Module],
    views: Sequence[type],
    exemptions: Mapping[tuple[str, str], str],
) -> _HaltGateReading:
    """Find each call outside the views' classes that passes on a view method without the gate.

    `modules` maps each module's dotted name to its parsed source. Calls inside the views'
    own classes are left to `_halt_gate_bypasses`. A callback is matched to a view's method
    by its attribute name alone, as `view._apply` or `self.view._apply` is matched to
    `RunView._apply`, because the source does not say which object the name before the dot
    holds. A callback named `self.<name>` is the enclosing
    class's own method and is not matched, so a callback that another class stores as
    `self._callback = view._apply` and connects later is not seen. A lambda that calls a
    view's method from outside is not checked either. Each key in `exemptions` pairs the
    module's dotted name with the callback's source text.
    """

    methods = _view_methods(views)
    own_classes = {(view.__module__, view.__name__) for view in views}
    judged: list[tuple[str, str, str, str | None]] = []
    connections = 0

    for module_name, tree in modules.items():
        body = [
            statement
            for statement in tree.body
            if not (
                isinstance(statement, ast.ClassDef) and (module_name, statement.name) in own_classes
            )
        ]

        for call, assigned in _calls_with_their_assignments(body):
            positioned = _passed_callbacks(call, assigned)

            if positioned is None:
                continue

            if isinstance(call.func, ast.Attribute) and call.func.attr == "connect":
                connections += 1

            for callback, _ in positioned:
                if not isinstance(callback, ast.Attribute) or callback.attr not in methods:
                    continue

                if isinstance(callback.value, ast.Name) and callback.value.id == "self":
                    continue

                ungated = [
                    f"{view.__name__}.{callback.attr}"
                    for view, gated in methods[callback.attr]
                    if not gated
                ]
                reason = (
                    f"it is named like {', '.join(ungated)}, which does not pass the gate"
                    if ungated
                    else None
                )
                judged.append((module_name, ast.unparse(call), ast.unparse(callback), reason))

    bypasses: list[tuple[str, str]] = []
    exempt_but_gated: list[tuple[str, str]] = []
    exemptions_handed_out: set[tuple[str, str]] = set()

    for module_name, text, callback_text, reason in judged:
        key = (module_name, callback_text)

        if key in exemptions:
            exemptions_handed_out.add(key)

            if reason is None:
                exempt_but_gated.append(key)
        elif reason is not None:
            bypasses.append((f"{module_name}: {text}", reason))

    return _HaltGateReading(bypasses, exempt_but_gated, exemptions_handed_out, connections)


def _app_modules() -> dict[str, ast.Module]:
    """Return every module under `src/anesthesia_sim/app/`, parsed, by its dotted name."""

    package = Path(inspect.getfile(run_view_module)).parent

    return {
        ".".join(("anesthesia_sim", "app", *path.relative_to(package).with_suffix("").parts)): (
            ast.parse(path.read_text(encoding="utf-8"))
        )
        for path in sorted(package.rglob("*.py"))
    }


def test_every_slot_that_touches_a_run_passes_the_halt_gate() -> None:
    """Every slot that `RunView` and `SimulationView` connect or hand out passes the halt gate.

    A slot that reads or changes a run can raise, for example on a run whose snapshot rejects
    a value. Without the gate, PySide6 prints an exception raised inside a slot and carries
    on, so the run still shows "Paused" and no halt appears on screen. Hand-written `try`
    blocks missed six slots, so every slot now passes through `app/halt_gate.py`'s
    `halt_gate`, and this test makes each new slot pass through it too (`PL-HJKN`).

    The test parses each class's source, and `_callback_bypass` decides which callbacks
    bypass the gate. It also parses every other module under `app/` for a view method that
    other code connects without the gate (`PL-WV74`). The test fails on any such callback
    unless it is listed in `_HANDED_OUT_WITHOUT_THE_HALT_GATE` with the reason it does not
    need the gate. `test_the_halt_gate_check_finds_each_way_around_the_gate` and
    `test_the_halt_gate_check_finds_a_slot_connected_from_outside_the_view` show that the
    check catches each kind of bypass.
    """

    bypasses: list[str] = []
    exempt_but_gated: list[tuple[str, str]] = []
    exemptions_handed_out: set[tuple[str, str]] = set()

    for view_class in (RunView, SimulationView):
        reading = _halt_gate_bypasses(view_class, _HANDED_OUT_WITHOUT_THE_HALT_GATE)
        bypasses.extend(f"{view_class.__name__}: {call}: {why}" for call, why in reading.bypasses)
        exempt_but_gated.extend(reading.exempt_but_gated)
        exemptions_handed_out |= reading.exemptions_handed_out

        assert reading.connections > 0, f"no connection found in {view_class.__name__}'s source"

    outside = _outside_bypasses(
        _app_modules(), (RunView, SimulationView), _HANDED_OUT_WITHOUT_THE_HALT_GATE
    )
    bypasses.extend(f"{call}: {why}" for call, why in outside.bypasses)
    exempt_but_gated.extend(outside.exempt_but_gated)
    exemptions_handed_out |= outside.exemptions_handed_out

    assert outside.connections > 0, "no connection found outside the views' own source"

    stale = set(_HANDED_OUT_WITHOUT_THE_HALT_GATE) - exemptions_handed_out

    assert not bypasses, "slots that bypass the halt gate:\n" + "\n".join(bypasses)
    assert not exempt_but_gated, f"exempt callbacks that pass the gate: {exempt_but_gated}"
    assert not stale, f"exempt callbacks that are no longer handed out: {sorted(stale)}"


class _ViewWiredAroundTheGate(QWidget):
    """A view that passes on callbacks in every shape the halt gate check must judge.

    It is never built, and `_wire` is never called. The check reads its source.
    """

    controller: Any

    def halt_for_slot(self, error: Exception) -> None:
        raise AssertionError("the view is never built")

    @halt_gate
    def _gated(self) -> None:
        pass

    @halt_gate
    def _gated_with_one(self, value: int) -> None:
        pass

    def _ungated(self) -> None:
        pass

    def _run_now(self, action: Callable[[], None]) -> None:
        action()

    def _register(self, actions: tuple[Callable[[], None], ...]) -> None:
        pass

    @halt_gate
    def showEvent(self, event: Any) -> None:
        pass

    def keyPressEvent(self, event: Any) -> None:
        self.controller.pause()

    def _wire(self, button: Any, run: Any, timer: Any, menu: Any, key: Any) -> None:
        def local() -> None:
            self._gated()

        button.clicked.connect(self._gated)
        button.clicked.connect(partial(self._gated_with_one, 1))
        button.clicked.connect(_bare_function)
        button.clicked.connect(run.controller.pause)
        button.clicked.connect(self._ungated)
        button.clicked.connect(lambda: self._gated())
        button.clicked.connect(local)
        button.clicked.connect(self.controller.pause)
        self._run_now(lambda: self._ungated())
        self._run_now(local)
        timer.singleShot(0, self._gated)
        timer.singleShot(0, self._ungated)
        timer.singleShot(0, lambda: self._gated())
        timer.singleShot(0, local)
        QShortcut(key, self, self._gated)
        QShortcut(key, self, self.controller.pause)
        menu.addAction("Pause", run.controller.pause)
        timer.singleShot(0, run.controller.pause)
        type(button)("Pause", clicked=self._gated)
        type(button)("Pause", clicked=run.controller.pause)
        self._run_now(*(self._ungated,))
        self._register((self._gated, self._ungated))
        held_gated = self._gated
        button.clicked.connect(held_gated)
        held_ungated = self._ungated
        timer.singleShot(0, held_ungated)
        for looped in (self._ungated,):
            button.clicked.connect(looped)
        chosen = self._gated if key else self._ungated
        timer.singleShot(0, chosen)
        self._stored = partial(self._ungated, 1)


def _bare_function() -> None:
    """A module-level function that `_ViewWiredAroundTheGate` connects by its bare name."""


def _wire_from_outside(view: _ViewWiredAroundTheGate, button: Any, timer: Any) -> None:
    """Connect `view`'s methods from outside its class, in each shape the check must judge.

    It is never called. `test_the_halt_gate_check_finds_a_slot_connected_from_outside_the_view`
    reads its source.
    """

    button.clicked.connect(view._gated)
    button.clicked.connect(view._ungated)
    held_gated = view._gated
    button.clicked.connect(held_gated)
    held_ungated = view._ungated
    timer.singleShot(0, held_ungated)
    timer.singleShot(0, partial(view._ungated))
    chosen = view._gated if timer else view._ungated
    button.clicked.connect(chosen)
    slots = [view._gated, view._ungated]
    timer.register(slots)


def test_the_halt_gate_check_finds_each_way_around_the_gate() -> None:
    """The check reports each callback in `_ViewWiredAroundTheGate` that bypasses the gate.

    The expected list below was written by hand from that class's source. Four kinds of
    callback pass the gate. They are a gated method in any position, a `partial` of a gated
    method, a gated override of a Qt method, and a lambda or a local function that one of
    the view's own methods runs at once. An exempt callback is not reported while it
    bypasses the gate. Once the gate covers it, its entry is reported as stale (blind
    review of `PL-HJKN`).
    """

    reading = _halt_gate_bypasses(_ViewWiredAroundTheGate, {})

    assert [call for call, _ in reading.bypasses] == [
        "def keyPressEvent",
        "button.clicked.connect(_bare_function)",
        "button.clicked.connect(run.controller.pause)",
        "button.clicked.connect(self._ungated)",
        "button.clicked.connect(lambda: self._gated())",
        "button.clicked.connect(local)",
        "button.clicked.connect(self.controller.pause)",
        "timer.singleShot(0, self._ungated)",
        "timer.singleShot(0, lambda: self._gated())",
        "timer.singleShot(0, local)",
        "QShortcut(key, self, self.controller.pause)",
        "menu.addAction('Pause', run.controller.pause)",
        "timer.singleShot(0, run.controller.pause)",
        "type(button)('Pause', clicked=run.controller.pause)",
        "self._run_now(*(self._ungated,))",
        "self._register((self._gated, self._ungated))",
        "timer.singleShot(0, held_ungated)",
        "timer.singleShot(0, chosen)",
        "partial(self._ungated, 1)",
        "button.clicked.connect(looped)",
    ]
    assert reading.exempt_but_gated == []
    assert reading.exemptions_handed_out == set()
    assert reading.connections == 10

    exempt = ("_ViewWiredAroundTheGate", "run.controller.pause")
    gated = ("_ViewWiredAroundTheGate", "self._gated")
    override = ("_ViewWiredAroundTheGate", "def keyPressEvent")
    reading = _halt_gate_bypasses(
        _ViewWiredAroundTheGate, {exempt: "a test", gated: "a test", override: "a test"}
    )
    reported = [call for call, _ in reading.bypasses]

    assert "button.clicked.connect(run.controller.pause)" not in reported
    assert "def keyPressEvent" not in reported
    assert reading.exempt_but_gated == [gated] * 7
    assert reading.exemptions_handed_out == {exempt, gated, override}


def test_the_halt_gate_check_finds_a_slot_connected_from_outside_the_view() -> None:
    """The check reports each view method without the gate that `_wire_from_outside` connects.

    The expected list was written by hand from that function's source. A method that passes
    the gate is not reported, whether it is named at once or held in a variable first. A
    method without the gate is reported in each shape: named at once, held in a variable,
    wrapped in a `partial`, chosen by a conditional expression, and held in a list. A
    `partial` is reported twice, once by the call that passes it on and once by its own
    call, which also catches a `partial` that is stored and passed later.
    """

    modules = {"synthetic": ast.parse(inspect.getsource(_wire_from_outside))}
    reading = _outside_bypasses(modules, (_ViewWiredAroundTheGate,), {})

    assert [call for call, _ in reading.bypasses] == [
        "synthetic: button.clicked.connect(view._ungated)",
        "synthetic: timer.singleShot(0, held_ungated)",
        "synthetic: timer.singleShot(0, partial(view._ungated))",
        "synthetic: button.clicked.connect(chosen)",
        "synthetic: timer.register(slots)",
        "synthetic: partial(view._ungated)",
    ]
    assert reading.connections == 4

    exempt = ("synthetic", "view._ungated")
    gated = ("synthetic", "view._gated")
    reading = _outside_bypasses(
        modules, (_ViewWiredAroundTheGate,), {exempt: "a test", gated: "a test"}
    )

    assert reading.bypasses == []
    assert reading.exempt_but_gated == [gated] * 4
    assert reading.exemptions_handed_out == {exempt, gated}


def test_a_raise_in_a_slot_that_no_try_guarded_halts_its_run(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An exception in the Pause slot, which no hand-written `try` guarded, now halts the run.

    Before the halt gate (`PL-HJKN`), PySide6 printed the exception and carried on. The run
    kept showing that it was running, and nothing on screen said that it had failed. The
    halt gate now halts the run.
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    run._start_button.click()
    assert run._pause_button.isEnabled() is True, "the started run offers no Pause to press"

    def refuse() -> None:
        raise RuntimeError("the pause could not be recorded")

    monkeypatch.setattr(controller, "pause", refuse)
    run._pause_button.click()

    assert controller.has_failed is True
    assert controller.snapshot().failure_reason == ("RuntimeError: the pause could not be recorded")
    assert run._status_text.text() == STATUS_FAILED_TEXT


def test_a_dashboard_slot_that_raises_withdraws_branching_and_names_the_dashboard(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An exception in a dashboard slot halts every run, and the refusal names the dashboard.

    Through the halt gate, every slot of `SimulationView` that raises now halts every run,
    as a frame that fails does. One such slot is Edit on the marks panel, which raises when
    the editor cannot be built. The branch panel's refusal used to say "the frame this run
    is drawn in failed", although no frame had failed (blind review of `PL-HJKN`).
    """

    case = _branched_case()
    view = _case_view(application, case)

    def refuse(*args: object, **kwargs: object) -> NoReturn:
        raise RuntimeError("the marks editor could not be built")

    monkeypatch.setattr(simulation_view_module, "BookmarkDialog", refuse)
    _marks_panel(view).edit_button.click()

    assert [run.controller.has_failed for run in view.runs] == [True] * len(view.runs)
    assert case.trunk.fork_refusal == (
        "the dashboard this run is drawn in failed (RuntimeError: the marks editor could not "
        "be built), and a branch would be drawn by the same dashboard and could fail the same "
        "way; reset the run first"
    )


def test_a_halt_whose_dials_cannot_be_written_still_withdraws_branch_here(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A halt asks for a frame even if the dials cannot be written, so "Branch here" is withdrawn.

    `show_presentation` raises once it has shown the halt, when a fresh gas flow range is narrower
    than the dial's step (`PL-M3M2`). `_halt_run` used to ask for no frame then, and the
    dashboard rewrites its branch panel only when it draws. So "Branch here" kept offering
    the halted trunk. Every slot of a run reaches this path through the halt gate, including
    `start_adjustment`, which no `try` guarded before (blind review of `PL-HJKN`).
    """

    case = _branched_case()
    view = _case_view(application, case)
    trunk = view.runs[0]
    here = _fork_panel(view).here_button
    assert here.isHidden() is False, "the paused trunk offers no Branch here to withdraw"
    monkeypatch.setattr(
        BreathingCircuit,
        "accepted_fresh_gas_flow_range_l_min",
        property(lambda circuit: (0.21, 0.29)),
    )

    def refuse() -> None:
        raise RuntimeError("the adjustment could not be recorded")

    monkeypatch.setattr(case.trunk, "begin_control_adjustment", refuse)

    with pytest.raises(ValueError, match="can offer no setting"):
        trunk.start_adjustment()

    assert case.trunk.has_failed is True
    assert here.isHidden() is True


def test_a_new_case_question_that_cannot_be_built_leaves_the_selector_working_after_reset(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failure to build the new-case question halts the run, and Reset frees the selector.

    `_confirm_new_case` used to record the pending agent before it built the question. When
    building the question raised an exception, the gate halted the run, but the pending agent
    was not cleared. So the selector put back every later pick, even after the Reset that the
    halt names as the way out (blind review of `PL-HJKN`).
    """

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]
    running = controller.agent_id
    other = next(agent for agent in ("desflurane", "isoflurane", "sevoflurane") if agent != running)

    def refuse(*args: object, **kwargs: object) -> NoReturn:
        raise RuntimeError("the question could not be built")

    monkeypatch.setattr(run_view_module, "new_case_question", refuse)
    _select_agent(run, other)

    assert controller.has_failed is True
    assert run._agent_dropdown.currentData() == running

    monkeypatch.undo()
    run._reset_button.click()
    _select_agent(run, other)

    assert controller.agent_id == other


def test_a_refused_reset_whose_halt_cannot_write_its_dials_halts_the_run_once(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A refused Reset halts its run once, for the refusal, even when showing the halt raises.

    `_reset_now` used to halt the run itself, inside the gated Reset slot. Showing that halt
    raised for a fresh gas flow range narrower than the dial's step (`PL-M3M2`). The gate
    then caught the dial's exception and halted the run a second time, for that exception
    (blind review of `PL-HJKN`).
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    run._start_button.click()
    _steps(run, 5)
    _with_stale_tissue_flows(controller, 6.0)
    halted_for: list[str] = []
    halt_for_slot = RunView.halt_for_slot

    def recording(self: RunView, error: Exception) -> None:
        halted_for.append(type(error).__name__)
        halt_for_slot(self, error)

    monkeypatch.setattr(RunView, "halt_for_slot", recording)
    monkeypatch.setattr(
        BreathingCircuit,
        "accepted_fresh_gas_flow_range_l_min",
        property(lambda circuit: (0.21, 0.29)),
    )

    with pytest.raises(ValueError, match="can offer no setting"):
        run._handle_reset()

    assert halted_for == ["SimulationConfigurationError"]
    assert controller.has_failed is True


def test_a_slot_that_raises_inside_the_halt_does_not_start_the_halt_again(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If a slot that the halt's own frame sets off raises, it does not halt every run again.

    Halting every run ends by drawing a frame. Laying that frame out emits `rangeChanged`,
    which calls `_follow_chart`. Before this change, when `_follow_chart` raised, its gate
    started the halt again inside the halt already under way. One exception started the halt
    21 times, nested 6 deep (blind review of `PL-HJKN`).
    """

    case = _branched_case()
    view = _case_view(application, case)
    depth = 0
    deepest = 0
    halt_every_run = SimulationView._halt_every_run

    def tracking(self: SimulationView, error: BaseException) -> None:
        nonlocal depth, deepest
        depth += 1
        deepest = max(deepest, depth)

        try:
            halt_every_run(self, error)
        finally:
            depth -= 1

    def refuse(self: SimulationView) -> NoReturn:
        raise RuntimeError("the chart is gone")

    monkeypatch.setattr(SimulationView, "_halt_every_run", tracking)
    view._chart_view_owed = True
    monkeypatch.setattr(SimulationView, "_chart_in_view", refuse)
    _take_fork(view, 60.0)
    _settle(application)

    assert deepest == 1
    assert [run.controller.has_failed for run in view.runs] == [True] * len(view.runs)


def test_every_dashboard_control_is_restated_on_a_halt(application: QApplication) -> None:
    """Every control on the dashboard is restated by a halt, or is named with why it need not be.

    A `RunView` restates its own widgets on a halt, and `PL-X7D5`'s guard enforces that by
    default. The dashboard's own panels sit outside every run. Each one used to be restated
    by hand in `_halt_every_run`, so a panel added later was restated only if someone
    remembered to add it there (`PL-5JTH`). This test builds the dashboard with every panel
    that holds a control. It gives the view a case, so that the branch panel is offered,
    adds a mark, and opens the marks editor. It then fails on any control that no run
    holds, that no `halt_restatements` panel holds, and that no container in
    `NOT_RESTATED_ON_A_HALT` holds.
    """

    case = _branched_case()
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(30.0), "check"))
    view = _case_view(application, case)
    _opened_bookmark_dialog(view)
    run_widgets = {id(widget) for run in view.runs for widget in _widget_attributes(run).values()}
    restated = {
        id(panel) for restatement in view.halt_restatements() for panel in restatement.panels
    }
    exemptions_used: set[str] = set()
    unrestated: list[str] = []

    for control in _controls(view):
        chain = _ancestry(control)

        if any(id(widget) in run_widgets or id(widget) in restated for widget in chain):
            continue

        exempt = next(
            (type(w).__name__ for w in chain if type(w).__name__ in NOT_RESTATED_ON_A_HALT), None
        )

        if exempt is not None:
            exemptions_used.add(exempt)
            continue

        unrestated.append(" < ".join(type(widget).__name__ for widget in chain[:6]))

    assert view._bookmark_dialog is not None
    assert sorted(set(unrestated)) == [], (
        "these controls are in no RunView and in no panel a halt restates: add their panel "
        "to SimulationView.halt_restatements, or name its container in "
        "NOT_RESTATED_ON_A_HALT with the reason a halt need not restate it"
    )
    assert sorted(set(NOT_RESTATED_ON_A_HALT) - exemptions_used) == [], (
        "these exemptions match no control on the dashboard now - remove the entry"
    )


#: The widget types outside every run that may show differently on a halted
#: dashboard and on the same dashboard once a frame draws it. Each type maps to
#: the reason that only a frame can state it. The test below checks this list
#: in both directions, as it checks `FRAME_WIDGETS`: an unlisted difference
#: fails, and so does an entry that no longer differs (`PL-WM5P`).
SURFACE_FRAME_WIDGETS: dict[str, str] = {
    "QScrollBar": (
        "a scroll bar follows the height the frame lays its scroll area out at, the page's "
        "or the control-change record's. Whether the bar is shown at all follows the same "
        "height. That is layout, and it states nothing about a run."
    )
}

#: The names that Qt gives the private widgets holding a `QScrollArea`'s two
#: scroll bars. Qt shows or hides a bar by showing or hiding its container. So
#: the walk below reads each container as part of its bar, not as a widget of
#: its own. A container is a plain `QWidget`, and an exemption for that type
#: would exempt every plain panel on the dashboard (`PL-CSK0`).
_SCROLL_BAR_CONTAINERS = frozenset({"qt_scrollarea_hcontainer", "qt_scrollarea_vcontainer"})


def _run_widget_ids(view: SimulationView) -> set[int]:
    """Every widget `_widget_attributes` names for a run, and every widget under each."""

    held: set[int] = set()

    for run in view.runs:
        for widget in (run, *_widget_attributes(run).values()):
            held.add(id(widget))
            held.update(id(child) for child in widget.findChildren(QWidget))

    return held


def _surface_widgets(view: SimulationView) -> dict[str, list[QWidget]]:
    """Every widget in the window that no run holds, grouped by its type and the five above it."""

    held = _run_widget_ids(view)
    surfaces: dict[str, list[QWidget]] = {}

    for widget in view.window().findChildren(QWidget):
        if id(widget) in held or widget.objectName() in _SCROLL_BAR_CONTAINERS:
            continue

        chain = " < ".join(type(w).__name__ for w in _ancestry(widget)[:6])
        surfaces.setdefault(chain, []).append(widget)

    return surfaces


def _surface_state(widget: QWidget) -> tuple[object, ...]:
    """Return what a reader sees of one widget outside the runs.

    For a scroll bar, the state also says whether the bar is shown within the
    window. Qt hides a bar by hiding its container, and the bar's own hidden
    flag stays false. Without this, a bar that appears only once a frame lays
    the page out would read the same in both states.
    """

    if isinstance(widget, QScrollBar):
        return (*_widget_state(widget), widget.isVisibleTo(widget.window()))

    return _widget_state(widget)


def _surface_states(view: SimulationView) -> dict[str, list[tuple[object, ...]]]:
    """Return what a reader sees of every widget outside the runs, read afresh.

    The window is walked again on each call. So a row that a frame adds, such
    as a newly listed mark, shows up as a difference rather than as a widget
    that nobody compares.
    """

    return {
        chain: [_surface_state(widget) for widget in widgets]
        for chain, widgets in _surface_widgets(view).items()
    }


def test_every_run_state_surface_outside_the_run_view_reads_alike_on_a_drawn_run_and_a_halted_one(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A halt states the run on every panel outside the runs, found by a walk rather than a list.

    `test_every_run_state_widget_reads_alike_on_a_drawn_run_and_a_halted_one`
    checks that each `RunView` has one writer of its run state (`PL-X7D5`).
    The branch panel, the marks panel, the marks editor and every Area's
    header sit outside the runs, and the halt restates them through
    `halt_restatements` (`PL-5JTH`). `test_every_dashboard_control_is_restated_on_a_halt`
    checks that each control is in a restated panel, but not what the panel
    then says. This test checks what it says. The run is drawn, and the
    branch panel is given a refusal. The refusal comes before the halt,
    because a halted trunk disables the branch controls. Then, while every
    frame fails, the test changes what the other panels state: it adds a
    mark and changes the playback rate. Finally it compares the halted
    screen, widget by widget, with the same dashboard once a frame draws it.
    So a panel that only a frame writes fails this test even though no list
    names it (`PL-WM5P`).
    """

    case = _branched_case()
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(30.0), "check"))
    view = _case_view(application, case)
    _opened_bookmark_dialog(view)
    view.present(False)
    _fork_panel(view).point_selector.clear()
    _fork_panel(view).take_button.click()
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(45.0), "later"))
    trunk = view.runs[0]
    trunk._playback_rate_dropdown.setCurrentIndex(trunk._playback_rate_dropdown.findData(5))
    view.present(False)

    assert case.trunk.has_failed is True
    assert _fork_panel(view).notice.notice() == FORK_NOTHING_SELECTED_TEXT

    halted = _surface_states(view)

    monkeypatch.undo()
    view.present(False)

    drawn = _surface_states(view)
    differing = {
        chain.partition(" < ")[0]
        for chain in set(halted) | set(drawn)
        if halted.get(chain) != drawn.get(chain)
    }

    unexplained = {
        chain: (halted.get(chain), drawn.get(chain))
        for chain in set(halted) | set(drawn)
        if halted.get(chain) != drawn.get(chain)
        and chain.partition(" < ")[0] not in SURFACE_FRAME_WIDGETS
    }

    assert len(halted) > 20, "the walk found too few widgets to be reading the window"
    assert sorted(differing - set(SURFACE_FRAME_WIDGETS)) == [], (
        "these widgets outside every run read differently on a halted dashboard and on the "
        "same dashboard drawn: restate them from SimulationView.halt_restatements, or name "
        "their type in SURFACE_FRAME_WIDGETS with the reason only a frame can state them. "
        "Each chain below is followed by its widgets as the halt left them, then as a frame "
        "drew them, each as (type, hidden, enabled, style sheet, text or value):\n"
        + "\n".join(
            f"{chain}\n  halted: {pair[0]}\n  drawn:  {pair[1]}"
            for chain, pair in sorted(unexplained.items())
        )
    )
    assert sorted(set(SURFACE_FRAME_WIDGETS) - differing) == [], (
        "these widgets read alike on a halted dashboard and a drawn one now, so their "
        "exemption is stale - remove the entry"
    )


def test_the_surface_guard_fails_on_a_panel_only_a_frame_writes(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The guard above catches a panel that a halt leaves as the last frame drew it.

    The marks panel's restatement is switched off here. The mark added while
    frames fail is then listed on the drawn dashboard and not on the halted
    one, which is the stale state the guard exists to catch.
    """

    case = _branched_case()
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(30.0), "check"))
    view = _case_view(application, case)
    view.present(False)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(view, "_restate_bookmark_panel", lambda: None)

    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(45.0), "later"))
    view.present(False)
    halted = _surface_states(view)

    monkeypatch.undo()
    view.present(False)

    drawn = _surface_states(view)
    differing = {
        chain for chain in set(halted) | set(drawn) if halted.get(chain) != drawn.get(chain)
    }

    assert any("MarkListingLabel" in chain for chain in differing)


def test_the_surface_guard_reads_a_scroll_bar_qt_shows_through_its_container_as_the_bar(
    application: QApplication,
) -> None:
    """A record column whose scroll bar appears is read as a scroll bar difference.

    In the drift run of 2026-11-02, under PySide6 6.12, the control-change
    record overflowed its column on the drawn dashboard and not on the halted
    one. So its vertical bar appeared only once a frame drew the dashboard. Qt
    shows the bar by showing its private container, a plain `QWidget`. The
    guard above therefore reported a `QWidget` that read differently
    (`PL-CSK0`). This test makes the record overflow on purpose. It checks
    that the difference is read on the bar, which `SURFACE_FRAME_WIDGETS`
    exempts as layout, and on no plain `QWidget`.
    """

    view = _case_view(application, _branched_case())
    view.present(False)
    _settle(application)
    record_scroll = next(
        area
        for area in view.unconditional_region.findChildren(QScrollArea)
        if area.widget() is not None
        and area.widget().objectName() == simulation_view_module._RECORD_COLUMN_NAME
    )
    # The bar starts hidden whatever the platform's fonts make of the record's
    # height. Turning the bar off hides its container, which is how Qt hides
    # a bar that is not needed.
    record_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    _settle(application)
    assert not record_scroll.verticalScrollBar().isVisibleTo(view.window())
    fitting = _surface_states(view)

    record_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    record_scroll.widget().setMinimumHeight(record_scroll.viewport().height() + 400)
    _settle(application)
    overflowing = _surface_states(view)

    differing = {
        chain.partition(" < ")[0]
        for chain in set(fitting) | set(overflowing)
        if fitting.get(chain) != overflowing.get(chain)
    }

    assert record_scroll.verticalScrollBar().isVisibleTo(view.window())
    assert differing == {"QScrollBar"}


def test_a_dial_write_that_refuses_on_a_halt_still_restates_every_panel(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A run whose dials cannot be written on a halt still lets the halt restate every panel.

    `show_presentation` writes the dials last and raises when `setting_readouts`
    cannot build them, as `test_a_halt_is_stated_before_its_dials_are_written`
    shows for one run. `_halt_every_run` used to call it in a bare loop. So the
    exception left the halt path before the branch panel and the bookmark panel
    were restated. "Branch here" stayed enabled over a failed trunk, and a mark
    ahead of the clock went on showing as still to come (`PL-TLH4`). The exception
    now waits until the panels are restated and the frame is tried. The test
    checks the bookmark row against the literal text of a mark that a failed run
    cannot reach, as `test_a_failing_frame_withdraws_the_last_frames_bookmark_standings`
    does.
    """

    case = _branched_case()
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(600.0), "check"))
    view = _case_view(application, case)
    here = _fork_panel(view).here_button
    assert here.isHidden() is False, "the paused trunk offers no branch here to withdraw"
    assert _marks_panel(view).times.text() == "10m – check"
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(
        BreathingCircuit,
        "accepted_fresh_gas_flow_range_l_min",
        property(lambda circuit: (0.21, 0.29)),
    )

    with pytest.raises(ValueError, match="can offer no setting"):
        view.present(False)

    assert case.trunk.has_failed is True
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT
    assert here.isHidden() is True
    assert _fork_panel(view).point_selector.count() == 0
    assert _marks_panel(view).times.text() == (
        "10m – check · not reached before the simulation error"
    )


def test_a_withdrawn_bookmark_panel_withdraws_the_open_dialog(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A halt that withdraws the bookmark panel withdraws the editor's lists and Remove buttons too.

    The editor lists the same rows as the panel beside the chart. A halt that could not
    work out the marks' standings used to hide the panel but leave the open editor
    listing the last frame's rows. The editor then still showed the mark ahead of the
    clock as still to come, and its Remove button still worked on that row (`PL-F5KT`).
    The next frame that is drawn shows both again.
    """

    controller = _paused_run_with_history()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600.0), "check"))
    view = _shown_view(application, controller)
    dialog = _opened_bookmark_dialog(view)
    withdrawn = (
        dialog.time_list,
        dialog.remove_time_button,
        dialog.target_list,
        dialog.remove_target_button,
    )
    assert dialog.time_list.count() == 1
    assert not any(widget.isHidden() for widget in withdrawn)

    def unanswerable(self: SimulationController) -> NoReturn:
        raise RuntimeError("the run could not say where it stands on its marks")

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(SimulationController, "bookmark_standings", unanswerable)

    view.present(False)

    assert controller.has_failed is True
    assert _marks_panel(view).times.isHidden() is True
    assert all(widget.isHidden() for widget in withdrawn)

    monkeypatch.undo()
    view.present(False)

    assert not any(widget.isHidden() for widget in withdrawn)


#: A mark name long enough that its row wraps in the bookmark panel at any
#: width the page allows.
_WRAPPING_MARK_NAME = "a mark name long enough to wrap " * 10


@pytest.mark.parametrize("height_px", [450, 1000])
def test_a_wrapped_mark_row_is_never_clipped(application: QApplication, height_px: int) -> None:
    """A mark row that wraps gets the height its lines need in a narrow window (`PL-KX97`).

    The row's name is long enough to wrap at the page's narrowest width, so
    the row under test does wrap. The expected height is the label's own
    `heightForWidth`, not a value read from the layout under test. A short
    window must scroll the page rather than squeeze the row.
    """

    case = BranchedCase(SimulationController())
    case.trunk.add_mac_target(
        MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5), _WRAPPING_MARK_NAME)
    )
    view = _case_view(application, case, width_px=700)
    view.resize(700, height_px)
    application.processEvents()
    view.present(False)
    application.processEvents()
    rows = [
        label
        for label in _marks_panel(view).findChildren(QLabel)
        if label.isVisible() and label.wordWrap() and _WRAPPING_MARK_NAME.strip() in label.text()
    ]

    assert rows

    for row in rows:
        needed_px = row.heightForWidth(row.width())

        assert needed_px > row.fontMetrics().height(), "the row does not wrap"
        assert needed_px <= row.height()
