---
id: PL-B1R4
title: Sweep the seven docket mode files for other prescriptions stored in a mode that cannot act on them, the class PL-YZJD fixed one instance of: falsifies: told a triage pass what to do from close-out.md, where only a close-out session reads it
priority: P3
effort: M
status: done
classes: docs
feature: worker-instructions
milestone: v0.5.28
touches: .claude/skills/docket/modes, .claude/skills/docket/SKILL.md, docs/items/PL-B1R4-sweep-the-seven-docket-mode-files-for-other.md
added: 2026-09-22
closed: 2026-10-18
pr: 1557
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

**Swept 2026-10-18.** All eight files under `.claude/skills/docket/modes/`
were read in full, with `SKILL.md`, for instructions whose actor reads a
different mode. The count is eight, not the seven the title says. Three were
moved and one was copied to the mode that acts on it:

- **The gate relation of every offered item** sat in `picking.md`, which named
  design-round and close-out sessions as bound by it. It moved to `SKILL.md`
  § "Always", which every mode's session reads. `picking.md` keeps the four
  relations and points at the rule.
- **Writing a missing `payoff:` as the item starts** (`picking.md`) and
  **repairing a `verify:` as the item starts** (`triage.md`) were addressed to
  a session starting an item. `start.md` now names both moments and points at
  the rules.
- **Declaring `falsifies:` before working an item captured and closed on one
  branch** sat in `close-out.md`, where the moment to declare has passed. It
  is now in `capture.md` too, and `close-out.md` keeps the reasons.

Four candidates were left where they are, because the session that acts on
each already gets the instruction by another route:

- `release.md`'s "offer this; do not wait to be asked" addresses a picking or
  close-out session. The session-start digest's `Releasable:` line already
  tells every session to offer the cut, at the moment the rule names.
- `ideas.md`'s "offer this" for scoping a milestone. `SKILL.md`'s dispatch
  table routes "the queue has thinned and a planned milestone is worth
  scoping" to `ideas.md`.
- `start.md`'s "mark it ready in the push that closes the item" addresses a
  close-out session. `CLAUDE.md`'s commit-and-push rule, which is resident,
  says the same through `bin/docket arm`.
- `picking.md`'s takeover line, for a session that holds a claim and hands the
  item to a fresh one. The line goes into the reply that recommends the fresh
  session, and writing that recommendation is picking's work, so the session
  writing the line has `picking.md` open. This one is a judgment call.
