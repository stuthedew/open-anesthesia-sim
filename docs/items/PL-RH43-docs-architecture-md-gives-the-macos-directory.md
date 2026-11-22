---
id: PL-RH43
title: docs/ARCHITECTURE.md gives the macOS directory of the saved Workspaces as ~/Library/Application Support/<App>, which nobody has run on a Mac, and on Linux Qt adds the organization name
priority: P3
effort: S
status: ready
classes: defect
feature: interface-matches-its-spec
touches: docs/ARCHITECTURE.md, src/anesthesia_sim/app_metadata.py
deferred-from: v0.7.0 - present at the freeze, with no real connection to the frozen list or to v0.7.0's Required scope: the sentence states where Qt files user data on macOS, which no v0.7.0 entry wrote or depends on, and the preferences section that v0.7.0 added names no platform path
added: 2026-11-21
payoff: A reader on a Mac is told the right place to find, back up or delete their saved Workspaces and prices.
---

**Problem.** docs/ARCHITECTURE.md gives the macOS directory of the saved Workspaces as ~/Library/Application Support/\<App>, which nobody has run on a Mac, and on Linux Qt adds the organization name

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/ARCHITECTURE.md` § "User state: the saved Workspaces" says "On macOS the directory is `~/Library/Application Support/<App>`." This check corrected the Linux path in the same paragraph to `~/.local/share/<Org>/<App>`, after Qt printed `<HOME>/.local/share/OpenAnesthesia/Open Anesthesia Simulator` there. The macOS path has the shape that the wrong Linux path had, and no session can run it. The comment on `APP_ORGANIZATION_NAME` in `src/anesthesia_sim/app_metadata.py` states only the Linux path.

**The owner can settle it with one command on the Mac**, from the repository root:

```
uv run python -c 'from PySide6.QtCore import QCoreApplication, QStandardPaths; from anesthesia_sim.app_metadata import APP_DISPLAY_NAME, APP_ORGANIZATION_NAME; app = QCoreApplication([]); app.setOrganizationName(APP_ORGANIZATION_NAME); app.setApplicationName(APP_DISPLAY_NAME); print(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))'
```

**Checked again 2026-11-22**, at `d4e8200c`. `grep -n "Application Support" docs/ARCHITECTURE.md` still prints the sentence "On macOS the directory is `~/Library/Application Support/<App>`", with no `<Org>`, beside the Linux path `~/.local/share/<Org>/<App>`. The same paragraph also fixes where the reader's prices are kept, because `docs/ARCHITECTURE.md` § "User state: the reader's preferences" puts `preferences.json` beside the Workspaces file. A session without a Mac may be able to settle the path from Qt's published source for the macOS standard paths instead of the command above. Whichever route is taken, the item records it.

**Why it matters.** The document tells a reader where to find, back up or delete their saved Workspaces and prices.

**Done when.** The macOS sentence states the directory that Qt reports on a Mac, and the item records where that reading came from.

**Generator check.** A one-off. The misread fact is what Qt reports for `AppDataLocation` on one platform, an outside behaviour that nothing in the tree models. `PL-5FMC` corrected the Linux sibling in the same paragraph from Qt's own output, and no head's `misread:` states this fact.
