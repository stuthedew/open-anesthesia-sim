---
id: PL-KCWD
title: APP_VERSION falls back to 'unknown' in the one line tying a displayed value to the model that produced it
status: needs-decision
priority: P3
effort: S
classes: anticipated, defect
touches: src/anesthesia_sim/app_metadata.py, src/anesthesia_sim/app/formatting.py, tests/unit/test_app_metadata.py
added: 2026-09-02
---

**Problem.** `app_metadata.py` falls back to `APP_VERSION = "unknown"` when
installed-package metadata is unavailable, and `formatting.format_subtitle()`
renders
`f"Version {APP_VERSION} - {agent_display_name} patient model"`. The
subtitle is the only on-screen link between a displayed number and the model
that produced it, and in that build it reads "Version unknown".

**Why it matters.** The fallback's comment - "fail visibly rather than crash
on launch" - is the right policy. The objection is where the visible failure
lands: in a provenance field, where "unknown" reads as an answer rather than
as an absence. `CLAUDE.md` requires displayed values to be "traceable to the
exact model/version, inputs, units, and transformations that produced them".

Classed `anticipated` because the trigger is the frozen or bundled build,
which `ROADMAP.md` item 23 has not built yet. It becomes real when packaging
does.

**Where.** `src/anesthesia_sim/app_metadata.py`;
`src/anesthesia_sim/app/formatting.py`, `format_subtitle()` (moved there from
`SimulationView` by PL-WB0X, and now covered by
`tests/unit/test_formatting.py`).

**Decision needed.** Whether to solve it now or at packaging time, and how:

1. Stamp the version into the package at build time, so the fallback is
   unreachable in a shipped build.
2. Keep the fallback but render the provenance line differently when it
   fires - an explicit "version unavailable, this build is not traceable"
   rather than a version-shaped string.
3. Defer entirely until item 23 (packaging, signing, distribution) is
   scoped, and record it as that milestone's problem.

Option 3 is defensible and may be the right call for a project with no
frozen build yet. Recorded so the decision is taken rather than defaulted
into.

Adjacent and deliberately not folded in: the *parameter set* has no version
of its own - `schema_version` versions the schema, not the values - so
editing a partition coefficient changes every displayed number and bumps
nothing. The app version is an adequate proxy for a released build and stops
being one if agent files ever arrive from outside the wheel.

**Done when.** The decision is recorded, and if the code changes, a test
asserts the rendered subtitle for the metadata-unavailable case.

**Measured 2026-09-02.** Confirmed as written. With
`importlib.metadata.version` raising `PackageNotFoundError` and both modules
reloaded, `APP_VERSION` is `'unknown'` and
`format_subtitle('Sevoflurane')` returns

    'Version unknown - Sevoflurane patient model'

against `'Version 0.3.0 - Sevoflurane patient model'` normally. The string
reaches the header verbatim, so the provenance line reads as though
"unknown" were the version rather than the absence of one.

Worth recording how the first probe failed, because it is a trap: patching
`anesthesia_sim.app_metadata.version` and then reloading the module does
**not** reproduce this - the reload re-executes
`from importlib.metadata import ... version`, which overwrites the patch, and
the probe reports the real version and a false all-clear. The patch has to be
on `importlib.metadata.version` itself.
