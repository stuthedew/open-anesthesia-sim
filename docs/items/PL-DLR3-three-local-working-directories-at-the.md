---
id: PL-DLR3
title: Three local working directories at the repository root - oas-mirror, output and outputs - are neither tracked nor ignored, so every session and the owner read them as untracked in git status and a git add -A would sweep them in
status: untriaged
touches: .gitignore
added: 2026-09-15
---

**Problem.** Three local working directories at the repository root - oas-mirror, output and outputs - are neither tracked nor ignored, so every session and the owner read them as untracked in git status and a git add -A would sweep them in

**Observed 2026-09-15**, from the project owner's file-explorer listing:
`oas-mirror/`, `output/` and `outputs/01a03b25-621b-7522-9f75-14...` sit beside
`spikes/` at the repository root. None appears in a fresh clone, which is why a
container session sweeping the tree for unused directories found nothing and
reported the tree clean.

**Both halves measured.** Tracked: no - `git log --all -- oas-mirror output
outputs` returns zero commits for all three, so nothing is being hidden that
history holds. Ignored: also no - `git check-ignore --no-index` matched none of
them before this change. So all three read as untracked in `git status`, which
is the state `PL-1YDK` names as the one where a stray file gets swept into a
diff, and they had been doing so invisibly to every session.

**Fixed here** by three anchored entries in `.gitignore`. Anchored with a
leading `/` deliberately: `output` and `outputs` are ordinary enough words that
an unanchored rule would also hide a real `output/` inside a package, and the
regression probe for that is in the commit.

**`/oas-mirror/` is the one that was more than untidy.** If it holds a clone -
its name and the project owner's "OAS mirror" both say so - then `git add` on
it records a gitlink rather than files: mode `160000` pointing at a commit this
repository has no `.gitmodules` entry for, so a clone of this repository gets a
reference it cannot resolve. Reproduced in a scratch repository on 2026-09-15;
git does print `warning: adding embedded git repository`, which is easy to miss
inside a `git add -A`.

**Left open, deliberately.** Whether any of the three should be *deleted* is
the project owner's call and needs their machine: this session cannot see what
is inside them. `outputs/` holding a UUIDv7-named subdirectory suggests a
per-run output directory from some tool, and nothing in this repository writes
either path - `PL-CNJ1` records that `src/` writes no file at all. Ignoring
them is right under either answer and does not foreclose deleting them.

**Done when.** The three are ignored, no tracked path is newly hidden, and a
nested `output/` under `src/` or `tests/` is still visible. All three verified
in the commit.
