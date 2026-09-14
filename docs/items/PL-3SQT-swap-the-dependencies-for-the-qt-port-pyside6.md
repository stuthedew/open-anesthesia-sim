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

**The Qt port's Required scope, item 5.** PySide6-Essentials, pyqtgraph and numpy
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

**Rider, 2026-09-14 (pre-port survey).** pyqtgraph 0.14.0 ships no `py.typed`,
so `uv run mypy` (strict; `files` includes `src`) fails on the first
`import pyqtgraph` with `[import-untyped]`; PySide6 6.11.2 is typed. Add beside
the existing `flet_charts` and `msgpack` overrides in `pyproject.toml`:

```toml
[[tool.mypy.overrides]]
module = ["pyqtgraph", "pyqtgraph.*"]
ignore_missing_imports = true
```

with a comment that this degrades every pyqtgraph name to `Any` - the hazard
the msgpack override's comment already describes and `tools/ignore_check.py`
polices. The `flet_charts` and `msgpack` overrides go dead when `PL-7SVX`
deletes their importers; `warn_unused_configs = true` under `[tool.mypy]`
would make the next dead override loud, since `strict` does not enable it.

**Two more, same survey.** mypy `--strict` rejects pyqtgraph a second time
even with the `ignore_missing_imports` override: `disallow_subclassing_any`
refuses the two `pyqtgraph` subclasses the spike is built on, since their
bases have become `Any`. Each such class needs `# type: ignore[misc]` with
the reason, or a minimal local stub - decide which here, once, before
`PL-G59B` writes the first one. And licensing: PySide6-Essentials and
shiboken6 are LGPLv3 (GPL-only for some modules) and ship no licence text in
the wheel; this repository is Apache-2.0 with no `NOTICE`. Nothing is
violated today - the obligations (dynamic linking, a recipient's ability to
relink, conveying the LGPL text) attach when a binary is *conveyed*, and this
project ships none, `uv` installing from PyPI per user. Record that reading
in `docs/ARCHITECTURE.md` when the dependency lands, so the day a bundled
build is proposed the obligation is already written down.
