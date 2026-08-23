from importlib.metadata import version

DISTRIBUTION_NAME = "anesthesia-sim"
APP_DISPLAY_NAME = "Working Title"
APP_AUTHOR = "Open Anesthesia Simulator contributors"
APP_VERSION = version(DISTRIBUTION_NAME)  # sourced from pyproject.toml; do not hardcode here
APP_BUNDLE_ID = "org.openanesthesia.simulator"
