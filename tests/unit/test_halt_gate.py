"""Test that a gated slot's exception halts the view, and that Qt's extra arguments are dropped.

`app/halt_gate.py` imports no GUI toolkit, so these tests call a gated method directly,
with the arguments that Qt would hand it. The dashboard's own tests drive the gate
through real slots, and `test_every_slot_that_touches_a_run_passes_the_halt_gate`
checks that every slot is wrapped in it (`PL-HJKN`).
"""

from __future__ import annotations

import pytest

from anesthesia_sim.app.halt_gate import halt_gate, passes_halt_gate


class _View:
    """A view that records each halt and each call its slots receive."""

    def __init__(self) -> None:
        self.halts: list[Exception] = []
        self.calls: list[tuple[object, ...]] = []

    def halt_for_slot(self, error: Exception) -> None:
        self.halts.append(error)

    @halt_gate
    def takes_nothing(self) -> None:
        self.calls.append(())

    @halt_gate
    def takes_one(self, index: int) -> None:
        self.calls.append((index,))

    @halt_gate
    def takes_any(self, *values: int) -> None:
        self.calls.append(values)

    @halt_gate
    def takes_a_keyword(self, value: int, *, coalesce: bool = False) -> None:
        self.calls.append((value, coalesce))

    @halt_gate
    def raises(self) -> None:
        raise ValueError("the snapshot refused a value")

    def ungated(self) -> None:
        self.calls.append(())


def test_a_raise_inside_a_gated_slot_halts_the_view_and_does_not_escape() -> None:
    view = _View()

    view.raises()

    assert [str(error) for error in view.halts] == ["the snapshot refused a value"]


def test_a_slot_that_returns_does_not_halt() -> None:
    view = _View()

    view.takes_nothing()

    assert view.halts == []
    assert view.calls == [()]


def test_a_gated_slot_is_handed_only_as_many_arguments_as_it_takes() -> None:
    """PySide6 hands a gated method every argument of the signal, as `rangeChanged` hands two.

    Qt hands a plain slot only as many as it takes, so the gate does the same. Without
    that, a slot that takes nothing would raise `TypeError` on every signal with an
    argument, and the gate would halt the run for it.
    """

    view = _View()

    view.takes_nothing(0, 100)  # type: ignore[call-arg]
    view.takes_one(3, 7)  # type: ignore[call-arg]
    view.takes_any(1, 2, 3)

    assert view.halts == []
    assert view.calls == [(), (3,), (1, 2, 3)]


def test_a_keyword_reaches_the_slot() -> None:
    view = _View()

    view.takes_a_keyword(4, coalesce=True)

    assert view.calls == [(4, True)]


def test_a_keyword_only_parameter_takes_no_signal_argument() -> None:
    """A signal's second argument is dropped, rather than filling a keyword-only parameter.

    Counting the keyword-only `coalesce` as a place for a positional argument would pass
    9 to a slot that takes one, which raises `TypeError` (coverage review of `PL-HJKN`).
    """

    view = _View()

    view.takes_a_keyword(4, 9)  # type: ignore[call-arg]

    assert view.halts == []
    assert view.calls == [(4, False)]


def test_a_raise_from_the_halt_itself_escapes_once_the_halt_is_called() -> None:
    """Stating a halt can raise, as `present_halt` does for a dial with no setting.

    That exception still reaches the console, after the halt has been stated (`PL-TLH4`).
    """

    class _FailingHaltView(_View):
        def halt_for_slot(self, error: Exception) -> None:
            super().halt_for_slot(error)
            raise RuntimeError("the dials could not be written")

    view = _FailingHaltView()

    with pytest.raises(RuntimeError, match="the dials could not be written"):
        view.raises()

    assert [str(error) for error in view.halts] == ["the snapshot refused a value"]


class _NestingView(_View):
    """A view with a gated slot that calls another gated slot, as `_handle_fork` calls `present`."""

    @halt_gate
    def calls_a_raising_slot(self) -> None:
        self.raises()
        self.calls.append(("after the inner slot",))


def test_a_raise_inside_a_nested_gated_slot_halts_once_and_the_outer_slot_goes_on() -> None:
    view = _NestingView()

    view.calls_a_raising_slot()

    assert [str(error) for error in view.halts] == ["the snapshot refused a value"]
    assert view.calls == [("after the inner slot",)]


def test_a_raise_from_the_halt_inside_a_nested_gated_slot_halts_only_once() -> None:
    """An exception raised while the view shows a halt passes through each outer gate.

    No outer gate halts the run again. Each outer gate used to catch the exception as a new
    error and show the whole halt a second time, with that exception as the reason (blind
    review of `PL-HJKN`).
    """

    class _FailingHaltNestingView(_NestingView):
        def halt_for_slot(self, error: Exception) -> None:
            super().halt_for_slot(error)
            raise RuntimeError("the dials could not be written")

    view = _FailingHaltNestingView()

    with pytest.raises(RuntimeError, match="the dials could not be written"):
        view.calls_a_raising_slot()

    assert [str(error) for error in view.halts] == ["the snapshot refused a value"]
    assert view.calls == []


def test_passes_halt_gate_tells_a_gated_method_from_an_ungated_one() -> None:
    assert passes_halt_gate(_View.takes_nothing) is True
    assert passes_halt_gate(_View().takes_nothing) is True
    assert passes_halt_gate(_View.ungated) is False
    assert passes_halt_gate(None) is False


def test_a_function_that_takes_no_view_is_refused() -> None:
    def no_view() -> None:
        pass

    with pytest.raises(TypeError, match="takes no view"):
        halt_gate(no_view)  # type: ignore[arg-type]
