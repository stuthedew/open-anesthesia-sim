"""Every slot of a view that holds a run is called through the halt gate in this module.

A run whose snapshot rejects a value must stop, and the screen must say that
it stopped (`PL-7DJK`). Qt calls a slot from its event loop. When a slot
raises, PySide6 prints the exception and goes on, and `emit` returns as if
nothing had happened (measured on PySide6 6.11.2, 2026-10-25). So an exception
that escapes a slot halts nothing, and the screen goes on showing "Paused" for
a controller that cannot continue.

Before `PL-HJKN`, a `try` was added to each slot by hand. Six slots were found
without one, each in a separate review (`PL-YK2V`, `PL-7DJK`, `PL-V2HC`,
`PL-08SS`, `PL-F2T2`, `PL-M3M2`). `halt_gate` is now the one place where an
exception raised inside a slot becomes a halt.
`test_every_slot_that_touches_a_run_passes_the_halt_gate` reads the source of
`RunView` and `SimulationView`. It fails on a connected slot that is not
wrapped in the gate. This module imports no GUI toolkit.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any, Concatenate, Final, Protocol

#: The attribute that `halt_gate` sets on each function it returns, which
#: `passes_halt_gate` reads.
_GATED_ATTRIBUTE: Final = "__passes_halt_gate__"

#: The attribute that `halt_gate` sets on an exception that `halt_for_slot` raised.
#: Each outer gate that the exception leaves passes it on and does not halt again.
_RAISED_BY_THE_HALT_ATTRIBUTE: Final = "__raised_by_halt_for_slot__"


class HaltingView(Protocol):
    """A view whose slots pass the halt gate, and what a raise inside one of them halts."""

    def halt_for_slot(self, error: Exception) -> None:
        """Halt what this view's slots act on, because of `error`, and show the halt on screen.

        `RunView` halts its own run. `SimulationView` halts every run, because
        its slots act on the case rather than on one run.

        Raises:
            Exception: The exception that showing the halt raised. It is raised only
                once every widget that could show the halt is showing it (`PL-TLH4`).
        """


def halt_gate[View: HaltingView, **Params](
    slot: Callable[Concatenate[View, Params], None],
) -> Callable[Concatenate[View, Params], None]:
    """Make an exception raised inside `slot` halt the view's run, rather than escape to Qt.

    The returned method runs `slot`. When `slot` raises an `Exception`, the returned
    method passes it to the view's `halt_for_slot`. A slot can raise when it reads a
    snapshot that rejects a value, or when a setting or a step that it applies raises.
    Either way, the run is left halted and the halt is shown on screen. A method that a
    gated slot calls may be gated as well. The inner gate then halts and returns, and
    the outer slot goes on.

    Showing the halt can itself raise (`PL-TLH4`). The gate marks that exception, and
    each outer gate passes it on. Otherwise each outer gate would show the whole halt
    a second time, with the halt's own exception as the reason.

    Qt hands a slot only as many of its signal's arguments as the slot takes. The
    returned method does the same for `slot`. It has to, because it takes `*args`
    itself, and PySide6 hands such a method every argument of the signal. Otherwise
    a slot that takes no argument, connected to `rangeChanged`, would be called with
    two (measured on PySide6 6.11.2, 2026-10-25).

    Args:
        slot: A method of a `HaltingView` that returns nothing.

    Returns:
        The gated method, marked so that `passes_halt_gate` returns True for it.
    """

    capacity = _positional_capacity(slot)
    call: Callable[..., None] = slot

    @wraps(slot)
    def gated(view: View, /, *args: Params.args, **kwargs: Params.kwargs) -> None:
        passed: tuple[Any, ...] = args if capacity is None else args[:capacity]

        try:
            call(view, *passed, **kwargs)
        except Exception as error:
            if getattr(error, _RAISED_BY_THE_HALT_ATTRIBUTE, False) is True:
                raise

            try:
                view.halt_for_slot(error)
            except Exception as halt_error:
                setattr(halt_error, _RAISED_BY_THE_HALT_ATTRIBUTE, True)
                raise

    setattr(gated, _GATED_ATTRIBUTE, True)

    return gated


def passes_halt_gate(method: object) -> bool:
    """Whether `method` is a function or method that `halt_gate` returned."""

    return getattr(method, _GATED_ATTRIBUTE, False) is True


def _positional_capacity(slot: Callable[..., None]) -> int | None:
    """How many positional arguments `slot` takes after the view, or None if it takes any number.

    Args:
        slot: The method's function, whose first parameter is the view.

    Raises:
        TypeError: If `slot` takes no parameter for the view.
    """

    parameters = list(inspect.signature(slot).parameters.values())

    if not parameters:
        raise TypeError(f"{slot.__qualname__} takes no view, so it is not a method of one")

    kinds = [parameter.kind for parameter in parameters[1:]]

    if inspect.Parameter.VAR_POSITIONAL in kinds:
        return None

    positional = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)

    return sum(1 for kind in kinds if kind in positional)
