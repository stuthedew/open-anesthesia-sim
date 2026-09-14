"""Settings every test tree needs before a single test module is imported.

`QT_QPA_PLATFORM`: unset, Qt picks `xcb` on Linux and `QApplication` aborts
the process when no display is attached - which is every CI runner and every
web-container session. `offscreen` is the platform plugin the Qt build's
tests render under, so it is set here, before any `PySide6` import, rather
than on the pytest command line: `tools/doc_check.py`'s `check_coverage_gate`
holds the `Makefile`'s pytest line and `quality.yml`'s to string equality, and
an environment prefix on either would break that comparison for a reason
unrelated to coverage (`PL-YCWZ`'s pre-port survey, 2026-09-14).

`setdefault`, not assignment: a developer running the suite on a desktop with
a display may set the variable themselves to watch a test render, and nothing
here should override that.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
