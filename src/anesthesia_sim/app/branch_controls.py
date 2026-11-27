"""The words on the controls that open a branch.

The Branch View draws these controls, and the controller's refusals name
them, so a user whose press is refused is told which control to use
instead. Both read the words from here (`PL-3JTH`). The controller cannot
read them from `dashboard_frame.py`, which imports the controller. This
module imports nothing, so either can read it.
"""

from typing import Final

__all__ = ["FORK_POINT_LABEL", "HERE_FORK_NAME", "TAKE_FORK_LABEL"]

#: The label of the list of instants a branch can open at. "From" labels the
#: instant at which the branch opens.
FORK_POINT_LABEL: Final = "From"

# The label is "Branch", not "Branch here" (`PL-Y2SL`). On the button below,
# "here" names where the paused trunk stands, while this button branches at
# the point that "From" names. Two adjacent buttons whose labels start with
# the same words but do different things invite the wrong press. A branch
# taken at the wrong instant can then be ended only with the trunk's Reset,
# because only one comparison is allowed at a time.
TAKE_FORK_LABEL: Final = "Branch"

#: The words that open the label of the button that branches where the paused
#: trunk stands. `dashboard_frame.HERE_FORK_LABEL_TEMPLATE` adds the instant.
HERE_FORK_NAME: Final = "Branch here"
