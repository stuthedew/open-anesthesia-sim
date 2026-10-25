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
"""

from enum import Enum

__all__ = ["DisplayUnit"]


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

    recorded: str
    label: str
    axis_title: str

    def __init__(self, recorded: str, label: str, axis_title: str) -> None:
        self.recorded = recorded
        self.label = label
        self.axis_title = axis_title
