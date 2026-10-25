"""How a run is identified, independently of where it is drawn.

A run used to be named by its position in the dashboard's drawing order, so
"the second run" meant whichever run was second at the time (`PL-7Z84`). A
Workspace that pins a run (`PL-WV9K` Q6) would then point at whatever run took
that place, and show it as the run it remembers. The reader would see the
correct number under the wrong patient context, which `docs/MODEL.md` § "What
this list requires once the layout is the reader's" treats as a display
failure.

**A `RunId` is a session and a number.** The session is the application
session that minted the identity, a random token drawn once when that session
starts. The number counts the runs that session has placed, from 1, and no
number is given out twice. So a run in a later session that is numbered the
same is a different run, and a branch taken after an earlier one was dropped
gets a new number rather than the dropped branch's. The number is also what
the run is called on screen: `dashboard_frame.run_label` renders it.

**A run keeps its identity for as long as it keeps its place on screen.** The
trunk keeps it from the dashboard's construction onward. A branch keeps it from
the fork that opened it until the branch is dropped. A Reset of the run, or a
change of agent, begins a new run definition in the same place, after the
confirmation that `docs/MODEL.md` § "Agent-change behavior" requires. The run
keeps its identity through both.

`RunIdentities` is the one object in this package whose state changes, because
it is the session's counter. Everything else here is an immutable value.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import Final

from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.layout.exceptions import InvalidLayout

__all__ = ["RunId", "RunIdentities", "SessionToken"]

# A session token is a version 4 UUID written as 32 lowercase hexadecimal
# digits, the form `uuid.UUID.hex` gives.
_SESSION_TOKEN: Final = re.compile(r"[0-9a-f]{32}")


class SessionToken(str):
    """The token of the application session that minted a run identity, checked when built.

    Raises:
        TypeError: the token is not a `str`.
        InvalidLayout: the token is not 32 lowercase hexadecimal digits.
    """

    __slots__ = ()

    def __new__(cls, token: str) -> SessionToken:
        if not isinstance(token, str):
            raise TypeError(f"a session token is a str, not {type(token).__name__}")

        if _SESSION_TOKEN.fullmatch(token) is None:
            raise InvalidLayout(
                f"a session token is 32 lowercase hexadecimal digits, not {token!r}"
            )

        return super().__new__(cls, token)

    @classmethod
    def drawn(cls) -> SessionToken:
        """Return a new random token for a session that starts now."""

        return cls(uuid.uuid4().hex)


@dataclass(frozen=True, slots=True)
class RunId:
    """One run's identity: the session that placed it, and its number in that session.

    Two identities are the same run only where both fields are equal.

    Raises:
        TypeError: `session` is not a `SessionToken`, or `number` is not an
            `int` (a `bool` is refused).
        InvalidLayout: `number` is less than 1.
    """

    session: SessionToken
    number: int

    def __post_init__(self) -> None:
        if not isinstance(self.session, SessionToken):
            raise TypeError(
                f"a run identity's session is a SessionToken, not {type(self.session).__name__}"
            )

        if isinstance(self.number, bool) or not isinstance(self.number, int):
            raise TypeError(f"a run's number is an int, not {type(self.number).__name__}")

        if self.number < 1:
            raise InvalidLayout(f"runs are numbered from 1, not {shown(self.number)}")


class RunIdentities:
    """The identities one application session gives its runs, in the order it places them.

    Args:
        session: The session's token. When none is given, a new random token
            is drawn. A test passes its own token so that it knows the
            identities in advance.

    Raises:
        TypeError: `session` is neither `None` nor a `SessionToken`.
    """

    __slots__ = ("_last", "_session")

    def __init__(self, session: SessionToken | None = None) -> None:
        if session is not None and not isinstance(session, SessionToken):
            raise TypeError(f"a session is a SessionToken or None, not {type(session).__name__}")

        self._session = SessionToken.drawn() if session is None else session
        self._last = 0

    @property
    def session(self) -> SessionToken:
        return self._session

    def mint(self) -> RunId:
        """Return the identity for the next run this session places, one more than the last."""

        self._last += 1

        return RunId(self._session, self._last)
