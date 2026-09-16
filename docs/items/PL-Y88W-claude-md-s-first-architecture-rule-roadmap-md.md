---
id: PL-Y88W
title: CLAUDE.md's first architecture rule, ROADMAP.md's development rules and docs/resident-instructions.md all still say 'independent of Flet', a toolkit the tree no longer imports, so the resident rule names the wrong dependency in every session
status: untriaged
added: 2026-09-16
---

**Problem.** CLAUDE.md's first architecture rule, ROADMAP.md's development rules and docs/resident-instructions.md all still say 'independent of Flet', a toolkit the tree no longer imports, so the resident rule names the wrong dependency in every session

**The three lines, found by `PL-3SQT` while taking Flet out of
`pyproject.toml`.**

- `CLAUDE.md:131` - "Keep scientific/simulation code independent of Flet."
  This is resident: it loads at launch in every session.
- `ROADMAP.md:3317` - "Keep simulation code independent of Flet, wall-clock
  time, filesystem state, ..."
- `docs/resident-instructions.md:136` - names the same invariant as one of the
  ones tested for residency.

**Why it is a capture and not a defect that misleads.** The rule's *intent*
still holds and a session obeying it literally does the right thing, so
nothing is silently wrong; the cost is that the resident instruction names a
package the tree does not import and the enforcement lives elsewhere.
`tools/import_boundary_check.py` is what actually carries it now, in two
shapes - `flet` and `flet_charts` permitted in no module under `src/`, and
`PySide6`, `pyqtgraph` and `numpy` in none under `core/` (`PL-9KDK`).

**The question this is really asking** is whether the rule should name the
current toolkit or stop naming one at all. "Independent of the UI toolkit" is
the invariant, and it is the phrasing that does not go stale on the next port;
`PL-YVM1` adopted the same principle for version numbers - outside
`ROADMAP.md` the port is named by what it is, never by a version.

**Not fixed in `PL-3SQT`'s branch on purpose.** `CLAUDE.md` sits in the cached
prefix of every request, so it is edited in its own session
(`CLAUDE.md` § "Session and tool-use efficiency"), and this is outside that
item's `touches`.
