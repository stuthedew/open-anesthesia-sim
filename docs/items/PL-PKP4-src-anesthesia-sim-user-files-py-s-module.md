---
id: PL-PKP4
title: src/anesthesia_sim/user_files.py's module docstring says the atomic-write steps, including os.replace, live there once, but each store (layout/store.py, app/preferences.py) calls os.replace itself and user_files.py holds only write_synced, sync_directory_quietly and remove_quietly; correct the docstring, or move the replace into user_files.py so the claim holds (found by the PL-SVGH restructure audit)
priority: P2
effort: S
status: ready
classes: defect, docs
touches: src/anesthesia_sim/user_files.py
deferred-from: v0.7.0 - a new problem, not present at the freeze: user_files.py and its docstring arrived in 2076f542 (PL-93B3)
added: 2026-11-07
payoff: a developer changing how a reader's file is saved knows which steps are shared and which each store does itself, so neither store drifts unnoticed
verify: ! grep -qF 'The steps live here once' src/anesthesia_sim/user_files.py
---

**Problem.** The module docstring of `src/anesthesia_sim/user_files.py` says that every atomic-write step, `os.replace` included, lives there once. But each store (`layout/store.py`, `app/preferences.py`) calls `os.replace` itself, and `user_files.py` holds only `write_synced`, `sync_directory_quietly` and `remove_quietly`. Correct the docstring, or move the replace into `user_files.py` so that the docstring is true. The `PL-SVGH` restructure audit found this.

**Checked 2026-11-09:** The module docstring of `src/anesthesia_sim/user_files.py` still says "The steps live here once". `os.replace` is still called in `layout/store.py` (in the save and in `_copy_replacing`) and in `app/preferences.py`. `user_files.py` defines only `write_synced`, `sync_directory_quietly` and `remove_quietly`, as it has since #1920 created it.

**Why it matters.** A developer who trusts the docstring changes the write procedure in `user_files.py` and believes both stores follow, when each store's replace step is its own. The two files hold the reader's saved layouts and agent prices, so a store that drifted could lose them on a crash.

**Recommended.** Correct the docstring so that it names the steps that live here and says each store replaces the file itself. The layout store copies its previous generation between the write and the replace, and wraps each step so that its error names it, so a shared write-and-replace function would have to take that step as an argument. A session that finds a clean shared function may build it instead and rewrite the `verify:`.

**Done when.** The module docstring says what `user_files.py` holds and what each store does itself, and no sentence claims that a step lives there when it does not.

**Generator check.** One-off. The docstring was wrong from the commit that created it, and the `PL-SVGH` restructure audit found it. No head states the fact.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. `src/anesthesia_sim/user_files.py` did not exist at 817a4d88. Its docstring arrived in 2076f542 (`PL-93B3`, #1920, 2026-11-01), which built v0.7.0's preferences file, so this is a new problem and is deferred.
