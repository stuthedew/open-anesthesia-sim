import importlib
import importlib.metadata
import tomllib
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import Any

from anesthesia_sim import app_metadata

PYPROJECT_PATH = Path(__file__).resolve().parents[2] / "pyproject.toml"


def test_app_version_matches_pyproject_toml() -> None:
    """Regression test for APP_VERSION drifting from pyproject.toml.

    Catches the exact bug found when v0.2.0 shipped without bumping
    pyproject.toml's [project].version, leaving the running app
    displaying the prior milestone's version in its own header.
    """

    with PYPROJECT_PATH.open("rb") as stream:
        declared_version = tomllib.load(stream)["project"]["version"]

    assert app_metadata.APP_VERSION == declared_version


def test_app_version_falls_back_when_package_metadata_missing(
    monkeypatch: Any,
) -> None:
    """A frozen/bundled build without preserved package metadata must not
    crash on import; it must fall back to a visibly unknown version."""

    def raise_not_found(name: str) -> str:
        del name
        raise PackageNotFoundError

    with monkeypatch.context() as patched:
        # app_metadata re-runs `from importlib.metadata import version` on
        # reload, so the source attribute must be patched, not the name as
        # already bound in app_metadata's namespace.
        patched.setattr(importlib.metadata, "version", raise_not_found)
        importlib.reload(app_metadata)
        assert app_metadata.APP_VERSION == "unknown"

    importlib.reload(app_metadata)
    assert app_metadata.APP_VERSION != "unknown"
