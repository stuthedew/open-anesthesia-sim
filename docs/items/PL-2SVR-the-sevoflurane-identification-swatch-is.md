---
id: PL-2SVR
title: The sevoflurane identification swatch is invisible as a shape against the panel
priority: P3
effort: S
status: dropped
classes: ux
feature: presentation-safety
touches: src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md
added: 2026-09-02
closed: 2026-09-02
reason: Written from the colour constants without reading the widget that uses them, and wrong in both of its claims. The swatch is on the page background, not the panel (1.27:1, not 1.37:1), and the border this item proposes adding already exists and predates the item - `simulation_view.py` builds the badge with `border=ft.Border.all(1, foreground)` under a comment already citing the figure. Every agent swatch is perceivable today: sevoflurane by its border at 10.70:1, isoflurane and desflurane by their fills at 6.60 and 6.06. What is genuinely wrong is that the checker cannot express "perceivable by either channel" and so reports a false shortfall, which is `PL-GNN1`. The one thing neither covers - whether isoflurane's and desflurane's inert white borders should be removed - is cosmetic, and filing it would put a styling preference in a queue that is meant to hold defects.
---

> **Read this first (2026-09-02).** Most of what follows is wrong, and the item
> is much narrower than it was written. Two corrections, both found while doing
> `PL-X0RG`:
>
> 1. **The swatch is on the page background, not the panel.** The title above
>    and the measurements below say `PANEL`. The header badge and the agent
>    dropdown both sit in the top-level column, so the surface is `BACKGROUND`
>    (`#F4F7FA`) and the sevoflurane fill measures **1.27:1**, not 1.37:1.
> 2. **A border already exists, and predates this item.** `simulation_view.py`
>    builds `_agent_header_badge` with `border=ft.Border.all(1, foreground)`,
>    under a comment that already cites the 1.37:1 figure. The mitigation this
>    item proposes was in the tree before the item was written; the item was
>    drafted from the colour constants without reading the widget that uses
>    them.
>
> So every badge does have a perceivable boundary today — but by a different
> channel for each agent, which nothing states and nothing checks:
>
> | Agent | Fill vs page | Border vs page | Perceivable by |
> | --- | --- | --- | --- |
> | Sevoflurane | 1.27 | 10.70 | its border |
> | Isoflurane | 6.60 | 1.08 | its fill |
> | Desflurane | 6.06 | 1.08 | its fill |
>
> Isoflurane and desflurane carry a **white** border on a near-white page. It
> contributes nothing; their dark fills do the work instead.
>
**Decision needed.** Whether anything is left in this item at all. `PL-GNN1`
covers the checkable part - a "fill or border" requirement kind, which makes all
three swatches pass honestly and would catch a future agent that is invisible by
both channels. If that is the whole of it, drop this item with a reason rather
than leaving it open. What `PL-GNN1` does *not* decide is whether isoflurane's
and desflurane's white borders should stay: they are inert rather than harmful,
but a border that contributes nothing is a thing every later reader has to work
out before concluding it is deliberate. That is a judgment call, and it is the
only live question here.

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
