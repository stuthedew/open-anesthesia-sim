"""App identity/version constants, read from installed package metadata."""

from importlib.metadata import PackageNotFoundError, version

DISTRIBUTION_NAME = "anesthesia-sim"
APP_DISPLAY_NAME = "Working Title"
APP_AUTHOR = "Open Anesthesia Simulator contributors"

try:
    # Sourced from pyproject.toml; do not hardcode here.
    APP_VERSION = version(DISTRIBUTION_NAME)
except PackageNotFoundError:
    # A frozen/bundled build (see ROADMAP.md item 24) may not preserve
    # installed-package metadata; fail visibly rather than crash on launch.
    APP_VERSION = "unknown"

APP_BUNDLE_ID = "org.openanesthesia.simulator"
