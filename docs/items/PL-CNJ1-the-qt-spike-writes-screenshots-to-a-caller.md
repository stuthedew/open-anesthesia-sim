---
id: PL-CNJ1
title: The Qt spike writes screenshots to a caller-supplied path with no default directory and no ignore rule, so a --screenshot run in the repo root leaves a PNG a git add -A would commit
status: untriaged
touches: .gitignore, spikes/qt/qt_spike.py
added: 2026-09-15
---

**Problem.** The Qt spike writes screenshots to a caller-supplied path with no default directory and no ignore rule, so a --screenshot run in the repo root leaves a PNG a git add -A would commit

**Measured, 2026-09-15**, while answering "what about output folders?".

`src/anesthesia_sim/` writes **nothing**. A grep for `.write_text`, `.write_bytes`,
`open(..., "w"/"a"/"x")`, `.mkdir(`, `json.dump`, `csv.writer`, `QSettings` and
`QStandardPaths` across `src/` returns zero hits, so the simulator produces no
output directory of its own and needs no ignore rule for one. Tests write only
to pytest's `tmp_path`, which is outside the tree. `make prebuild` is `git
status` plus `make check` and builds nothing.

The single exception is `spikes/qt/qt_spike.py:1106`:

    written = window.grab().save(path)

reached by `--screenshot PATH` (`save_screenshot`, line 1065). The path is
whatever the caller passes, there is no default directory, and `.gitignore`
carries no rule for images. So `uv run python spikes/qt/qt_spike.py --screenshot
shot.png` from the repository root leaves an untracked PNG that a `git add -A`
commits — the same failure shape as `PL-8PT6`'s stray `uv.lock`, in a tree that
has since learned to ignore that one.

**Why it is worth answering now rather than when it bites.** Two open items in
this milestone generate images by design - `PL-7J96` (make the interface
renderable in a check) and `PL-YCWZ` (headless rendering tests over the real
Qt). Both need somewhere to put them, and deciding that once is cheaper than
three callers each choosing a path. `spikes/` itself is deleted by `PL-7SVX`,
so the spike is not the thing to fix - the convention is.

**Recommended shape, for the project owner to accept or replace.** One ignored
output directory at the root, `/out/`, named in `.gitignore` beside the other
generated paths, and every image-producing entry point defaulting into it
rather than into the working directory. That gives the rendering checks a home
that exists before they are written, keeps `git status` clean after a
screenshot run, and costs one line plus one `default=` per caller.

Rejected: a bare `*.png`, which would silently swallow a legitimate asset if
this project ever carries one - `assets/` exists for exactly that and was empty
only by accident (`PL-J7MM`).

**Done when.** A screenshot run from the repository root leaves `git status`
clean, and the directory it writes into is named in one place that `PL-7J96`
and `PL-YCWZ` can both read.
