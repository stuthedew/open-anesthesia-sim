---
id: PL-L1LP
title: docs/ARCHITECTURE.md, README.md and the CI workflow's comment say the Qt wheels need five OS packages on Linux, and the wheels also link glib, which none of the five brings
status: untriaged
feature: interface-matches-its-spec
added: 2026-11-21
---

**Problem.** docs/ARCHITECTURE.md, README.md and the CI workflow's comment say the Qt wheels need five OS packages on Linux, and the wheels also link glib, which none of the five brings

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/ARCHITECTURE.md` § "Dependencies" says "**On Linux, the Qt wheels need shared objects from five OS packages.**" and lists `libegl1`, `libgl1`, `libxkbcommon0`, `libdbus-1-3` and `libfontconfig1`. `README.md` § "Running it" says an ordinary desktop "already has the four other system libraries that Qt links", and a comment in `.github/workflows/quality.yml` names the same four.

`readelf -d` on `PySide6/Qt/lib/libQt6Gui.so.6` of `pyside6-essentials` 6.11.2 lists these `NEEDED` entries that the wheel does not hold: `libEGL.so.1`, `libfontconfig.so.1`, `libX11.so.6`, `libglib-2.0.so.0`, `libxkbcommon.so.0`, `libGL.so.1`, `libz.so.1`, `libfreetype.so.6` and `libgthread-2.0.so.0`. On Ubuntu 24.04, `apt-cache depends --recurse --no-recommends` over the five listed packages reaches `libx11-6`, `libfreetype6` and `zlib1g`, and no glib package. `dpkg -S libglib-2.0.so.0` names `libglib2.0-0t64`.

Nobody has built a container without glib and watched the import fail, so the sixth package is measured from the links and not from a failure.

**Why it matters.** A contributor who sets up a minimal container from the document's list of five can still meet a failed import of the Qt interface.

**Done when.** A container that holds the five listed packages and no glib either imports `PySide6.QtGui` or fails, and the three places state the count that the run shows.
