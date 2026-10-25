"""Tests for the build identifier the header subtitle carries.

`build_identifier` is tested against fixed git output rather than against this
checkout, deliberately. A test that read the real repository would assert
whatever happens to be true while it runs. It would pass on a clean release tag
and on a dirty branch for different reasons. It could also never exercise the
case it exists for: a release build, which the test suite never runs in.
"""

from __future__ import annotations

import importlib
import importlib.metadata
from typing import Any

import pytest

from anesthesia_sim.app_metadata import (
    APP_BUILD,
    APP_BUILD_VERSION,
    APP_VERSION,
    APP_VERSION_IS_KNOWN,
    UNKNOWN_VERSION,
    build_identifier,
)


def test_a_clean_checkout_of_the_released_tag_adds_nothing() -> None:
    """This is the shipped case, and the reason a release build returns no identifier.

    A released build has nothing useful to add: its version already names it
    exactly. Anything appended would add noise to the product to serve a
    development need.
    """

    assert build_identifier("v0.4.10", "8d46af8c", "0.4.10") is None


def test_a_commit_past_the_tag_is_named() -> None:
    """`PL-QC38` was this case: a build between two releases.

    `git describe` reports the distance from the tag and the commit. Only the
    commit is shown. The hash tells the reader which build this is, and the
    distance would cost header width without telling them anything more.
    """

    assert build_identifier("v0.4.10-3-g8d46af8c", "8d46af8c", "0.4.10") == "g8d46af8c"


def test_an_uncommitted_working_tree_says_so() -> None:
    """This is the state in which it is hardest to know which build is running.

    A dirty tree is not any commit, so naming the commit alone would overstate
    what is running.
    """

    assert build_identifier("v0.4.10-3-g8d46af8c-dirty", "8d46af8c", "0.4.10") == "g8d46af8c.dirty"


def test_a_dirty_checkout_of_the_released_tag_is_still_not_the_release() -> None:
    """`v0.4.10-dirty` is not `v0.4.10`, and must not be reported as it.

    This is the one case in which the equality test makes the whole decision.
    The describe output differs from the tag only by a suffix. Treating it as a
    release build would be exactly the false confirmation that the build
    identifier exists to prevent.
    """

    assert build_identifier("v0.4.10-dirty", "8d46af8c", "0.4.10") == "g8d46af8c.dirty"


def test_a_repository_with_no_release_tag_yet_is_named_by_its_commit() -> None:
    """The `--always` option makes git fall back to the bare hash, which is not a version string."""

    assert build_identifier("8d46af8c", "8d46af8c", "0.4.10") == "g8d46af8c"


@pytest.mark.parametrize(
    ("described", "revision"), [(None, "8d46af8c"), ("v0.4.10-3-g8d46af8c", None), (None, None)]
)
def test_a_build_git_cannot_describe_falls_back_to_the_bare_version(
    described: str | None, revision: str | None
) -> None:
    """No git, no repository, a timeout or a failed call all end up in this case.

    The result is then the bare version, which is the same string a release
    build shows. The `APP_BUILD_VERSION` docstring states this openly: a missing
    build identifier means "the release, or a build that cannot be identified".
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


def test_this_build_knows_its_own_version() -> None:
    """This pins the ordinary case, so the unknown-version sentinel cannot quietly become normal."""

    assert APP_VERSION_IS_KNOWN is True
    assert APP_VERSION != UNKNOWN_VERSION


def test_absent_package_metadata_makes_the_build_declare_itself_untraceable(
    monkeypatch: Any,
) -> None:
    """`PL-KCWD`: the fallback has to be reportable, not just survivable.

    Falling back rather than crashing on launch is the right policy, because a
    frozen or bundled build may not preserve installed-package metadata. The
    interface then needs a way to *ask* whether the running build is
    identified. The provenance line can then say that the version is not known,
    instead of showing "unknown" as though it were a version.

    The test patches `importlib.metadata.version` rather than the module's own
    imported name, and that is the whole difficulty of this test. The reload
    below re-executes `from importlib.metadata import ... version`. That import
    would overwrite a patch applied to `anesthesia_sim.app_metadata.version`,
    so the test would see the real version and give a false all-clear.
    """

    def _no_metadata(distribution_name: str) -> str:
        raise importlib.metadata.PackageNotFoundError(distribution_name)

    monkeypatch.setattr(importlib.metadata, "version", _no_metadata)

    import anesthesia_sim.app_metadata as app_metadata

    try:
        reloaded = importlib.reload(app_metadata)

        assert reloaded.APP_VERSION == reloaded.UNKNOWN_VERSION
        assert reloaded.APP_VERSION_IS_KNOWN is False
    finally:
        monkeypatch.undo()
        importlib.reload(app_metadata)
