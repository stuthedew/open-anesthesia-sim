---
id: PL-PKP4
title: src/anesthesia_sim/user_files.py's module docstring says the atomic-write steps, including os.replace, live there once, but each store (layout/store.py, app/preferences.py) calls os.replace itself and user_files.py holds only write_synced, sync_directory_quietly and remove_quietly; correct the docstring, or move the replace into user_files.py so the claim holds (found by the PL-SVGH restructure audit)
status: untriaged
added: 2026-11-07
---

**Problem.** The module docstring of `src/anesthesia_sim/user_files.py` says that every atomic-write step, `os.replace` included, lives there once. But each store (`layout/store.py`, `app/preferences.py`) calls `os.replace` itself, and `user_files.py` holds only `write_synced`, `sync_directory_quietly` and `remove_quietly`. Correct the docstring, or move the replace into `user_files.py` so that the docstring is true. The `PL-SVGH` restructure audit found this.
