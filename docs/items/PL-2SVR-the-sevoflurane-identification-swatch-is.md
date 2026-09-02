---
id: PL-2SVR
title: The sevoflurane identification swatch is invisible as a shape against the panel
priority: P2
effort: S
status: ready
classes: defect, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/simulation_view.py, tools/contrast_check.py, docs/MODEL.md
added: 2026-09-02
verify: python3 tools/contrast_check.py && ! grep -q '("sevoflurane.fill", "PANEL")' tools/contrast_check.py
---

**Problem.** Sevoflurane's ISO 5360 identification colour is yellow,
`#FEDB00` as approximated in `app/theme.py:60`. Against `PANEL` (`#FFFFFF`) it
measures **1.37:1** - far below WCAG 2.2 SC 1.4.11's 3:1 for graphical objects.
The agent *name* over that fill is fine (8.41:1, the best of the three), so the
text is readable; what is not perceivable is the swatch's own boundary. On a
white panel the yellow chip has, visually, no edge.

**Why it matters.** A swatch with no perceivable edge is a safety cue that
does not read as a cue. The identification colour exists so an agent is
recognised at a glance, and a chip that blends into the panel is recognised as
nothing - the reader falls back to the name alone, which is exactly the
redundancy the colour was added to provide, running in the wrong direction.
Sevoflurane is also the agent this defect happens to hit, and it is the one
most likely to be selected.

**Why this is not simply "change the colour".** The colour is fixed by ISO
5360:2016 Table 2 and `app/theme.py:30-37` records why it cannot move: "If a
colour is used ... it is important that only the colour for the appropriate
anaesthetic agent be used." Substituting a darker yellow to pass a contrast
check would break the identification guarantee the colour exists to provide -
trading a real safety property for a formal one. SC 1.4.11 anticipates this
with its exception for graphics "where a particular presentation ... is
essential to the information being conveyed", which an agent-identification
colour plainly is.

**So the defect is the presentation, not the colour.** The swatch needs a
perceivable boundary that is not the fill: a border at >= 3:1 against `PANEL`,
or placing it on a surface it separates from. Isoflurane (7.10:1) and
desflurane (6.52:1) do not need one, but the treatment should be uniform -
bordering only the yellow chip would make sevoflurane look like a different
kind of control.

**Approach.** Give every agent swatch the same border, specified against
`PANEL` rather than against its own fill so one rule covers all three. Then
decide how `tools/contrast_check.py` should record it: either the requirement
moves to `border on PANEL` (the honest pair once a border exists), or the
1.4.11 exception is declared explicitly in `REQUIREMENTS` with this item's
reasoning. Prefer the first - it keeps the check measuring something real
rather than recording a licensed failure.

**Where.** `app/theme.py` (`AGENT_COLOR_SCHEMES`, and a border constant);
the swatch construction in `app/simulation_view.py:280-303`;
`tools/contrast_check.py`'s `KNOWN_SHORTFALLS` entry for
`("sevoflurane.fill", "PANEL")`; `docs/MODEL.md` beside the agent-colour
section.

**Done when.** Every agent swatch has a boundary perceivable at >= 3:1 against
`PANEL`, no ISO 5360 fill has been altered, and the checker measures the
boundary rather than carrying a shortfall entry.
