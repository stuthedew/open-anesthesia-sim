---
id: PL-YKF8
title: The interface shows only the released version, so an owner verifying a fix by eye cannot tell which build drew the screen
priority: P2
effort: S
status: done
classes: ux, infra
feature: presentation-safety
touches: src/anesthesia_sim/app_metadata.py, src/anesthesia_sim/app/formatting.py, tests/unit/test_formatting.py, tests/unit/test_app_metadata.py, tools/import_boundary_check.py, docs/ARCHITECTURE.md
added: 2026-09-08
closed: 2026-09-08
pr: 468
verify: uv run pytest tests/unit/test_formatting.py && grep -q 'def test_the_subtitle_carries_the_build_identifier_when_there_is_one' tests/unit/test_formatting.py
---

**Problem.** The interface shows only the released version, so an owner verifying a fix by eye cannot tell which build drew the screen

`_subtitle_text` in the header badge reads
`Version {APP_VERSION} — {agent} patient model`, and `APP_VERSION` comes from
`pyproject.toml`. That number moves only when a release is cut, so every build
between two releases displays the same string - including a build from before a
fix and a build from after it.

**What that cost, concretely** (`PL-QC38`, 2026-09-08). `PL-61WW` (the agent
name losing contrast in the disabled selector) merged, and the project owner
reported the symptom still present. It was a stale build. Nothing on screen
could have told them that: both the old and the new build read "Version 0.4.9",
because no release has been cut since the fix landed. The session spent several
turns ruling out a regression from the source, and could not check visually at
all - the app is Flet, its Flutter renderer is fetched from `www.gstatic.com`,
and a Claude Code web container's egress policy answers 403 to Google hosts, so
the app never leaves its splash screen.

**Why it matters.** This is not a nuisance about a label. The gate this project
is currently clearing is full of `presentation-safety` items whose fixes can
only be confirmed by eye, on the owner's own machine, because no test in this
repository can see a rendered pixel. Every one of them has the ambiguity this
item describes, and the failure mode is the expensive direction: a fix that
works is reported broken, and a session spends its context re-deriving a
correctness argument for code that was already correct. A wrong reading in the
other direction is worse - a fix that did *not* work, confirmed as working
because the screen looked new.

**Candidate directions, none chosen.** The choice is a design question about
what a build should say about itself, not an obvious fix.

- Show the git describe/commit alongside the version where the build is not a
  released one - most informative, and it puts a developer-facing string into a
  clinician-facing header, which `CLAUDE.md`'s presentation standard has
  opinions about.
- Show it somewhere other than the badge - an About affordance, or the
  disclaimer line at the foot of the page.
- Leave the interface alone and give the owner a command that prints what the
  running build is, which keeps the screen clean and does not help while they
  are looking at the screen.

Worth deciding before the next presentation-safety item is handed over for
visual confirmation.

**Triaged `ux, infra` at P2 rather than `safety` at P1, deliberately.** The
version the subtitle shows today is *correct* - it is the installed
distribution's version, and `CLAUDE.md`'s traceability clause asks a displayed
value to name the model and version behind it, which it does. What is missing
is the ability to distinguish two builds carrying the same version, which is a
verification problem for whoever is looking at the screen rather than a
clinician being misled by it. `docket check` pins `safety` to the top band and
the band has to keep meaning "a clinician could be misled".

**The direction, decided by the project owner (2026-09-08): the commit beside
the version, on builds that are not a release.** Of the three the brief above
poses, the only one that helps at the moment the owner is actually looking at
the screen, and the only one that costs a released build nothing.

**Done when.** The header subtitle names the build whenever the running code is
not a clean checkout of the released tag, and says nothing extra when it is.

- `APP_BUILD_VERSION` in `app_metadata.py` is `APP_VERSION` on a release build
  and `{APP_VERSION}+g{short hash}` otherwise, with `.dirty` appended where the
  working tree has uncommitted changes. PEP 440 local-version syntax, so it
  reads as a version rather than as debug output.
- The git read runs against **the directory the module was loaded from**, not
  the process working directory, so launching the app from elsewhere cannot
  describe a different repository.
- It fails closed and silently: no git, not a repository, a timeout, or a
  non-zero exit all give the bare version. That conflates "this is the release"
  with "this cannot be identified", which is stated in the docstring rather
  than hidden - the alternative, printing "unknown build" on every installed
  copy, would put noise on the shipped product to serve a development need.
- The decision of what to display is a pure function of what git said, so it is
  tested against fixed inputs rather than against whatever state this checkout
  happens to be in.
- `subprocess` joins `tools/import_boundary_check.py`'s `BOUNDARIES`, confined
  to `app_metadata.py`. This change is what puts an environment read into the
  package for the first time, and the guard is what stops the habit reaching
  `core/`, where reading the environment would break the reproducibility
  guarantee `docs/MODEL.md` states.

**Landed (2026-09-08).** The header now reads
`Version 0.4.10+ge9cd9c93.dirty — Isoflurane patient model` in a working
checkout, and `Version 0.4.10 — Isoflurane patient model` on a clean checkout
of the tag.

`build_identifier` is a pure function of what git said, and every case is
tested against fixed input rather than against this checkout: the release tag,
a commit past it, a dirty tree, a dirty checkout *of* the tag (the case where
the equality test carries the whole decision - `v0.4.10-dirty` is not
`v0.4.10`, and reporting it as the release would be the exact false
confirmation this item exists to prevent), a repository with no release tag,
and the three ways git can fail to answer. `_git` holds the impure half: it
runs against `Path(__file__).parent` rather than the process working
directory, so launching the app from elsewhere cannot describe a different
repository, and it returns None on a missing binary, a non-repository, a
timeout or a non-zero exit.

**`subprocess` is now confined by `tools/import_boundary_check.py` to
`app_metadata.py` alone.** This change is what puts an environment read into
the package for the first time; the guard is what stops the habit reaching
`core/`, where it would break the reproducibility guarantee `docs/MODEL.md`
states. Not scope creep but the other half of doing this safely - the same
argument `time` and `datetime` are confined on.

**Docs.** `docs/ARCHITECTURE.md`'s package-map line for `app_metadata.py` said
"version (from package metadata)", which is now incomplete, and says what the
header shows and why. Nothing else needed changing: `docs/MODEL.md`,
`README.md` and the rest of `docs/ARCHITECTURE.md` make no statement about
what the version line contains, so no statement became false. `docs/MODEL.md`
arguably *should* say it, under the traceability clause - not added here,
because that file is contested by sibling sessions and `PL-K8YM` already holds
the header statements it is owed.

**The base was merged into this branch**, which `CLAUDE.md`'s `PL-WC72` rule
normally refuses. The branch forked before v0.4.10 was cut, so `doc_check`
failed on it - git holds the tag, and the branch's `ROADMAP.md` had no row for
it - while `main` was green. That is the admitted case: a branch that cannot go
green without the base, rather than a merge out of habit.
