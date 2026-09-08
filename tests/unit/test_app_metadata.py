"""Tests for the build identifier the header subtitle carries.

`build_identifier` is tested against fixed git output rather than against this
checkout, deliberately. A test that read the real repository would assert
whatever happens to be true while it runs - it would pass on a clean release
tag and on a dirty branch for different reasons, and it could never exercise
the case it exists for, which is the release build the test suite is never in.
"""

from __future__ import annotations

import pytest

from anesthesia_sim.app_metadata import APP_BUILD, APP_BUILD_VERSION, APP_VERSION, build_identifier


def test_a_clean_checkout_of_the_released_tag_adds_nothing() -> None:
    """The shipped case, and the reason absence has to be the release's answer.

    A released build has nothing useful to add: its version already names it
    exactly. Anything appended here would be noise on the product to serve a
    development need.
    """

    assert build_identifier("v0.4.10", "8d46af8c", "0.4.10") is None


def test_a_commit_past_the_tag_is_named() -> None:
    """The case `PL-QC38` was: a build between two releases.

    `git describe` reports the distance and the commit; only the commit is
    shown, because "which build is this" is answered by the hash and the
    distance would cost header width without adding an answer.
    """

    assert build_identifier("v0.4.10-3-g8d46af8c", "8d46af8c", "0.4.10") == "g8d46af8c"


def test_an_uncommitted_working_tree_says_so() -> None:
    """The state where "which build is this" is least knowable.

    A dirty tree is not any commit, so naming the commit alone would overstate
    what is running.
    """

    assert build_identifier("v0.4.10-3-g8d46af8c-dirty", "8d46af8c", "0.4.10") == "g8d46af8c.dirty"


def test_a_dirty_checkout_of_the_released_tag_is_still_not_the_release() -> None:
    """`v0.4.10-dirty` is not `v0.4.10`, and must not be reported as it.

    The one case where the equality test carries the whole decision: the
    describe output differs from the tag by a suffix, and treating it as a
    release build would be the exact false confirmation this item exists to
    prevent.
    """

    assert build_identifier("v0.4.10-dirty", "8d46af8c", "0.4.10") == "g8d46af8c.dirty"


def test_a_repository_with_no_release_tag_yet_is_named_by_its_commit() -> None:
    """`--always` falls back to the bare hash, which is not any version string."""

    assert build_identifier("8d46af8c", "8d46af8c", "0.4.10") == "g8d46af8c"


@pytest.mark.parametrize(
    ("described", "revision"), [(None, "8d46af8c"), ("v0.4.10-3-g8d46af8c", None), (None, None)]
)
def test_a_build_git_cannot_describe_falls_back_to_the_bare_version(
    described: str | None, revision: str | None
) -> None:
    """No git, no repository, a timeout or a failed call all land here.

    The bare version is then the same string a release build shows, which the
    `APP_BUILD_VERSION` docstring states rather than hides: its absence means
    "the release, or a build that cannot be identified".
    """

    assert build_identifier(described, revision, "0.4.10") is None


def test_the_installed_version_is_never_silently_dropped() -> None:
    """Whatever the build turns out to be, the version still leads it.

    `CLAUDE.md` requires a displayed value to be traceable to the model and
    version that produced it. The build identifier is additional provenance
    and must not replace the version it qualifies.
    """

    assert APP_BUILD_VERSION.startswith(APP_VERSION)
    if APP_BUILD is not None:
        assert APP_BUILD_VERSION == f"{APP_VERSION}+{APP_BUILD}"
