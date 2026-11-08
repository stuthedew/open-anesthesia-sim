---
id: PL-7SVX
title: Delete spikes/ and the last Flet import once the port is complete
priority: P2
effort: S
status: done
classes: refactor, infra
feature: qt-port
milestone: v0.4.26
touches: spikes, ROADMAP.md, docs/WORKING_NOTES.md, pyproject.toml, tools/doc_check.py
added: 2026-09-10
closed: 2026-09-16
pr: 638
verify: uv run python tools/import_boundary_check.py && ! test -d spikes
---

**Problem.** Delete spikes/ and the last Flet import once the port is complete

**The Qt port's Required scope, item 7, and it is the last one.**

Two deletions: `spikes/` entire - `PL-55DH` built it to throw away cleanly, and
`rm -rf spikes/` is the whole procedure - and the last `import flet`.

**It is also the check that the port is actually finished.** While any module
imports Flet, both toolkits are in the tree and the release has not crossed the
boundary it claims to. `tools/import_boundary_check.py` is where that becomes a
rule rather than a sweep: a boundary declaring that *nothing* imports Flet is
the same shape as the two it already enforces, and it is what stops the next
change reaching for the old toolkit.

**Do not run this early.** The spike is the working reference every other item
in this milestone reads from, so it goes last.

**Why it matters.** It is the check that the port actually finished, not a
tidy-up after it. While any module imports Flet both toolkits are in the tree,
the dependency declaration cannot be narrowed, and the release has not crossed
the boundary it claims to. Making it a rule rather than a sweep is what stops
the next change reaching for the old toolkit:
`tools/import_boundary_check.py` already enforces two boundaries of exactly this
shape, and "nothing imports Flet" is a third.

**Done when.** `spikes/` is deleted, no module under `src/anesthesia_sim/`
imports Flet, and `tools/import_boundary_check.py` declares and enforces that as
a boundary so the absence is held rather than merely current.

**Do not run this early.** The spike is the working reference every other item
in this milestone reads from, so it goes last.

**Rider, 2026-09-14 (pre-port survey).** Deleting
`tests/integration/test_chart_patching.py` (which imports
`flet.messaging.protocol`, `flet.controls.object_patch` and
`flet.pubsub.pubsub_hub`) orphans two `[[tool.mypy.overrides]]` in
`pyproject.toml`: `flet_charts`, and `msgpack`, whose comment names that file
as its only importer. mypy will not report them - `strict` does not enable
`warn_unused_configs`. Delete both in the same commit.

**The Flet half landed with `PL-25KS`, 2026-09-15.** The last `import flet`
left with the Flet dashboard, and `tools/import_boundary_check.py` already
holds `flet` and `flet_charts` to no module under `src/anesthesia_sim/` - the
"held rather than merely current" boundary this brief asks for. What this item
still owes is `spikes/` (the working reference every other port item read
from, so it goes last, after `PL-L9RD` and `PL-3SQT`) and `PL-C92D`'s table.
The `verify:` above was re-pointed the same day, because its old form passed
the moment the dashboard port merged and `docket check --verify` refuses a
command that passes before the work.

**Closed 2026-09-16.** `spikes/` is gone - four files, deleted whole, exactly
the `rm -rf` this brief promised. The Flet half was already held: nothing under
`src/anesthesia_sim/` imported either package, and
`tools/import_boundary_check.py` has carried `flet` and `flet_charts` at
`allowed=()` since `PL-25KS`, so this branch edited neither file.

**The deletion's real cost was the citations, not the tree.** Seven documents
named the spike. Five were code-span path citations `tools/doc_check.py` failed
on the moment the directory went - `ROADMAP.md` x3, `docs/WORKING_NOTES.md` x2.
Two were invisible to it and mattered more: `ROADMAP.md`'s two
`spikes/qt/qt_spike.py --screenshot` spans carry a ` --screenshot` suffix, so
the span is not a bare path and `_is_path_citation` never resolves it - they
read as live instructions to a session that cannot run them. Both now name
`tests/integration/test_qt_rendering.py`, which is where `PL-YCWZ` landed that
capability. This is `CLAUDE.md`'s "do not script the judgment" line arriving as
a worked example: the check decided whether a path exists and could not decide
whether the sentence around it was still true.

**What was kept, and why.** The spike was evidence for leaving Flet, and the
evidence does not vanish with the artifact - only its retrieval path does. Every
mention became past tense naming what was demonstrated, and
`docs/WORKING_NOTES.md` § "Built and measured: the Qt spike runs" now says
outright that the source tree is gone and its tables are what survives of it.
The heading itself was left alone deliberately: `PL-C92D` and `PL-55DH` both
quote it verbatim, and `docs/WORKING_NOTES.md` headings are dated records, so
renaming it would have broken two citations to fix a tense the date already
carries.

**`touches` was re-declared, which `docket verify` flags and should.** It was
written 2026-09-10, before anyone had swept for citations, and predicted the
wrong footprint in both directions. Removed: `tools/import_boundary_check.py`,
`src/anesthesia_sim/app` and `docs/ARCHITECTURE.md`, none of which this work
edits, and declaring `app/` would have blocked other sessions out of a hot tree
for nothing. Added: `ROADMAP.md`, `docs/WORKING_NOTES.md`, `pyproject.toml` and
`tools/doc_check.py`. The rule applied is that **a statement this change
falsifies is this change's work, wherever it lives** - which is what admits the
`ROADMAP.md` and `docs/WORKING_NOTES.md` edits `make check` fails without, and
the same argument applied consistently admits the other two rather than routing
them through the fix-now door they do not fit.

**`docket verify` reports two FAILs and both are honest.** `pyproject.toml`
trips "the checks themselves are unedited" because that file also holds the ruff,
mypy and coverage configuration; the diff is four comment lines and no setting.
`touches` trips "item front matter unchanged" for the re-declaration above. Both
are the audit surfacing a judgment for a human, which is its job - neither was
worked around.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "Waiting on the Qt port, on 2026-09-12".

> **Four are waiting on the port rather than on anybody's attention.** `PL-7SVX` *is* item 7 of the port's Required scope. Deleting the Qt spike tree before the port landed would have removed the working reference that every other item in that milestone read from. `PL-C92D` asks for a caveat on a Flet measurement whose toolkit is being removed. The same pass re-scoped it so that it no longer asks for a re-measurement. `PL-SQJ1` measures a playback shortfall that is a consequence of frame cost the port removes. So measuring it now would measure a tree that is about to change. `PL-ZG5J` would land a harness built on `flet.messaging.session.Session` for the use of one milestone. Each of the four is real, and each gets a worse answer if it is hurried in ahead of the port.

> The port has since landed (`PL-25KS`, § "Completed: v0.4.26 — the interface moves to Qt"). So the ground above is spent rather than wrong. It records why these four were deferred on 2026-09-12. Whether each one can be started now is for the queue to say, not this section. `PL-ZG5J` closed on 2026-09-19 with a Qt harness under `tests/benchmarks/`, which is not the Flet harness described above. In Flet, a serializing connection made the measurement method subtle. In Qt, the paint plays the part of that serializing connection. The harness is written down rather than thrown away, so that the next session re-measures instead of re-deriving it.

> - PL-7SVX (S) Delete spikes/ and the last Flet import once the port is complete — closed in v0.4.26
