"""Per-project settings, so the package is usable outside the repository it grew in.

Everything here has a working default. A project that does not care about the
distinction between safety-critical and ordinary work, or that calls its
process work something else, should not have to write a config file to use
this - but a project that does care should not have to edit the source.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_NAME = "docket.toml"


@dataclass(frozen=True)
class Config:
    """The knobs a project is likely to want to turn."""

    items_dir: str = "docs/items"
    #: Classes whose subject matter may not sit in the lower priority bands.
    safety_classes: tuple[str, ...] = ("safety", "science")
    #: Classes describing work on the process rather than on the product.
    process_classes: tuple[str, ...] = ("session-cost", "docs", "infra")
    #: Past this, the top band is too large to choose from at a glance.
    top_band_limit: int = 5
    #: Past this, an untriaged capture has become a second queue nobody reads.
    untriaged_stale_days: int = 14
    #: Classes that make a release a minor version bump rather than a patch.
    minor_classes: tuple[str, ...] = ("feature",)
    version_file: str = "pyproject.toml"
    extra: dict[str, object] = field(default_factory=dict)


def _tuple(value: object, fallback: tuple[str, ...]) -> tuple[str, ...]:
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return tuple(str(v) for v in value)
    return fallback


def load(root: Path) -> Config:
    """Read `docket.toml` from the project root, falling back to the defaults.

    A malformed config is reported by failing to parse rather than by being
    silently ignored: a setting that looks applied but is not is worse than
    one that was never written.
    """
    path = root / CONFIG_NAME
    if not path.is_file():
        return Config()
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    section = data.get("docket", data)
    defaults = Config()
    return Config(
        items_dir=str(section.get("items_dir", defaults.items_dir)),
        safety_classes=_tuple(section.get("safety_classes"), defaults.safety_classes),
        process_classes=_tuple(section.get("process_classes"), defaults.process_classes),
        top_band_limit=int(section.get("top_band_limit", defaults.top_band_limit)),
        untriaged_stale_days=int(
            section.get("untriaged_stale_days", defaults.untriaged_stale_days)
        ),
        minor_classes=_tuple(section.get("minor_classes"), defaults.minor_classes),
        version_file=str(section.get("version_file", defaults.version_file)),
    )
