---
id: PL-HC9P
title: Make the WCAG colour target fire when a session picks a colour
priority: P3
effort: S
status: done
classes: infra
feature: presentation-safety
milestone: v0.2.9
touches: .claude/rules/ui-color.md
added: 2026-09-02
closed: 2026-09-02
pr: 183
verify: python3 tools/doc_check.py check && grep -qF 'Picking a color in this interface' .claude/rules/ui-color.md
---

**Problem.** The project's accessibility standard, wherever it ends up written,
reaches no session at the moment it is needed. A session adding a UI colour
reads `app/theme.py` or `app/simulation_view.py`; nothing in either path tells
it there is a target. `.claude/rules/expert-review.md` loads on `src/**` and
lists human factors among the review domains, but names no contrast criterion
and no number. The result is visible in the tree: the three agent colours got a
careful analysis with recorded provenance and dichromacy simulation, and the six
trace colours immediately beside them got none — same file tree, same session
population, no rule in between.

**Why it matters.** This is the difference between a goal and a change.
`CLAUDE.md`'s behaviour-change rule is explicit that an item on its own changes
nothing — it sits untriaged and invisible to `bin/docket next` while every
session in the meantime keeps picking colours the old way. `PL-1MK1` catches a
violation after it is written; this stops it being written.

**Approach.** Route it per `CLAUDE.md`'s four dispositions, cheapest first, and
note that this item is disposition 3 only for the part `PL-1MK1` cannot decide:

- Disposition 1 is `PL-1MK1` — the checker. Anything it can decide should not
  also be prose here. Prefer deleting a sentence from this rule over keeping one
  the script now enforces.
- Disposition 3 is what is left: a `.claude/rules/ui-colour.md` with `paths:`
  frontmatter scoped to `src/anesthesia_sim/app/**`, loading when a session
  reads the UI. It should carry the judgment half only — the conformance target
  and level, that colour is never the sole channel and why (the ISO 5360
  reasoning in `theme.py:30-37`, which is stronger than SC 1.4.1's floor), that
  a new colour is added to the checker's declared table in the same change, and
  that trace discriminability is a stricter bar than background contrast.
- Not disposition 4. This matters only in `app/`, and a session that never opens
  the UI has no reason to carry it.

**Caveat on path-scoped rules.** They fire on a *read*, so they do not cover a
session that writes a new UI file without reading an existing one.
`PL-1MK1` is the backstop for exactly that case, which is another reason the
checker should land first or alongside.

**Where.** New `.claude/rules/ui-colour.md`. Possibly a cross-reference from
`.claude/rules/expert-review.md`, though duplicating the content there would
violate the same one-place rule this item exists to serve.

**Depends on.** `PL-MMYM` for what the rule states. Best done with or after
`PL-1MK1` so the rule can point at the checker rather than restate it.

**Done when.** A session reading `src/anesthesia_sim/app/theme.py` sees the
conformance target and the sole-channel rule without being told to look, and the
rule states only what the checker cannot decide.
