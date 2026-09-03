---
id: PL-2MYT
title: 'Record the source hierarchy: a reference implementation is not a citation'
priority: P1
effort: S
status: done
closed: 2026-09-03
classes: science, docs
feature: model-spec-accuracy
touches: docs/MODEL.md, .claude/rules/expert-review.md, docs/WORKING_NOTES.md
added: 2026-09-03
verify: python3 tools/doc_check.py check
---

**Problem.** The project owner, on 2026-09-03: Gas Man was provided as a
starting point for values and a working example of an implementation, never
as a definitive citation, and would not be used as a primary source. Sessions
have been treating it as one — presenting it as the authority for a constant
in files and in replies.

Nothing in the tree said otherwise. `CLAUDE.md` already requires "authoritative
primary sources over convention-by-habit", and `docs/MODEL.md` already
required a full citation for every scientific parameter, but neither said
what makes a source authoritative, so a citation to a commercial teaching
product's workbook satisfied both rules as written. Worse, two of this
project's three tier-3 citations are peer-reviewed papers — De Wolf et al.
2012 and Meybohm et al. 2021, both Gas Man simulation studies — which made
the provenance look primary at a glance while neither paper measured a
coefficient.

**Why it matters.** This is a safety-critical provenance question, not a
bibliographic one. `CLAUDE.md` requires a displayed clinical value to be
traceable to the exact model, inputs and transformations that produced it. A
reader who follows a citation and finds a measurement believes the number was
measured; a reader who follows it and finds another program's parameter set
learns something different and important. Presenting the second as the first
breaks the chain at the point where the reader would have caught it.

**Where, and how it was routed.** `CLAUDE.md`'s four dispositions, cheapest
first, with the answer for each:

1. *A check.* The decidable half is real but needs a machine-readable tier
   field, which is a schema change to four protected data files. Scoped as
   `PL-1JDD` (make the source tier machine-readable so `doc_check` can decide
   it) rather than built here.
2. *A skill.* No — this is not a multi-step procedure with its own trigger.
3. *A path-scoped rule.* Yes, for the session-conduct half.
   `.claude/rules/expert-review.md` already scopes to `src/**`, `docs/**` and
   `tests/**`, which is exactly where a provenance note gets written, so the
   block was added there rather than in a new file. It costs zero resident
   lines: `measure_resident` counts only `CLAUDE.md` and
   `.claude/rules/instruction-writing.md`, the two that load unconditionally.
4. *Resident in `CLAUDE.md`.* No, and deliberately. The general principle —
   prefer authoritative primary sources — is already resident. The specific
   application cannot be violated before a session reads a data file, the
   provenance table, or `docs/MODEL.md`, all of which the rule above covers.

The substantive standard went to `docs/MODEL.md` § "Source hierarchy: what may
be cited as the authority for a value", because it is the authoritative model
specification and a human reader needs it as much as a session does. The rule
file points at it and holds only what a session needs at the moment it names
a source — the pattern `.claude/rules/ui-color.md` already uses.

**What landed.**

- `docs/MODEL.md` — a new "Source hierarchy" subsection under "Parameter
  provenance": three tiers (primary measurement, secondary synthesis,
  reference implementation), the rule that republication does not promote a
  value between them, a plain statement of where this project actually stands
  (26 of the 29 rows in the provenance table are tier 3; the three
  exceptions are vaporizer device limits), and three rules for a
  `sources` entry. The provenance checklist above it now requires the tier.
- `docs/MODEL.md` — the "v0.2.0: isoflurane and desflurane" subsection, which
  presented "all three agents drawn from the same source table" as a virtue
  without saying the table is Gas Man's parameter set, now says so and says
  what the shared source does and does not buy.
- `.claude/rules/expert-review.md` — "A reference implementation is not a
  source", including that the rule binds replies as well as files.
- `docs/WORKING_NOTES.md` — one stale inference corrected: the venous-pool
  note read "1.0 L is the Gas Man reference value ... so the number is right".

**Not done here, and filed.** `PL-6Q8N` (the reference adult's eleven
physiologic parameters have no primary source at all), `PL-D6LX` (decide
whether to adopt primary-literature partition coefficients or label the
shipped set as Gas Man's), `PL-1JDD` (make the source tier machine-readable).
`PL-T531` (decide isoflurane's blood:gas coefficient) carries an appended note
that its recommendation rested on the premise this item demotes.

**No stored value changed.** Documentation and instructions only.

**Done when.** `docs/MODEL.md` states the hierarchy and this project's honest
position within it; a session writing a provenance note meets the rule at the
moment it writes one; `python3 tools/doc_check.py check` passes; and the
substantive re-sourcing work is filed rather than silently deferred.
