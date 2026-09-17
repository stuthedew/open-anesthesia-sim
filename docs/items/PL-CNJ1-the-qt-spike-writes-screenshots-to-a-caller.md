---
id: PL-CNJ1
title: The Qt spike writes screenshots to a caller-supplied path with no default directory and no ignore rule, so a --screenshot run in the repo root leaves a PNG a git add -A would commit
priority: P3
effort: S
status: done
classes: defect, docs
milestone: v0.4.26
touches: .gitignore, docs/worker.md, spikes/qt/qt_spike.py
added: 2026-09-15
closed: 2026-09-15
pr: 589
verify: python3 tools/doc_check.py check && git check-ignore -q --no-index out/dashboard.png && grep -q 'out/dashboard.png' docs/worker.md
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

**Worked.** The brief had the finding right and its location wrong, so the
diff reaches a file the brief never named.

*`docs/worker.md` is the recurring case, and the spike is not.* The brief
named `spikes/qt/qt_spike.py:1106` as the only writer. It is the only writer in
*code*, but `docs/worker.md` § "Seeing the interface" hands every worker
session a command ending `print(view.grab().save('dashboard.png'))` and then
says it "writes `dashboard.png` in the working directory" - which is the
repository root. That is an instruction to dirty the tree, issued to every
session that wants to look at the interface, in a file that outlives `PL-7SVX`
by design. It is repointed at `out/dashboard.png`, and the command gains a
`mkdir -p out &&` prefix so it works on a clean checkout. `touches` was widened
to declare the file before the edit.

*The spike default is a CLI change, not just a constant.* `--screenshot` was a
required-value flag; it is now `nargs="?"` with `const=DEFAULT_SCREENSHOT_PATH`,
so a bare `--screenshot` writes `out/dashboard.png` while `--screenshot PATH`
behaves exactly as before. `save_screenshot` also creates the parent directory,
so a caller-supplied path into a directory that does not exist now works rather
than failing at `save`. That needed `from pathlib import Path`, which the module
did not import.

*No `docs/ARCHITECTURE.md` entry, deliberately.* The brief asked for the
directory to be "named in one place that `PL-7J96` and `PL-YCWZ` can both
read". `docs/worker.md` is that place - it is where a session goes to render
the interface - and `PL-YCWZ` has since closed with its test writing to
pytest's `tmp_path`, so it needs nothing. A third statement of the same
convention is the two-documents-one-rule hazard `CLAUDE.md` warns about.

*No `*.png` pattern and no check.* The pattern is rejected in the brief above.
A check refusing tracked images outside `assets/` was considered and not built:
it is worth building only if such a file would otherwise recur, and the count
across this repository's history is zero.

*Both entry points were run, not reasoned about.* The spike wrote
`out/dashboard.png` (161 KB) and the documented `worker.md` command wrote it
again (178 KB), each from the repository root, with `git status` showing only
this item's own edits afterwards.

*`out` and never `out/` in prose, which is not a style choice.*
`tools/doc_check.py:2213` reads any code span ending in `/` as a claim that the
directory exists, and `out/` deliberately does not in a fresh checkout. The
first push here turned CI red on exactly that - `docs/worker.md:50: cites
`out/`, which does not exist` - while `make check` had passed locally, because
testing the screenshot had created the directory minutes earlier. The prose was
wrong and the check was right, so the fix is the wording; the gap that makes the
correct wording undiscoverable is `PL-MXSL`. Note the two neighbouring escapes
are accidents rather than design: `out/dashboard.png` passes only because `.png`
is not in `PATH_SUFFIXES`, and `out` passes only because it has no suffix.

*Re-run with the directory absent.* `make check` was re-run after `rm -rf out`,
so the local result matches a clean checkout rather than the tree this session
had been testing in.
