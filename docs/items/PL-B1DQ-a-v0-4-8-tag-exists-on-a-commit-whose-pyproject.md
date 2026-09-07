---
id: PL-B1DQ
title: A v0.4.8 tag exists on a commit whose pyproject says 0.4.7 and whose ROADMAP has no v0.4.8 row, so doc_check errors in every clone that holds the tag
status: untriaged
added: 2026-09-07
---

**Problem.** A v0.4.8 tag exists on a commit whose pyproject says 0.4.7 and whose ROADMAP has no v0.4.8 row, so doc_check errors in every clone that holds the tag

An annotated tag `v0.4.8`, written 2026-09-07 12:29:42 -0500, points at
`b03a7d03` — the current tip of `origin/main`, and the commit that closed
`PL-0GTC`, `PL-CL8J` and `PL-SR8F` in `#432`. No release was cut at it:
`pyproject.toml` reads `version = "0.4.7"`, `ROADMAP.md`'s version table stops
at the v0.4.7 row that also carries `current baseline`, and `docs/releases/`
holds no v0.4.8 notes. `tools/doc_check.py` reports it as an **error**, which
is correct: "git holds v0.4.8, but no row of the version table marks v0.4.8
completed; a release that shipped is one this table has to name".

**Why it matters.** The failure is currently **local only**, which is the worse
shape rather than the milder one. `git ls-remote --tags origin` does not list
v0.4.8 (68 tag refs, none of them this one), and `.github/workflows/quality.yml`
checks out at `fetch-depth: 0`, which takes its tags from the remote — so CI is
green while `make check` and `make doc-check` fail in every clone that holds the
tag. A gate that is red locally and green in CI is the shape that trains a
session to read past `doc-check` output, and `CLAUDE.md`'s "A check earns its
place every run, or it is retired" is about exactly that cost. Observed
2026-09-07 in a session working `PL-P1Z3`: `make check` failed on this error
alone, and the only way to establish that it was pre-existing was to delete the
tag ref, re-run, and restore it.

It also goes wrong in the other direction the moment the tag is pushed: CI
inherits the error on every open pull request until the ROADMAP row exists.

**What the fix is not.** Deleting the tag from a container is not the fix — the
container is ephemeral and the remote is authoritative. Which way to resolve it
is the project owner's, and it is one of two:

- **Cut v0.4.8 at `b03a7d03` and move the tag onto the release commit.** The
  release commit is by construction *later* than the commit currently tagged,
  because it is the commit that writes the version, so the tag has to move
  rather than stay. `bin/docket release` refuses to cut a release while the
  previous one is untagged, and this is the inverse case — a tag with no
  release — which it does not currently detect.
- **Delete the tag and cut v0.4.8 normally**, per the `docket` skill's release
  mode.

**The check that would have caught it earlier.** `bin/docket release` guards
"the previous release is untagged". Nothing guards "a tag names a version no
release cut", which is the same invariant read the other way and is equally
decidable from the tree: `tools/doc_check.py` already computes it, so what is
missing is that the guard fires at the moment somebody is about to tag rather
than on every `make check` afterwards.
