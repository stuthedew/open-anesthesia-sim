---
id: PL-QBX0
title: ROADMAP planned item 24 gates only data/**/*.json scientific parameters out of the preferences panel, which does not cover the three ISO 5360 agent-identification colours or the contrast-checked palette, both of which app/theme.py holds and tools/contrast_check.py verifies statically
priority: P1
effort: S
status: done
classes: safety, docs
feature: settings-panel-prerequisite
touches: ROADMAP.md
added: 2026-09-17
closed: 2026-09-19
pr: 709
verify: grep -qF 'the agent-identification colours and the contrast-checked palette' ROADMAP.md
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

## What was written, 2026-09-19

**The gate is now a criterion with instances under it, rather than a longer
list.** Replacing one enumeration with a three-entry enumeration would have
left the same defect in place: item 24's sentence was not wrong about
`data/**/*.json`, it was wrong to be a list at all, and a list is silent about
the next constant exactly as this one was silent about `app/theme.py`. So the
sentence that decides is *what holds a value* - a safety, standards-conformance
or accessibility guarantee enforced by something outside the panel - and the
table beneath it is labelled as the instances known on this date rather than as
the scope.

This is `.claude/rules/expert-review.md` § "Say what would falsify it" applied
in the direction it points here: what would falsify the enumeration is a new
constant, which is certain, so the enumeration is the instance and the
criterion is the rule.

**Four rows, and one is not in the item's own brief.** The brief names the ISO
5360 colours and the contrast-checked palette; the table also carries the six
compartment traces' **dash patterns**, in `app/chart_frame.py`'s
`COMPARTMENT_TRACES`. That was a session's call, taken because the row is the
criterion's clearest case rather than an extension of it: `app/theme.py` records
that colour cannot separate six traces at all - the 3:1 floor against the panel
caps every trace's luminance, so six of them cannot be more than 1.48 apart
against the 3:1 that would make colour sufficient - so the dash patterns *are*
the separating channel, and a panel that flattened them would void the
separability guarantee that the colour rows are only half of. It is also the one
row no tool defends, which the table says in place of a verifier.

**Verifiers, checked against the tree rather than recalled.** Each was opened
before its cell was written: `tests/unit/test_theme.py`'s
`test_agent_colors_match_iso_5360_2016_table_2` asserts the whole
`AGENT_COLOR_SCHEMES` mapping including the Munsell and Pantone provenance;
`tools/contrast_check.py` reads every module under `app/` with `ast` and holds
declared pairs to their declared ratios; `tools/agent_identity_check.py` refuses
a control carrying agent identity that can be rendered disabled, which is what
keeps the pair *measured* equal to the pair *rendered*. All three run in `make
check` and in `.github/workflows/quality.yml`. Nothing checks the dash patterns,
which is why that cell says so.
