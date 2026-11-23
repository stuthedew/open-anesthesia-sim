"""Tests of the words a branch refused for changed values gives the learner and the developer."""

from __future__ import annotations

import dataclasses
import logging

import pytest

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.core.concentration import MacPercent, Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.mac import mac_for_patient
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.supported_ranges import CaseInstant


def test_a_branch_rebuilt_on_changed_data_gives_the_learner_and_the_developer_their_own_text(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """The learner reads the reason and what to do, and the developer reads each differing value.

    The agent's file is edited after the run began, in two of the references a
    branch checks, so the branch would open under another name and another
    MAC. The exception's message is the learner's: it gives the fork in the
    panel's own form, names both possible causes and names no value. The
    exception's note and the failure log carry each differing value with both
    of its values, joined in the order they are compared (`PL-72X2`).
    """

    trunk = SimulationController()
    trunk.start()
    for _ in range(30):
        trunk.advance()
    trunk.set_delivered_concentration_percent(Percent(4.0))
    for _ in range(30):
        trunk.advance()
    trunk.pause()

    on_file = load_agent_parameters(trunk.snapshot().agent_id)
    edited = dataclasses.replace(
        on_file,
        display_name="Edited",
        mac_at_age_40_percent=MacPercent(on_file.mac_at_age_40_percent + 0.1),
    )
    monkeypatch.setattr(
        "anesthesia_sim.app.controller.load_agent_parameters", lambda agent_id: edited
    )
    patient = load_reference_adult_parameters()

    with (
        caplog.at_level(logging.ERROR, logger="anesthesia_sim"),
        pytest.raises(SimulationConfigurationError) as refusal,
    ):
        trunk.resumed_at(CaseInstant(30))

    note = (
        "a branch at 30 s was rebuilt with values this run did not hold there: "
        f"agent_display_name is {on_file.display_name!r} in this run and 'Edited' on the "
        f"branch; agent_mac is {mac_for_patient(on_file, patient)!r} in this run and "
        f"{mac_for_patient(edited, patient)!r} on the branch "
        '(docs/ARCHITECTURE.md, "What a branch is, and what it shares with its parent")'
    )

    assert str(refusal.value) == (
        "a branch at 30s would not open on the values this run held there, so it would be a "
        "different case rather than another way of managing this one. The simulator's data "
        "may have changed since this run began, or the simulator may have a fault. Reopen "
        "the simulator and run the case again to branch it. If this notice comes back at "
        "the same point, the cause is a fault in the simulator"
    )
    assert refusal.value.__notes__ == [note]
    assert [(record.levelno, record.getMessage()) for record in caplog.records] == [
        (logging.ERROR, f"Branch refused: {note}")
    ]
