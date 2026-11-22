---
id: PL-L1LP
title: docs/ARCHITECTURE.md, README.md and the CI workflow's comment say the Qt wheels need five OS packages on Linux, and the wheels also link glib, which none of the five brings
priority: P3
effort: S
status: done
classes: defect, docs
feature: interface-matches-its-spec
touches: docs/ARCHITECTURE.md, README.md, .github/workflows/quality.yml
added: 2026-11-21
closed: 2026-11-21
pr: 2200
payoff: A Linux user installing the simulator learns that glib is the sixth system package it needs
verify: grep -qF 'libglib2.0-0t64' docs/ARCHITECTURE.md
---

**Problem.** docs/ARCHITECTURE.md, README.md and the CI workflow's comment say the Qt wheels need five OS packages on Linux, and the wheels also link glib, which none of the five brings

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/ARCHITECTURE.md` § "Dependencies" says "**On Linux, the Qt wheels need shared objects from five OS packages.**" and lists `libegl1`, `libgl1`, `libxkbcommon0`, `libdbus-1-3` and `libfontconfig1`. `README.md` § "Running it" says an ordinary desktop "already has the four other system libraries that Qt links", and a comment in `.github/workflows/quality.yml` names the same four.

`readelf -d` on `PySide6/Qt/lib/libQt6Gui.so.6` of `pyside6-essentials` 6.11.2 lists these `NEEDED` entries that the wheel does not hold: `libEGL.so.1`, `libfontconfig.so.1`, `libX11.so.6`, `libglib-2.0.so.0`, `libxkbcommon.so.0`, `libGL.so.1`, `libz.so.1`, `libfreetype.so.6` and `libgthread-2.0.so.0`. On Ubuntu 24.04, `apt-cache depends --recurse --no-recommends` over the five listed packages reaches `libx11-6`, `libfreetype6` and `zlib1g`, and no glib package. `dpkg -S libglib-2.0.so.0` names `libglib2.0-0t64`.

Nobody has built a container without glib and watched the import fail, so the sixth package is measured from the links and not from a failure.

**Why it matters.** A contributor who sets up a minimal container from the document's list of five can still meet a failed import of the Qt interface.

**Done when.** A container that holds the five listed packages and no glib either imports `PySide6.QtGui` or fails, and the three places state the count that the run shows.

**Closed 2026-11-21.** Measured on Ubuntu 24.04.5 with `pyside6-essentials` 6.11.2. `readelf -d` on `libQt6Gui.so.6` lists `libglib-2.0.so.0` and `libgthread-2.0.so.0` among its needed libraries. With the glib library hidden by a bind mount of `/dev/null` in a private mount namespace (`unshare -m`), `import PySide6.QtGui` fails with "libglib-2.0.so.0: file too short", and it imports normally without the mount. `dpkg -S` puts both libraries in `libglib2.0-0t64`, which also answers to the name `libglib2.0-0`. So glib is a sixth package, and `docs/ARCHITECTURE.md` § "Dependencies", `README.md` and the comment in `.github/workflows/quality.yml` now say six. The workflow installs only `libegl1`, and the runner image already carries glib, because the suite imports `PySide6.QtGui` there, so CI changes nothing. Documents checked: `docs/ARCHITECTURE.md`, `README.md` and `.github/workflows/quality.yml`, which name the system packages, and `CONTRIBUTING.md`, which names none.

**Generator check.** One-off. The fact misread is which system libraries the PySide6 wheel loads. The count of five was written from a list rather than from the wheel's own `readelf` output, which the paragraph above now records.
