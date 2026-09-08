---
id: PL-YKF8
title: The interface shows only the released version, so an owner verifying a fix by eye cannot tell which build drew the screen
status: untriaged
added: 2026-09-08
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
