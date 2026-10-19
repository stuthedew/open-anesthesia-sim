"""Unit tests for `layout/run_identity.py`: what a run is called by, wherever it is drawn.

`PL-7Z84`: a run's identity is the session that placed it and its number in
that session. These hold the two properties a pin rests on: no number is given
out twice in a session, and a run from another session is never the same run,
whatever its number.
"""

import pytest

from anesthesia_sim.layout.exceptions import InvalidLayout
from anesthesia_sim.layout.run_identity import RunId, RunIdentities, SessionToken

SESSION = SessionToken("0123456789abcdef0123456789abcdef")
LATER = SessionToken("fedcba9876543210fedcba9876543210")


class TestSessionToken:
    def test_a_token_is_32_lowercase_hexadecimal_digits(self) -> None:
        assert SESSION == "0123456789abcdef0123456789abcdef"

    @pytest.mark.parametrize(
        "token",
        ["", "0" * 31, "0" * 33, "0123456789ABCDEF0123456789ABCDEF", "g" * 32, " " + "0" * 31],
    )
    def test_anything_else_is_refused(self, token: str) -> None:
        with pytest.raises(InvalidLayout, match="32 lowercase hexadecimal digits"):
            SessionToken(token)

    def test_a_token_is_a_str(self) -> None:
        with pytest.raises(TypeError, match="a session token is a str, not int"):
            SessionToken(5)  # type: ignore[arg-type]

    def test_a_drawn_token_is_one_and_two_draws_differ(self) -> None:
        first = SessionToken.drawn()
        second = SessionToken.drawn()

        assert isinstance(first, SessionToken)
        assert first != second


class TestRunId:
    def test_two_identities_are_one_run_only_where_session_and_number_are_both_equal(self) -> None:
        assert RunId(SESSION, 2) == RunId(SESSION, 2)
        assert RunId(SESSION, 2) != RunId(SESSION, 3)
        assert RunId(SESSION, 2) != RunId(LATER, 2)

    @pytest.mark.parametrize("number", [0, -1])
    def test_runs_are_numbered_from_one(self, number: int) -> None:
        with pytest.raises(InvalidLayout, match=f"runs are numbered from 1, not {number}"):
            RunId(SESSION, number)

    def test_each_field_is_of_its_type(self) -> None:
        with pytest.raises(TypeError, match="session is a SessionToken, not str"):
            RunId("0" * 32, 1)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="a run's number is an int, not bool"):
            RunId(SESSION, True)

        with pytest.raises(TypeError, match="a run's number is an int, not float"):
            RunId(SESSION, 1.0)  # type: ignore[arg-type]


class TestRunIdentities:
    def test_runs_are_numbered_in_the_order_they_are_placed_and_no_number_twice(self) -> None:
        identities = RunIdentities(SESSION)

        minted = [identities.mint() for _ in range(3)]

        assert minted == [RunId(SESSION, 1), RunId(SESSION, 2), RunId(SESSION, 3)]

    def test_a_session_given_no_token_draws_its_own(self) -> None:
        first = RunIdentities()
        second = RunIdentities()

        assert first.session != second.session
        assert first.mint() != second.mint()

    def test_the_session_is_a_session_token(self) -> None:
        with pytest.raises(TypeError, match="a session is a SessionToken or None, not str"):
            RunIdentities("0" * 32)  # type: ignore[arg-type]
