"""Entry point, so `python -m docket` works from a bare checkout.

The interpreter is checked before anything else is imported, because this is
the one place that can still speak under a `python3` below the floor. Left to
the imports, 3.10 fails on `cli`'s `from datetime import UTC` with a traceback
naming a module in this package, which reads as a defect here rather than as a
statement about the interpreter (`PL-LKGW`).
"""

import sys

#: The oldest Python this package runs under: `requires-python` in
#: `subprojects/docket/pyproject.toml`, which `tests/test_portability.py` holds
#: this to. Stated here rather than read from there, because reading TOML takes
#: `tomllib`, which is itself 3.11. Compared through this name and never as a
#: literal: under this package's py311 target, ruff's UP036 reads
#: `sys.version_info < (3, 11)` as an outdated version block, and the fix it
#: offers deletes the check.
FLOOR = (3, 11)


def run() -> int:
    """Refuse an interpreter below `FLOOR` in one line, then run the command.

    `cli` is imported here, after the check, since importing it is what fails
    below the floor.
    """
    if sys.version_info[:2] < FLOOR:
        found = ".".join(str(part) for part in sys.version_info[:3])
        raise SystemExit(
            f"docket needs Python {FLOOR[0]}.{FLOOR[1]} or newer; "
            f"this is Python {found}, at {sys.executable}"
        )
    from .cli import main

    return main()


raise SystemExit(run())
