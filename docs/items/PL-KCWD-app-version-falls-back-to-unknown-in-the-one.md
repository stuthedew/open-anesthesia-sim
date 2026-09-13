---
id: PL-KCWD
title: APP_VERSION falls back to 'unknown' in the one line tying a displayed value to the model that produced it
status: done
priority: P3
effort: S
classes: anticipated, defect
touches: src/anesthesia_sim/app_metadata.py, src/anesthesia_sim/app/formatting.py, tests/unit/test_app_metadata.py
added: 2026-09-02
closed: 2026-09-13
verify: uv run pytest tests/unit/test_formatting.py tests/unit/test_app_metadata.py && grep -q 'def test_the_subtitle_declares_an_unidentified_build_instead_of_naming_one' tests/unit/test_formatting.py
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

**Decided 2026-09-13: option 2, now rather than at packaging time.**
The brief calls option 3 - defer to item 23 - defensible, and it is, but it
was rejected on two counts. The first is queue mechanics: deferring does not
get this out of Gate 1. Packaging is not a scoped milestone with a version to
wait on, so the honest status would have stayed `needs-decision`, which
`bin/docket gate` counts as debt somebody can resolve, and it would have sat
there being re-read. The second is that option 2 costs about fifteen lines
and is testable today, where option 1 (stamping the version in at build time)
cannot be written or tested until a build exists to stamp - and option 1 does
not actually remove the fallback, it only makes one path unreachable, leaving
a corrupted install still rendering "Version unknown".

So the fallback's policy stays - failing visibly beats crashing on launch -
and only where the visible failure lands changes.
`app_metadata.py` gains `UNKNOWN_VERSION` and `APP_VERSION_IS_KNOWN`, the
fact kept with the metadata it is read from; `format_subtitle` owns the
words, so the one on-screen statement of provenance is composed in the module
that owns presentation rather than assembled from a sentinel that leaked into
it. An unidentified build now reads "Version unavailable (this build is not
traceable)" rather than "Version unknown".

The regression test patches `importlib.metadata.version` rather than the
module's own imported name, which is the trap this item's own measurement
recorded: the reload re-executes `from importlib.metadata import ... version`
and overwrites a patch applied to `anesthesia_sim.app_metadata.version`,
reporting the real version and a false all-clear.

The adjacent finding the brief deliberately did not fold in - that the
*parameter set* has no version of its own, so editing a partition coefficient
changes every displayed number and bumps nothing - is untouched here and
remains open.
