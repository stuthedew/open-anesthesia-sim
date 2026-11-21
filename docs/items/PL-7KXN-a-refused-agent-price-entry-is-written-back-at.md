---
id: PL-7KXN
title: A refused agent price entry is written back at every save and named at every launch, and the interface offers no way to clear it: Preferences.without_refused_entries has no caller
status: untriaged
feature: interface-matches-its-spec
added: 2026-11-21
---

**Problem.** A refused agent price entry is written back at every save and named at every launch, and the interface offers no way to clear it: Preferences.without_refused_entries has no caller

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `docs/ARCHITECTURE.md` § "User state: the reader's preferences" says that a price entry which names no agent is refused, written back at every save, and named in the notice at every launch. That is what the code does. The docstring of `Preferences.without_refused_entries` in `app/preferences.py` says "The interface offers this so that the reader can clear a refused entry". No code under `src/` calls it. Only `tests/unit/test_preferences.py` does.

**Why it matters.** A reader whose preferences file holds a refused entry reads the same notice at every launch and cannot clear it without editing the file by hand.

**Decided here** (2026-11-21, over deleting the method): the agent cost View offers to discard the refused entries beside the notice that names them, and asks the reader to confirm, because the discard cannot be undone.

**Done when.** The reader can discard refused entries from the agent cost View, a test discards one and reads a launch with no notice, and the docstring says what the interface offers.
