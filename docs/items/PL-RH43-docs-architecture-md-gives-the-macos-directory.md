---
id: PL-RH43
title: docs/ARCHITECTURE.md gives the macOS directory of the saved Workspaces as ~/Library/Application Support/<App>, which nobody has run on a Mac, and on Linux Qt adds the organization name
status: untriaged
feature: interface-matches-its-spec
added: 2026-11-21
---

**Problem.** docs/ARCHITECTURE.md gives the macOS directory of the saved Workspaces as ~/Library/Application Support/\<App>, which nobody has run on a Mac, and on Linux Qt adds the organization name

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/ARCHITECTURE.md` § "Where the saved Workspaces live" says "On macOS the directory is `~/Library/Application Support/<App>`." This check corrected the Linux path in the same paragraph to `~/.local/share/<Org>/<App>`, after Qt printed `<HOME>/.local/share/OpenAnesthesia/Open Anesthesia Simulator` there. The macOS path has the shape that the wrong Linux path had, and no session can run it. The comment on `APP_ORGANIZATION_NAME` in `src/anesthesia_sim/app_metadata.py` states only the Linux path.

**The owner can settle it with one command on the Mac**, from the repository root:

```
uv run python -c 'from PySide6.QtCore import QCoreApplication, QStandardPaths; from anesthesia_sim.app_metadata import APP_DISPLAY_NAME, APP_ORGANIZATION_NAME; app = QCoreApplication([]); app.setOrganizationName(APP_ORGANIZATION_NAME); app.setApplicationName(APP_DISPLAY_NAME); print(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))'
```

**Why it matters.** The document tells a reader where to find, back up or delete their saved Workspaces and prices.

**Done when.** The macOS sentence states the path that the command printed on a Mac, and the item records the output.
