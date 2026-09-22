---
id: PL-B1R4
title: Sweep the seven docket mode files for other prescriptions stored in a mode that cannot act on them, the class PL-YZJD fixed one instance of: falsifies: told a triage pass what to do from close-out.md, where only a close-out session reads it
priority: P3
effort: M
status: ready
classes: docs
feature: worker-instructions
touches: .claude/skills/docket/modes, docs/items/PL-B1R4-sweep-the-seven-docket-mode-files-for-other.md
added: 2026-09-22
payoff: an instruction filed in a mode that never acts on it reaches the session that does, or the sweep records that none is left
verify: grep -q '^\*\*Swept ' docs/items/PL-B1R4-*.md
---

**Problem.** Sweep the seven docket mode files for other prescriptions stored in a mode that cannot act on them, the class PL-YZJD fixed one instance of: falsifies: told a triage pass what to do from close-out.md, where only a close-out session reads it

**Why it matters.** A mode file is read only by a session in that mode. So an
instruction addressed to a different mode fires in a session that cannot act on
it, and never reaches the session that can. `PL-YZJD` measured the cost for one
field: by the time the only session told to write `falsifies:` read the
instruction, the window to write it had shut. A second instance would fail the
same silent way, because nothing checks which mode reads an instruction's
addressee.

**First pass, 2026-09-22 (`PL-14QR`, triage).** One grep across the seven files looked for
another mode named as an actor (`a triage pass`, `a close-out session` and the
like). It found four mentions, two in `start.md` and one each in `triage.md` and
`release.md`, and all four are references rather than instructions to that
mode. So the one phrasing checked holds no second instance. A prescription can
be phrased many other ways, which is why the sweep is a read rather than this
grep.

**Done when.** Each of the seven files under `.claude/skills/docket/modes/` has
been read for instructions whose actor reads a different mode. Each one found is
moved to the mode that acts on it. The result, "none found" included, is written
into this brief under a `**Swept` heading with its date.
