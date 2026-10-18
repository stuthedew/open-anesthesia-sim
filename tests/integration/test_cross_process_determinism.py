"""A run gives bit-identical results in another process with another hash seed.

`docs/MODEL.md` § "The reproducibility guarantee" promises that two runs of
one case produce element-wise identical run definitions and snapshots. Every
other determinism test compares two runs inside one interpreter, where every
`set` and `dict` of strings iterates in the same order both times. A sum taken
over a set, or an order taken from `id()`, would differ only between
processes, and often only in the last bits. So this test runs one scripted
case in two child processes with different `PYTHONHASHSEED` values, and once
in this process, and compares an exact digest of each result (`PL-75D9`).

A builtin `sum()` over floats rarely trips this test, because since Python
3.12 it adds with Neumaier's compensated summation, whose result seldom
depends on the order of the terms. An accumulation written as a loop or with
`functools.reduce` has no such protection. Sorting the terms of `propagate()`'s
row products by the hash of their `repr` fails this test when done with
`functools.reduce` and passes it when done with `sum()` (2026-10-18).

The digest is not compared with a stored value. `docs/MODEL.md` makes no
promise across platforms, and another maths library may round a
transcendental function differently.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow

#: The step of the scripted case, in seconds.
STEP_S = 0.1
#: The number of steps in the scripted case: ten minutes of 0.1 s steps.
STEPS = 6000
#: Each setting change in the scripted case, keyed by the step count at which
#: it happens. Every setting changes at least once.
CHANGES: dict[int, Callable[[SimulationController], None]] = {
    600: lambda c: c.set_fresh_gas_flow(FreshGasFlow(2.0)),
    1500: lambda c: c.set_alveolar_ventilation(AlveolarVentilation(6.0)),
    2400: lambda c: c.set_cardiac_output(CardiacOutput(4.5)),
    3300: lambda c: c.set_delivered_concentration_percent(Percent(5.0)),
    4800: lambda c: c.set_delivered_concentration_percent(Percent(0.0)),
}
#: Two hash seeds, so that the two child processes iterate sets of strings in
#: different orders.
SEEDS = ("0", "12345")


def digest() -> str:
    """Return the SHA-256 of the scripted run's final snapshot and run segments."""
    controller = SimulationController()
    controller.start()
    for step in range(STEPS):
        if step in CHANGES:
            CHANGES[step](controller)
        controller.advance(SimulationStep(STEP_S))
    text = repr(controller.snapshot()) + repr(controller.run_segments)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _in_child(seed: str) -> tuple[str, str]:
    """Return `digest()` and the hash of one string, from a fresh interpreter under `seed`."""
    code = (
        f"import sys; sys.path.insert(0, {str(Path(__file__).parent)!r}); "
        "import test_cross_process_determinism as t; print(t.digest()); print(hash('sevoflurane'))"
    )
    done = subprocess.run(
        [sys.executable, "-c", code],
        env={**os.environ, "PYTHONHASHSEED": seed},
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    run_digest, string_hash = done.stdout.split("\n")[:2]
    return run_digest, string_hash


def test_a_run_is_bit_identical_across_processes_and_hash_seeds() -> None:
    children = [_in_child(seed) for seed in SEEDS]
    # Without this check the test could pass because the seed never reached the child.
    assert children[0][1] != children[1][1], "the two hash seeds gave the same hash of a string"
    assert [run_digest for run_digest, _ in children] == [digest()] * len(SEEDS)
