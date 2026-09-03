"""Render modeled values as the strings the interface displays.

Pure formatting, independent of Flet and of the scientific core: every
function here takes a number the model produced and returns the text a
reader sees. Nothing in this module builds a control, reads simulation
state, or performs a physiological calculation.

Why it is its own module. `docs/MODEL.md` § "Displayed precision" is a
derivation - from the shipped operator split's measured error, to how many
digits of a concentration are worth showing - and this is where that
derivation terminates. `CLAUDE.md` treats presentation correctness as part
of the safety standard and requires a displayed value to be traceable to
the transformations that produced it, so the last transformation in that
chain has to be readable, citable and testable on its own rather than
reachable only by loading the whole dashboard. `tests/unit/test_formatting.py`
is what pins it.

The displayed resolution is a property of the display alone. Everything
upstream carries full binary64 - the compartment states, every integration
step, every `SimulationHistorySample` - and the rounding happens exactly
once, here.
"""

from typing import Final

from anesthesia_sim.app_metadata import APP_VERSION

__all__ = [
    "CONCENTRATION_DISPLAY_DECIMALS",
    "CONCENTRATION_DISPLAY_RESOLUTION_PERCENT",
    "FLOW_DISPLAY_DECIMALS",
    "format_delivered_label",
    "format_percent",
    "format_subtitle",
]

# Displayed resolution for every modeled concentration and relative partial
# pressure, and for the delivered-agent setting shown beside its slider. Two
# decimals of a percent — 0.01 percentage points — is a recorded decision
# (PL-040), justified in `docs/MODEL.md` § "Displayed precision" against the
# measured error of the shipped operator split. The short version: the
# split disagrees with the independent solution by up to 5e-3 percentage
# points at the default flows and 1.2e-2 at the extreme corner of the
# settings envelope, so the second decimal is the uncertain digit — as the
# last displayed digit should be — and the third and beyond were noise.
# Changing this is a safety-critical change to how a clinical value reads,
# not a formatting preference: revise the documented basis with it.
CONCENTRATION_DISPLAY_DECIMALS: Final = 2
# Smallest percentage-point difference the concentration readouts resolve.
CONCENTRATION_DISPLAY_RESOLUTION_PERCENT: Final = 10.0**-CONCENTRATION_DISPLAY_DECIMALS

# Decimals shown on the flow sliders' drag labels, matching the ".1f L/min"
# readouts beside them. Flet's default is 0, which would make a slider's own
# label disagree with the text next to it mid-drag.
FLOW_DISPLAY_DECIMALS: Final = 1


def format_percent(concentration_fraction: float) -> str:
    """Convert a concentration fraction to display percent.

    Renders at `CONCENTRATION_DISPLAY_RESOLUTION_PERCENT`, the
    resolution `docs/MODEL.md` § "Displayed precision" justifies against
    the measured error of the shipped operator split.

    A value that is positive but rounds to zero is rendered as below the
    resolution rather than as zero. The distinction is the point: muscle
    and fat sit under 0.01% for the first minutes of a run — fat for
    thirteen of them at 1 MAC sevoflurane — and `0.00%` there would
    assert a compartment is empty when the model says it is filling.
    `<0.01%` says only what is known, and leaves `0.00%` meaning what it
    should, that nothing has arrived yet.

    A negative fraction is deliberately not given the below-resolution
    form. The compartment guards make one impossible, so if one ever
    reaches here it must stay visible as the anomaly it is rather than
    be absorbed into a plausible-looking reading.

    Args:
        concentration_fraction: Dimensionless concentration
            fraction from zero through one.

    Returns:
        Concentration as percent at the displayed resolution, or the
        below-resolution form for a positive value that rounds to zero.
    """

    percent = concentration_fraction * 100.0
    rendered = f"{percent:.{CONCENTRATION_DISPLAY_DECIMALS}f}"

    if percent > 0.0 and float(rendered) == 0.0:
        resolution = CONCENTRATION_DISPLAY_RESOLUTION_PERCENT

        return f"<{resolution:.{CONCENTRATION_DISPLAY_DECIMALS}f}%"

    return f"{rendered}%"


def format_subtitle(agent_display_name: str) -> str:
    """Build the header subtitle naming the current app version and agent."""

    return f"Version {APP_VERSION} — {agent_display_name} patient model"


def format_delivered_label(agent_display_name: str) -> str:
    """Build the delivered-concentration panel label naming the agent."""

    return f"Delivered {agent_display_name.lower()}"
