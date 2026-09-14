---
id: PL-YVM1
title: Twenty-nine open items, src/anesthesia_sim/app/theme.py and docs/MODEL.md still name the Qt port v0.5.1 across 51 references, a version ROADMAP.md no longer contains, and doc_check cannot see it because none of them is a section citation
status: untriaged
added: 2026-09-14
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
