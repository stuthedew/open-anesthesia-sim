"""Where the simulator's package lives, for the tools that read it.

The package's location was spelt in five tools - `agent_identity_check`,
`glyph_check`, `literal_home_check`, `doc_check` and `import_boundary_check`,
six times in the last - so a move of the package would have left each tool
reading a tree that is no longer there (`PL-H5T9`). This module is the one
home of that fact for every tool under `tools/`, which imports it rather than
typing the path again.

The package's import name already has a home, `docket.arming.PRODUCT_PACKAGE`,
which the merge gate reads to tell a simulator test from a tooling test. This
module reads it from there rather than typing it a second time. `docket`
cannot import `tools/`, so the gate's own path tuples spell the data tree in
`docket.arming`.

Standard library and `docket` only, and floor-parseable, like every tool under
`tools/`.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "subprojects" / "docket" / "src"))

from docket.arming import PRODUCT_PACKAGE

#: The simulator package's import name.
PACKAGE = PRODUCT_PACKAGE
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
