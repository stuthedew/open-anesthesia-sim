---
id: PL-VHLZ
title: Nothing installs libegl1, so a fresh web container or CI runner dies on the first PySide6.QtGui import; quality.yml has no apt step and the environment setup script has no such line
status: untriaged
added: 2026-09-14
---

**Problem.** Nothing installs libegl1, so a fresh web container or CI runner dies on the first PySide6.QtGui import; quality.yml has no apt step and the environment setup script has no such line

**Found 2026-09-14** by the pre-port survey, and it contaminated a claim this
session had already made. `spikes/qt/qt_spike.py --screenshot` rendered here
at 18:39; `/var/log/apt/history.log` shows `apt-get install -y libegl1` at
18:37:44, run by a survey subagent two minutes earlier. Before that install,
`uv run --with PySide6-Essentials python -c "import PySide6.QtGui"` fails with
`ImportError: libEGL.so.1: cannot open shared object file`. `ldconfig -p`
carries `libGL.so.1`, `libxkbcommon.so.0` and `libdbus-1.so.3` already; the
only missing library is `libEGL`, and the only `libEGL.so` on disk belongs to
the bundled Playwright Chromium.

**Why it matters.** `ROADMAP.md` § "the interface moves to Qt" moved the port
ahead of v0.5.0 partly because the spike "already renders offscreen in that
same container" - true only after a package nothing in this repository or the
environment installs. `PL-YCWZ` (headless rendering tests over the real Qt
interface) is what the port's schedule rests on, and `.github/workflows/quality.yml`
has no `apt` step at all, so its first PySide6 import dies at collection.
`spikes/qt/README.md` names the line for "a bare Ubuntu container"; nothing
runs it.

**Three places, each its own line, and none of them a hook:**

1. **CI** - `.github/workflows/quality.yml`, a step after `actions/checkout`
   and before `astral-sh/setup-uv` (the floor section's design is that no
   toolchain is installed above it):

   ```yaml
   - name: Qt's system libraries, for the offscreen platform plugin
     run: sudo apt-get update && sudo apt-get install -y libegl1
   ```

   `libgl1` is already present on `ubuntu-latest`; `libegl1` is not.
2. **The web environment** - the project owner's, outside this repository.
   Per https://code.claude.com/docs/en/cloud-environments § "Setup scripts"
   (read 2026-09-14): "Scripts run as root on Ubuntu 24.04, so `apt install`
   and most language package managers work", the field is **Setup script** in
   the environment settings dialog at claude.ai/code, and `archive.ubuntu.com`
   is on the default **Trusted** allowlist. The snapshot is cached for roughly
   seven days and rebuilt when the script changes, so the install is paid
   once. The line, with the `|| true` the same page prescribes for
   non-critical installs:

   ```bash
   apt update && apt install -y libegl1 || true
   ```

   A `SessionStart` hook is the wrong carrier: the same page routes VM
   provisioning to the setup script and project setup to hooks, and a hook
   would re-run `apt` on every resume.
3. **`spikes/qt/README.md`** already carries the line, and `PL-7SVX` deletes
   the spike; the durable home for "what the Qt build needs from the OS" is
   `docs/ARCHITECTURE.md`, which `PL-25KS`'s definition of done rewrites.

**Done when** `quality.yml` installs `libegl1` before `setup-uv`, the owner's
environment setup script carries the line (recorded here as done by them, since
no file in this tree can prove it), and `PL-YCWZ`'s first rendering test passes
in CI on a runner that never had the library.

**The environment half is done** (project owner, 2026-09-14): the setup-script
line above was added to the cloud environment after `#576` merged. Recorded
here as done by them, as "Done when" provides, since no file in this tree can
prove it; the first fresh session in that environment that imports
`PySide6.QtGui` without an `apt` step is the proof. What remains is the CI
step in `quality.yml`, which rides whichever session takes this item.

**The CI half rode `PL-G59B`** (2026-09-14): the chart port's first commit adds
the `libegl1` step to `.github/workflows/quality.yml`, between `checkout` and
the floor section, because that commit is also the one that puts the first
`PySide6.QtGui` import into the suite and the two cannot land apart. The
environment proof named above was observed the same day: this container's
`/usr/lib/x86_64-linux-gnu/` carried `libEGL.so.1` at session start with no
`apt` step run, and `uv run --with PySide6-Essentials python -c "import
PySide6.QtGui"` succeeded. What this item still owes is the third place, the
OS-requirement line in `docs/ARCHITECTURE.md`, and the observation of the CI
step passing on a runner that never had the library, which the chart port's
own pull request supplies.
