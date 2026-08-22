from math import exp

import pytest

from anesthesia_sim.core.demo_model import response


def test_starts_at_zero() -> None:
    assert response(0.0, 10.0) == pytest.approx(0.0)


def test_one_time_constant() -> None:
    assert response(10.0, 10.0) == pytest.approx(1.0 - exp(-1.0))


def test_larger_time_constant_produces_slower_response() -> None:
    slow_response = response(10.0, 20.0)
    fast_response = response(10.0, 10.0)

    assert slow_response < fast_response


@pytest.mark.parametrize(
    "elapsed_s,time_constant_s",
    [(-1.0, 10.0), (1.0, 0.0), (1.0, -2.0)],
)
def test_rejects_invalid_inputs(
    elapsed_s: float,
    time_constant_s: float,
) -> None:
    with pytest.raises(ValueError):
        response(elapsed_s, time_constant_s)
