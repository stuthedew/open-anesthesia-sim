---
id: PL-3SQT
title: Swap the dependencies for the Qt port: PySide6-Essentials, pyqtgraph and numpy in, flet and flet-charts out, and re-argue the 'Decided: no numpy' note on its new scope
status: untriaged
feature: qt-port
added: 2026-09-10
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
