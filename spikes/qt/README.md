# Qt spike — `PL-55DH`

A disposable experiment, not a port. It draws the shipped concentration chart
and readout row behind the *existing* `SimulationController`, so that `PL-X9T3`
has something to run on the project owner's own machine and measure the one
term no session in the web container can: **paint cost on real hardware, and
whether it looks the way it is meant to.**

Nothing under `src/anesthesia_sim/` imports this tree. Deleting the whole
experiment is one command:

```bash
rm -rf spikes/
```

## Running it

Its dependencies are deliberately not in `pyproject.toml`. `uv run --with`
layers them over the project environment for one command and writes nothing:

```bash
PYTHONPATH=spikes/qt uv run --with PySide6-Essentials --with pyqtgraph --with numpy \
  python spikes/qt/qt_spike.py
```

`PYTHONPATH=spikes/qt` is what lets `qt_spike.py` find `chart_sources.py` and
`frame_timing.py` beside it. On Linux, Qt also needs system libraries the
wheels do not carry; on a bare Ubuntu container that is
`apt-get install -y libegl1 libgl1 libxkbcommon0 libdbus-1-3 libfontconfig1`.
macOS and Windows need nothing extra.

Two non-interactive modes, both of which run headless — set
`QT_QPA_PLATFORM=offscreen` where there is no display:

```bash
# Advance a real case, draw real frames, assert what the chart drew. Exit 1 on a mismatch.
python spikes/qt/qt_spike.py --self-check --seconds 1800 --rate 300

# Write one frame of a short run, with a dial change in it, to a PNG.
python spikes/qt/qt_spike.py --screenshot /tmp/spike.png
```

`--opengl` draws the curves through OpenGL instead of the raster painter. It
is a paint-cost lever rather than a preference, so it is worth reading the
instrument panel both ways.

## What is on screen, and what it is for

The **instrument panel** at the bottom is the point of the spike. It reports
five stages over the last 120 frames, and the first three are `PL-YSZN`'s
split on Flet so the two measurements can be set beside each other:

| Stage | What it is | Flet counterpart |
| --- | --- | --- |
| `advance` | the run's steps for this tick | `controller.advance` |
| `refresh` | reading the run and formatting the frame | `_refresh_view` |
| `handoff` | telling the toolkit the frame changed | `page.update()` |
| `paint` | this widget's own `paintEvent` | none — Flet renders out of process |
| `timer lateness` | how long a callback ready to run waited | Flet's input delay |

`paint` is CPU work **in this process only**: the compositor's share and the
GPU's are outside it and outside this measurement. In a container with no GPU
it is an offscreen software rasteriser and means nothing at all — `PL-QXSB`
measured 18–28 ms there *including for a frame where nothing changed*. A stage
with no samples prints `not measured` rather than `0.00 ms`, because a zero
reads as a stage that is free.

The **`Columns` control** is the successor to `PL-QXSB`'s "Qt would make
decimation optional". With `PL-2FM6` landed there is no decimation left to
drop, so the question is whether the column budget can be *raised*:
`CHART_COLUMN_BUDGET_PER_SERIES` is 150 because Flet charges ~24.5 µs per
point control per frame whether or not the point moved, and nothing in the
model or in a reader's eye chose that number.

## What it deliberately is not

Out of scope, per the item: the agent selector, the wash-in plot, the control
marks, the new-case dialog, the notice banner, and theming beyond enough
colour and dash to tell six traces apart. Missing pieces are missing on
purpose — the question is frame cost and feel, not completeness.

It is also **not a medical device and not the shipped interface**, which the
banner says permanently rather than on a timer. The values are the real
model's, so a reader arriving from a screenshot has no other way to know.

## What it borrows, and the two things it copies

Every number on screen goes through the shipped modules, which is what makes
the frame the application's frame rather than a lookalike: `app/formatting.py`
for every displayed value and every hedged label, `app/chart_time_base.py` for
the window ladder and the axis ruling, `app/playback.py` for the rate ladder,
`app/chart_series.py` for the column budget, `core/supported_ranges.py` for
the slider bounds, and `core/uptake_system.py` for the step size.

Two copies are kept knowingly, and they are declared where they live rather
than left for a reader to find:

- **The six trace colours and dash patterns** (`chart_sources.TRACES`).
  `app/theme.py` holds no Flet and could have been imported, but the dash
  patterns are written inline in `app/simulation_view.py`, which does — and
  importing that would load the toolkit this spike exists to be compared
  against. `PL-2CS8` consolidated every display token into `theme.py` so that
  nothing *shipped* keeps a second copy; this tree is disposable and says
  that it copied.
- **The render cadence** (`RENDER_INTERVAL_S`), for the same reason. The
  simulation step is taken from `core.uptake_system.MAXIMUM_SIMULATION_STEP_S`
  instead of copied, because the shipped step sits at that ceiling
  deliberately.

## What it is checked by, and what it is not

There is no test under `tests/`. A test of a throwaway tree is a shipped asset
for something meant to be deleted, and `pytest`'s `testpaths` does not reach
here. `--self-check` is the substitute: it advances a real case at a real
playback rate, draws real frames through the real render path, and asserts
that every trace's newest drawn point agrees with the readout printed beneath
it. A swapped compartment, a missing factor of a hundred, or a chart drawn
from a stale window each fail it.

The spike is outside the `mypy` gate as well — `pyproject.toml`'s `files` does
not list it, and adding it would put PySide6 stubs into the project's dev
environment for a tree that is going away. It is inside `ruff`'s, because that
runs over the repository root.
