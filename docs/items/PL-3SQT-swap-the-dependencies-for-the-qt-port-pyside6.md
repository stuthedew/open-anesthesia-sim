---
id: PL-3SQT
title: Swap the dependencies for the Qt port: PySide6-Essentials, pyqtgraph and numpy in, flet and flet-charts out, and re-argue the 'Decided: no numpy' note on its new scope
priority: P2
effort: S
status: ready
classes: infra, feature
feature: qt-port
touches: pyproject.toml, uv.lock, docs/WORKING_NOTES.md
added: 2026-09-10
verify: uv run python tools/import_boundary_check.py && grep -q 'PySide6' pyproject.toml
---

**Problem.** Swap the dependencies for the Qt port: PySide6-Essentials, pyqtgraph and numpy in, flet and flet-charts out, and re-argue the 'Decided: no numpy' note on its new scope

**`v0.5.1`'s Required scope, item 5.** PySide6-Essentials, pyqtgraph and numpy
enter; `flet` and `flet-charts` leave.

**numpy is the part that needs an argument rather than an edit.**
`docs/WORKING_NOTES.md` § "Decided: no numpy" (2026-09-05) concluded no, and
its reasoning was *fit*: numpy has no append, so it would have made
`RunHistory`'s compaction harder. `RunHistory` no longer exists (`PL-2FM6`),
and numpy arriving underneath a plotting library is a different proposition
from numpy as a storage choice. So that note is re-argued on its new scope
rather than cited either way, and the conclusion recorded whichever way it goes.

**Sizes, from `PL-QXSB`**: PySide6-Essentials 233 MB, numpy 33 MB, pyqtgraph
7.7 MB, against flet 5.5 MB and flet_web 73 MB. About 3.5x, trimmable in a
packaged build that ships selected Qt modules, and real for a download.

**The spike's own dependency handling is not the answer here.** It uses
`uv run --with` deliberately so that nothing reaches `pyproject.toml`; this item
is the opposite - the real declaration, the lockfile, and the Linux system
libraries the wheels do not carry (`libegl1 libgl1 libxkbcommon0 libdbus-1-3
libfontconfig1`).

**Why it matters.** It is the declaration that makes the port real, and it
carries one question that is an argument rather than an edit.
`docs/WORKING_NOTES.md` § "Decided: no numpy" (2026-09-05) concluded no, and its
reasoning was *fit*: numpy has no append, so it would have complicated
`RunHistory`'s compaction. `RunHistory` no longer exists (`PL-2FM6`), and numpy
arriving underneath a plotting library is a different proposition from numpy as
a storage choice. Citing that note either way without re-arguing it would be
carrying a conclusion past the premise it rested on.

The size is real and worth stating rather than discovering: PySide6-Essentials
233 MB, numpy 33 MB, pyqtgraph 7.7 MB against flet 5.5 MB and flet_web 73 MB -
about 3.5x, trimmable in a packaged build that ships selected Qt modules.

**Done when.** `pyproject.toml` and `uv.lock` declare PySide6-Essentials,
pyqtgraph and numpy and no longer declare `flet` or `flet-charts`; the Linux
system libraries the wheels do not carry are documented (`libegl1 libgl1
libxkbcommon0 libdbus-1-3 libfontconfig1`); and the "Decided: no numpy" note is
re-argued on its new scope with the conclusion recorded whichever way it goes.

**Sequencing.** Removing `flet` cannot land before `PL-7SVX`, which is what
deletes the last import; splitting this item's two halves across the milestone
is expected.
