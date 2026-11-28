"""Unit tests for `AreaName` in `app/view_contract.py`: what a screen reader calls an Area.

An Area is named by its View's title, and numbered from 1 where another Area
shows the same kind of View (`PL-XV64`). Each refusal's whole message is
written out here, so a refusal that names the wrong value fails.
"""

import pytest

from anesthesia_sim.app.view_contract import AreaName


def test_an_area_s_name_is_its_view_s_title_and_its_number_among_areas_of_that_kind() -> None:
    """A lone Area is named by its title, and a numbered one adds its number, counted from 1."""

    assert AreaName("Wash-in").text == "Wash-in"
    assert AreaName("Wash-in").among_copies is None
    assert AreaName("Wash-in", 1).text == "Wash-in 1"
    assert AreaName("Wash-in", 1).among_copies == "Wash-in 1"
    assert AreaName("Wash-in", 2).text == "Wash-in 2"


@pytest.mark.parametrize("number", [0, -1])
def test_an_area_s_number_below_one_is_refused(number: int) -> None:
    with pytest.raises(ValueError) as refused:
        AreaName("Wash-in", number)

    assert str(refused.value) == f"an Area's number counts from 1, and {number} was given"


@pytest.mark.parametrize(("number", "kind"), [(True, "bool"), (1.5, "float"), ("2", "str")])
def test_an_area_s_number_that_is_not_an_int_is_refused(number: object, kind: str) -> None:
    """A bool is refused although Python counts it as an int, because True would read as 1."""

    with pytest.raises(TypeError) as refused:
        AreaName("Wash-in", number)  # type: ignore[arg-type]

    assert str(refused.value) == f"an Area's number is an int, not {kind}"


def test_an_area_s_name_without_a_title_is_refused() -> None:
    with pytest.raises(ValueError) as refused:
        AreaName("")

    assert str(refused.value) == (
        "an Area's name needs its View's title, and the title given is empty"
    )
