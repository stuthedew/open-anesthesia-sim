---
id: PL-3SQT
title: Swap the dependencies for the Qt port: PySide6-Essentials, pyqtgraph and numpy in, flet and flet-charts out, and re-argue the 'Decided: no numpy' note on its new scope
priority: P2
effort: S
status: done
classes: infra, feature
feature: qt-port
touches: pyproject.toml, uv.lock, docs/WORKING_NOTES.md, docs/ARCHITECTURE.md, README.md, .github/workflows/drift.yml
added: 2026-09-10
closed: 2026-09-16
verify: uv run python tools/import_boundary_check.py && ! grep -qE '^\s*"flet' pyproject.toml
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

**The additive half landed with `PL-G59B`** (2026-09-14), on this item's own
rider: `PySide6-Essentials>=6.9,<7.0` and `pyqtgraph>=0.13.7,<0.15` are
declared in `pyproject.toml` and locked (pyside6-essentials 6.11.2, pyqtgraph
0.14.0, shiboken6 6.11.2, numpy 2.5.3 as pyqtgraph's own dependency), `flet`
and `flet-charts` left in place for `PL-7SVX`, and a mypy override for the
stubless pyqtgraph added beside the one for `flet_charts`. **numpy is
deliberately not declared** - nothing under `src/` imports it, and declaring
it before the re-argument this item owes would settle that question by
accident. What is left here is the subtractive half, which lands after
`PL-7SVX` has removed the last Flet import, and the numpy argument, which can
be made at any time.

**`verify:` rewritten 2026-09-14.** The command this item carried -
`grep -q 'PySide6' pyproject.toml` - started passing the moment the additive
half landed, and `docket check --verify` refused it on `PL-G59B`'s branch:
a command that passes before the work proves nothing. It now names the one
thing only the subtractive half creates, a `pyproject.toml` with no `flet`
dependency line; run and seen to fail (exit 1) with both lines still there.

**Closed 2026-09-16, and the numpy half went the other way from the title.**

*The subtractive half.* `flet` and `flet-charts` are out of `pyproject.toml`
and out of `uv.lock`, which drops **44** packages with them - `flet-cli`,
`flet-desktop`, `flet-web` and their transitive tree, `fastapi`, `uvicorn`,
`requests`, `jinja2`, `cookiecutter`, `msgpack` and `qrcode` among them,
counted from `git diff main -- uv.lock`. (The first commit's subject said 37,
from the `uv lock` console tail rather than the diff; 44 is the measured
number and this line is the record.) The three declared runtime dependencies are now
`PySide6-Essentials`, `pyqtgraph` and `pydantic`. This did **not** wait on
`PL-7SVX` as the sequencing note expected: `PL-25KS` had already deleted the
last module importing Flet, and `spikes/` - the other half of `PL-7SVX` -
never read this list, running its own toolchain through `uv run --with`. The
`verify:` command was seen to fail before the edit and pass after.

*The numpy half, which is the argument the item was written for.* The answer
is **no, numpy is not declared**, against this item's own title and the first
clause of its Done-when. The item asked for "the conclusion recorded whichever
way it goes", and this is it going the other way; the note carries the full
argument and the measurements, and the short form is three findings:

1. **There is nothing left to avoid.** pyqtgraph's metadata requires
   `numpy>=1.25.0` outright, so numpy has been installed in every environment
   since `PL-G59B` and `uv.lock` pins 2.5.3. The 2026-09-05 note's question -
   whether to *take* the dependency - no longer has a referent.
2. **numpy is already the chart's required input type.** Measured:
   `pyqtgraph.PlotCurveItem.updateData` raises
   `Plot data must be 1D ndarray.` on a tuple and converts a `list` with
   `np.array()`, so `qt_chart.py`'s `list(run.times_s)` is load-bearing. That
   conversion is 0.44-2.18% of a frame across the chart's whole width range.
3. **The one thing declaring it could lead to buys nothing.** Producing arrays
   in `app/run_series.py` so pyqtgraph could skip its conversion saves
   0.04-0.14% of a frame, and would put a mutable array where `DrawnWindow`
   holds immutable tuples. So no module under `src/` should import numpy, and
   a distribution nothing imports should not be declared: the version that
   decides what the chart draws is pyqtgraph's, which is declared, floored and
   capped.

Reversing this is one line in `pyproject.toml` plus the note's last paragraph,
which names the three things that would reopen it.

*The rest of the Done-when.* The Linux system libraries are documented in a
new `docs/ARCHITECTURE.md` § "Dependencies", measured rather than restated -
`ldd` over the wheel's own `libQt6Gui.so.6` and `platforms/libqoffscreen.so`
maps them to `libegl1`, `libgl1`, `libxkbcommon0`, `libdbus-1-3` and
`libfontconfig1` - and `README.md` § "Running it" now names the other four
beside the `libegl1` it already had. The same section carries the **LGPL
reading this item's rider asked for**: `pyside6_essentials` 6.11.2 and
`shiboken6` 6.11.2 declare `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only` and
ship no licence text in the wheel (measured - neither `dist-info` has a
`licenses` directory or a `License-File:`), this repository is Apache-2.0
with no `NOTICE`, and nothing is violated because the obligations attach on
conveying a binary and this project conveys none.

*The rider's other two survey findings are already settled elsewhere.* The
mypy override for the stubless pyqtgraph is in `pyproject.toml`, landed with
`PL-G59B`; the `flet_charts` and `msgpack` overrides the rider expected to go
dead are already gone, so there is nothing here for `warn_unused_configs` to
find and that suggestion is not taken. The `disallow_subclassing_any` question
was decided by `PL-G59B` and `PL-25KS` in the code they wrote.

*One stale statement the swap created, fixed with it.*
`.github/workflows/drift.yml`'s out-of-bounds comment used "flet 1.0" as its
example of a major bound `--upgrade` cannot cross. Flet is no longer a bound
this project declares, so the example now names ones it does.
