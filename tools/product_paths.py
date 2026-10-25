"""Where the simulator's package lives, for the tools that read it.

The package's location was spelt in five tools - `agent_identity_check`,
`glyph_check`, `literal_home_check`, `doc_check` and `import_boundary_check`,
six times in the last - so a move of the package would have left each tool
reading a tree that is no longer there (`PL-H5T9`). This module is the one
home of that fact for every tool under `tools/`, which imports it rather than
typing the path again. `docket` cannot import `tools/`, so `docket.arming`
keeps its own spelling of the data tree.

Standard library only and floor-parseable, like every tool under `tools/`. It
imports nothing, so a tool can read it before anything else is on the path.
"""

from __future__ import annotations

#: The simulator package's import name.
PACKAGE = "anesthesia_sim"
#: The package's directory, relative to the repository root.
PACKAGE_DIR = f"src/{PACKAGE}"
#: The scientific core, which computes every clinical value.
CORE_DIR = f"{PACKAGE_DIR}/core"
#: The interface, which draws what the core computes.
APP_DIR = f"{PACKAGE_DIR}/app"
#: The validated parameter data the core reads.
DATA_DIR = f"{PACKAGE_DIR}/data"
#: The Workspace, Area and View layout model.
LAYOUT_DIR = f"{PACKAGE_DIR}/layout"
