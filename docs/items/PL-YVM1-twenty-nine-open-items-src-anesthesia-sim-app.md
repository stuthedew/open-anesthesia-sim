---
id: PL-YVM1
title: Twenty-nine open items, src/anesthesia_sim/app/theme.py and docs/MODEL.md still name the Qt port v0.5.1 across 51 references, a version ROADMAP.md no longer contains, and doc_check cannot see it because none of them is a section citation
priority: P2
effort: S
status: done
classes: docs
feature: release-roadmap-seam
touches: docs/items/, docs/MODEL.md, docs/WORKING_NOTES.md, src/anesthesia_sim/app/theme.py
added: 2026-09-14
closed: 2026-09-14
verify: '! grep -rq "^\*\*.v0.5.1..s Required scope" docs/items/ && ! grep -qF "v0.5.1" src/anesthesia_sim/app/theme.py docs/MODEL.md'
---

**Problem.** Twenty-nine open items, src/anesthesia_sim/app/theme.py and docs/MODEL.md still name the Qt port v0.5.1 across 51 references, a version ROADMAP.md no longer contains, and doc_check cannot see it because none of them is a section citation

**Found 2026-09-14**, surveying what to clear before the port starts.

**The count.** 51 references across 29 open items, plus one source comment and
one line of the model specification:

- **The port's own six build items** each open "`v0.5.1`'s Required scope,
  item N": `PL-G59B` (chart), `PL-25KS` (dashboard), `PL-L9RD` (theme),
  `PL-3SQT` (dependencies), `PL-YCWZ` (headless rendering tests), `PL-7SVX`
  (deletion). A session starting one reads a version `ROADMAP.md` does not
  contain.
- `src/anesthesia_sim/app/theme.py:60` — "This binds the Qt port as much as
  this file. `v0.5.1` redecides the palette".
- `docs/MODEL.md:4822` — "**The decision binds `v0.5.1` as much as the current
  interface**". This is the authoritative model specification naming a version
  that does not exist.

**Why nothing caught it.** None is a section citation, so
`tools/doc_check.py` has nothing to resolve and passes. It is the judgment half
of the line `CLAUDE.md` draws, working as designed - the same reason `PL-D1RT`
gives for its own two.

**Why it recurs, which is the part worth deciding.** The port has been
renumbered once already (`v0.5.1` → `v0.4.25`, 2026-09-14 under `PL-RKWB`);
that sweep reached `ROADMAP.md` and ten blockquotes and stopped. Cutting any
patch before the port lands moves the number again - which is exactly what
`ROADMAP.md` § "v0.4.25" records as its one risk, and `PL-G7RD` is about to
exercise it. Every such move strands the prose again.

**Nothing mechanical reads these.** Every `blocked-by` on a port-dependent item
already names a port *item* (`PL-3355` → `PL-25KS`, `PL-GS3R` → `PL-G59B`, and
so on, verified across all nine), and `MilestoneStates.ships_with` reads
`ROADMAP.md`'s `Required scope`. The version in item prose is decoration that
has now been wrong twice.

**Decision needed, and it is the project owner's** because it is a convention
across the queue rather than a fix to one file:

1. **Sweep to the port's name, not to its number** - "the Qt port", or the port
   item id where one fits - and leave `ROADMAP.md`'s heading as the single
   place the version lives. The number can then move as often as the release
   train needs it to and no prose goes stale. **This is the recommendation.**
2. **Sweep to the new number.** Honest today, stale at the next patch cut
   before the port lands.

**Done when** no file outside `ROADMAP.md` names the port by a version that
`ROADMAP.md` does not currently carry, and `src/anesthesia_sim/app/theme.py`
and `docs/MODEL.md` read correctly against the plan as it stands.

## Swept 2026-09-14, to the port's name (option 1, project owner, 2026-09-14)

**The rule adopted.** Outside `ROADMAP.md`, the port is named by what it is -
"the Qt port", or the port item doing the work - never by a version. The
version lives in `ROADMAP.md`'s heading and timeline row, and in the `§`
citations of that heading, which `tools/doc_check.py` resolves and so fails
loudly when the heading moves. Prose carries no number because a number in
prose is checked by nothing, and this one had already been wrong twice.

**What changed: 56 edits across 32 files**, each asserting its line occurred
exactly once before it was touched. The six build items' openers
(`PL-G59B`, `PL-25KS`, `PL-L9RD`, `PL-3SQT`, `PL-YCWZ`, `PL-7SVX`) now read
"The Qt port's Required scope, item N". The ten deferral blockquotes - `PL-T7PY`'s
four and the six "rides the Qt port" - carry no version. The five "blocked on
the item rather than on the version" paragraphs say so in those words.
`src/anesthesia_sim/app/theme.py:60` and `docs/MODEL.md:4822` bind the
decision to "the Qt port". `docs/WORKING_NOTES.md:684` defers `PL-NGF7` to
the port by name.

**"Done when", refined.** The line above says "a version `ROADMAP.md` does not
currently carry"; the honest reading is *present-tense* naming. A dated record
of what the port was called on a given day is history and stays: the `reason:`
fields on `PL-7J96` and `PL-F0L8`, closed items' bodies, and the probe output
quoted in `PL-VFD8` (a literal `wave` fixture line, not a claim). This item's
own title and `PL-T7PY`'s describe the defect and stay as written.

**Left where it was, deliberately.** `ROADMAP.md`'s twenty-four `v0.4.25`
mentions are the cut's to move (`PL-G7RD`), since they change to whatever
number the port takes and the citations among them are what `doc_check`
guards. `subprojects/docket/` docstrings and `tools/doc_check.py` comments
quoting `v0.5.1` describe historical bugs in the tool and are fixtures rather
than claims about the plan.
