---
id: PL-QBX0
title: ROADMAP planned item 24 gates only data/**/*.json scientific parameters out of the preferences panel, which does not cover the three ISO 5360 agent-identification colours or the contrast-checked palette, both of which app/theme.py holds and tools/contrast_check.py verifies statically
priority: P1
effort: S
status: ready
classes: safety, docs
feature: settings-panel-prerequisite
touches: ROADMAP.md
added: 2026-09-17
verify: python3 tools/doc_check.py check && grep -qF 'the agent-identification colours and the contrast-checked palette' ROADMAP.md
---

**Problem.** ROADMAP planned item 24 gates only data/**/*.json scientific parameters out of the preferences panel, which does not cover the three ISO 5360 agent-identification colours or the contrast-checked palette, both of which app/theme.py holds and tools/contrast_check.py verifies statically

**Why it matters.** Item 24's gating sentence is the only thing standing between
a future preferences panel and the values this project treats as safety-critical,
and it names one location. The ISO 5360:2016 agent-identification colours are
not in `data/**/*.json` - they are in `app/theme.py`, adopted because Table 2
footnote b obligates them, and they are how a reader tells sevoflurane from
desflurane at a glance. A panel that let a reader recolour them would let one
agent be displayed in another's identification colour, which is
`CLAUDE.md`'s "the correct number with the wrong label" exactly. The
contrast-checked palette is the same shape one step down: `tools/contrast_check.py`
holds every trace to 3:1 against the panel in four vision models, and that floor
is a static guarantee about constants a settings screen would make editable.

Classed `safety` although nothing is built yet: the hazard is in the
specification a later session will implement from, and it is cheapest to close
there.

**Done when** item 24's gating sentence covers the display constants whose values
carry a safety or accessibility guarantee - the ISO 5360 agent-identification
colours and the contrast-checked trace palette - as well as the scientific
parameters in `data/**/*.json`, and says which tool verifies each, so the panel's
scope is decidable rather than inferred from where a constant happens to live.
