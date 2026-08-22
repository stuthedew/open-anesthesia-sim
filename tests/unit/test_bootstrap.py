from collections.abc import Callable
from importlib.metadata import distribution
from typing import Any

import anesthesia_sim
import anesthesia_sim.app.main as app_main


def test_import() -> None:
    assert anesthesia_sim is not None


def test_console_script_points_to_application_launcher() -> None:
    package = distribution("anesthesia-sim")

    console_script = next(
        entry_point
        for entry_point in package.entry_points
        if entry_point.group == "console_scripts" and entry_point.name == "anesthesia-sim"
    )

    assert console_script.value == ("anesthesia_sim.app.main:main")


def test_application_launcher_starts_flet(
    monkeypatch: Any,
) -> None:
    launched_targets: list[Callable[..., Any]] = []

    def record_launch(
        target: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        del args, kwargs
        launched_targets.append(target)

    monkeypatch.setattr(
        app_main.ft,
        "run",
        record_launch,
    )

    app_main.main()

    assert launched_targets == [app_main.build_app]
