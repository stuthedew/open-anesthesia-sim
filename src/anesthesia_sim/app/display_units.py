"""The units the interface states, each spelled in one place (`PL-G84G`).

A unit shown beside a value is part of that value under `CLAUDE.md`'s
safety-critical standard: the correct number with the wrong unit is still a
safety failure. Before `PL-G84G` gathered the units here, the panel typed
"L/min" beside each flow slider, the run record typed it again for each recorded
change, and the formatter typed it a third time. A change to one would have left
the other two stating the old unit. No check reads strings, so nothing would
have noticed.

So each unit is one `DisplayUnit` member, and every place the interface writes
the unit reads it from that member. A member holds each spelling a reader
meets. The run record writes `recorded` beside a recorded control change. The
panel and the formatters write `label` beside a value. The chart writes
`axis_title` on an axis drawn in the unit.

The delivered concentration shows why one member holds three spellings. The
record states its unit in full, "percent of 1 atm", because the record has to
say what the percent is of. The panel shows "%" beside the slider, where the
full phrase would not fit. The chart's left axis says "% of 1 atm". The three
spellings are one unit, so they live in one member.

The units live in `app/`, not in `core/units.py`, because a label is
presentation, and `CLAUDE.md` keeps presentation out of the calculation code.
Other repeated strings, such as message fragments, are left to code review. A
check that read strings would have to guess which of them are units.

An amount of agent is a volume of vapour, and a volume of gas means nothing
without the temperature and pressure it is stated at. The model states every
amount at one condition, 20 °C and 1 atm (`docs/MODEL.md` § "Agent amount").
`REFERENCE_CONDITION_LABEL` names that condition, and every place that shows an
agent amount names it from there (`PL-HQPF`). The label is built from the
constants that the conversion from vapour to liquid uses, so a change to either
constant changes the label with it (`PL-RJN9`).
"""

from enum import Enum
from typing import Final

from anesthesia_sim.core.liquid_agent import (
    REFERENCE_PRESSURE_PA,
    REFERENCE_TEMPERATURE_CELSIUS,
    STANDARD_ATMOSPHERE_PA,
)

__all__ = ["REFERENCE_CONDITION_LABEL", "REFERENCE_TEMPERATURE_LABEL", "DisplayUnit"]

#: The temperature at which the model states every amount of agent, as a label.
#: A liquid volume needs only the temperature, because a liquid's volume barely
#: changes with pressure.
REFERENCE_TEMPERATURE_LABEL: Final = f"{REFERENCE_TEMPERATURE_CELSIUS:g} °C"

#: The temperature and pressure at which the model states every amount of
#: agent vapour, as a label. The pressure is written in standard atmospheres.
REFERENCE_CONDITION_LABEL: Final = (
    f"{REFERENCE_TEMPERATURE_LABEL} and {REFERENCE_PRESSURE_PA / STANDARD_ATMOSPHERE_PA:g} atm"
)


class DisplayUnit(Enum):
    """One unit the interface states, with the three spellings a reader meets.

    Attributes:
        recorded: The unit as the run record writes it beside a recorded
            control change.
        label: The text shown beside a value, on a slider or in a readout.
        axis_title: The title of a chart axis drawn in the unit.
    """

    FLOW = ("L/min", "L/min", "L/min")
    CONCENTRATION = ("percent of 1 atm", "%", "% of 1 atm")
    # The multiplication sign is there for safety, not for typography. A reader
    # takes "0.80 MAC" as a depth of anesthesia. "0.80 ×MAC" says what the number
    # actually is: a partial pressure expressed as a multiple of the concentration
    # that would be 1 MAC. `docs/MODEL.md` § "MAC multiples as a display unit"
    # states the convention.
    MAC_MULTIPLE = ("multiple of MAC", "×MAC", "×MAC")
    # An agent amount's unit always says whether it counts vapour or liquid. A
    # millilitre of liquid gives about 180 to 210 mL of vapour, depending on the
    # agent, so a bare "mL" could be misread by that factor. `docs/MODEL.md`
    # § "The compartment schematic: what its heights, amounts and share bar
    # assert" sets the spelling. The wording is a placeholder, but the rule is not.
    AGENT_VAPOUR_MILLILITRES = ("millilitres of vapour", "mL vapour", "mL vapour")
    # The agent cost View shows the delivered agent in one of the next two units
    # (`PL-B396`). In millilitres of liquid, the figure is the volume of liquid agent
    # that the vaporizer turned into the delivered vapour.
    AGENT_VAPOUR_LITRES = ("litres of vapour", "L vapour", "L vapour")
    # A bottle of agent holds real liquid. So the reader's bottle volume, and
    # the price per millilitre worked out from it, are in this unit too
    # (`PL-1P15`). The field for the bottle volume names this unit, so the reader
    # is less likely to type a volume in litres or as a count of bottles
    # (`docs/MODEL.md` § "A cost at the reader's price").
    AGENT_LIQUID_MILLILITRES = ("millilitres of liquid", "mL of liquid", "mL of liquid")

    recorded: str
    label: str
    axis_title: str

    def __init__(self, recorded: str, label: str, axis_title: str) -> None:
        self.recorded = recorded
        self.label = label
        self.axis_title = axis_title
