"""The halt gate, through which every slot of a view that holds a run is called.

A run whose snapshot refuses a value must stop, and the screen must say that
it stopped (`PL-7DJK`). Qt calls a slot from its event loop. When a slot
raises, PySide6 prints the exception and goes on, and `emit` returns as if
nothing had happened (measured on PySide6 6.11.2, 2026-10-25). So an exception
that leaves a slot halts nothing, and the run goes on reading "Paused" over a
controller that cannot continue.

Before `PL-HJKN`, each slot was put behind a `try` by hand. Six slots were
found outside it, one review at a time (`PL-YK2V`, `PL-7DJK`, `PL-V2HC`,
`PL-08SS`, `PL-F2T2`, `PL-M3M2`). `halt_gate` is now the one place where an
exception raised inside a slot becomes a halt.
`test_every_slot_that_touches_a_run_passes_the_halt_gate` reads `RunView` and
`SimulationView` and fails on a connected slot that does not pass the gate.
This module loads no toolkit.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any, Concatenate, Final, Protocol

#: The attribute that `halt_gate` sets on each function it returns, which
#: `passes_halt_gate` reads.
_GATED_ATTRIBUTE: Final = "__passes_halt_gate__"


class HaltingView(Protocol):
    """A view whose slots pass the halt gate, and what a raise inside one of them halts."""

    def halt_for_slot(self, error: Exception) -> None:
        """Halt what this view's slots act on for `error`, and state the halt on screen.

        `RunView` halts its own run. `SimulationView` halts every run, because
        its slots act on the case rather than on one run.

        Raises:
            Exception: What stating the halt raised, once the halt is on every
                widget that could show it (`PL-TLH4`).
        """


def halt_gate[View: HaltingView, **Params](
    slot: Callable[Concatenate[View, Params], None],
) -> Callable[Concatenate[View, Params], None]:
    """Make a raise inside `slot` halt the view's run, rather than escape to Qt.

    The returned method runs `slot`. When `slot` raises an `Exception`, it calls
    the view's `halt_for_slot` with it. So a slot that reads a refusing snapshot,
    or that a setting or a step makes raise, leaves the run halted and the halt on
    screen. A method that a gated slot calls may pass the gate as well. The inner
    gate then halts and returns, and the outer one has nothing to catch.

    Qt hands a slot every argument of its signal, unless the slot takes fewer.
    The returned method does the same for `slot`. It takes `*args` itself, and
    PySide6 hands such a method every argument of the signal. A slot that takes
    no argument connected to `rangeChanged` would otherwise be called with two
    (measured on PySide6 6.11.2, 2026-10-25).

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
            view.halt_for_slot(error)

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
