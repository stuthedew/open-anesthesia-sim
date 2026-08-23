"""Flet application entry point: configures the page and assembles the
controller and view. `uv run anesthesia-sim` runs `main()` below.
"""

import flet as ft

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import BACKGROUND, PAGE_PADDING
from anesthesia_sim.app_metadata import APP_DISPLAY_NAME


async def build_app(page: ft.Page) -> None:
    """Configure the page and assemble the application."""

    page.title = APP_DISPLAY_NAME
    page.bgcolor = BACKGROUND
    page.padding = PAGE_PADDING
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.full_screen = True

    controller = SimulationController()
    simulation_view = SimulationView(
        page=page,
        controller=controller,
    )

    simulation_view.mount()
    simulation_view.start_simulation_timer()


def main() -> None:
    """Launch the Flet application."""

    ft.run(build_app)


if __name__ == "__main__":
    main()
