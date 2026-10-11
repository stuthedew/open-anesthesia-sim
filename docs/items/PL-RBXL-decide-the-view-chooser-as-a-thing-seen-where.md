---
id: PL-RBXL
title: Decide the View chooser as a thing seen, where Required-scope entry 16 specifies only what it guarantees
priority: P2
effort: S
status: done
classes: ux, planning
feature: interface-areas
touches: src/anesthesia_sim/app/, docs/items
added: 2026-10-11
closed: 2026-10-11
pr: 1395
payoff: the View chooser reads as navigation rather than as a setting, so choosing a View is never mistaken for changing the run
verify: grep -qF 'Answered 2026-10-11' docs/items/PL-RBXL-decide-the-view-chooser-as-a-thing-seen-where.md
---

**Problem.** Decide the View chooser as a thing seen, where Required-scope
entry 16 specifies only what it guarantees. `ROADMAP.md` § "v0.6.0" ->
"Required scope" entry 20, member 5. `PL-50PZ` Q4 (ratified 2026-09-27) puts
one chooser in each Area's header listing every registered kind by registry
title, and makes the accounting tier's reachability an invariant of the
registry and the chooser; `PL-50PZ` builds it.

**The reference.** Blender's editor-type selector is the first button at the
left of every header, an icon button whose menu lists the editors under
category headings (Blender Manual, `editors/index.html`, read 2026-10-11,
paraphrased).

## Design round 2026-10-11

**Q1. The control.** **Recommendation: a flat menu button, not a combo box.** It
shows the current View's registry title in `INK` at `METRIC_NAME_SIZE` with a
chevron after it, no frame at rest, a `BACKGROUND` fill on hover and while its
menu is open, and the keyboard focus ring the application already draws. It is
not a `QComboBox` because this interface uses combo boxes for *settings* -
Playback, Time base - and the chooser is navigation: giving it the settings'
control would say that choosing a View changes the run, which it never does
(`PL-WV9K` Q6). Blender's selector is the same shape, an icon where this project
has a title. *Alternatives refused:* a `QComboBox`, for the reason above; an
icon, because the project has no icon set until item 33 and an icon without a
title is a thing to learn.

**Q2. The menu.** **Recommendation:** a plain menu listing every registered kind
by registry title in registry order, the current kind checked, with no grouping
and no decoration on the required-reachable kinds: entry 16's guarantee is
structural (the registry refuses to drop them), so the menu need not mark them.
Choosing an entry calls `set_view`, including into an Area too small for it,
which then shows `PL-DB5G`'s statement (`PL-K285`). Keyboard: Space or Enter
opens, the arrows move, Enter chooses, Escape closes, type-ahead as `QMenu`
gives it, and the button is in the Area's tab order (`PL-M352`). *Alternative
refused:* Blender's grouped menu, which groups because Blender has some thirty
editors; this project has a handful, and groups would be headings over one
entry each.

**Q3. Width.** The button is as wide as its title, so the header's left block
changes width when the View changes. Accepted: a fixed width would be sized to
the longest title and spend header width in every other Area.

[superseded 2026-10-11: answered below, every recommendation ratified]
**Decision needed.** Q1-Q2 above: a flat menu button rather than a combo box
(Q1), and a plain menu of every registered kind in registry order with the
current one checked (Q2). Q3 is the session's call and is recorded rather than
asked. Agreeing with the recommendations ratifies both.

**Done when.** Q1-Q3 are recorded with the owner's kind and date, this item
closes on that record, and `PL-50PZ` builds the chooser to it, declaring its
hover pair in `tools/contrast_check.py`.

**Why it matters.** The chooser is how a learner reaches every View not on
screen, the accounting tier the safety standard requires to stay reachable
among them; a chooser that looks like a setting, or is not found, defeats the
guarantee entry 16 gives it.

**Generator check.** A one-off, and work the owner asked for: one of the
members `ROADMAP.md` Required-scope entry 20 names, scoped on 2026-09-21
(`PL-M3X6`) and filed by its round on 2026-10-11. `touches` reaches
`docs/items` only because the item closes on its own record once answered; no
apparatus fact was misread.

## Answers 2026-10-11

**Answered 2026-10-11: Q1-Q2 ratified** (project owner, 2026-10-11, ratified,
over the alternatives each question names - a combo box, an icon, and Blender's
grouped menu), given in the project thread as "Agree with recs" after the
recommendations were put one line each with the mock-up
(https://claude.ai/artifact/3KmFvWB3nXmjLBHKogNiNE) and the 1366 by 768 floor
confirmed by the same word. This item closes on that record; the build items
named in its Done-when carry the look.
