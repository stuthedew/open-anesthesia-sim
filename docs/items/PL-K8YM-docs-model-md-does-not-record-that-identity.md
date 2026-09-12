---
id: PL-K8YM
title: docs/MODEL.md does not record that identity-carrying controls are never rendered disabled, nor the running-agent chip beside the selector and header
priority: P2
effort: S
status: ready
classes: docs, ux
feature: presentation-safety
touches: docs/MODEL.md
added: 2026-09-07
verify: python3 tools/doc_check.py check && grep -q '_running_agent_display' docs/MODEL.md
---

**Problem.** docs/MODEL.md does not record that identity-carrying controls are never rendered disabled, nor the running-agent chip beside the selector and header

Two statements in `docs/MODEL.md` are now incomplete rather than wrong, and
both were left alone by `PL-61WW` (the agent name losing contrast in the
disabled selector) because three sibling sessions were holding that file at the
time.

- § "Agent identity" (the paragraph opening "The agent selector and header
  reinforce that written name...") names two carriers of the ISO 5360 colour.
  There are three: `_running_agent_display` stands in the selector's place for
  the whole of a run and carries the same `fill`/`foreground` pair.
- § "Color contrast, and the standard this interface is held to" lists the bars
  this interface holds itself *above* AA, and there is now a third one it does
  not name: **no control carrying agent identity is ever rendered in a disabled
  state**, so SC 1.4.3's exemption for "text ... that is part of an inactive
  user interface component" is never claimed here. That exemption is what made
  the `PL-61WW` defect formally conformant while it was on screen, which is
  exactly why declining to claim it is worth recording as a bar rather than
  left as an accident of the current widget tree.

**Where.** `docs/MODEL.md:3350` for the first; the bullet list under
"Color contrast..." (near `docs/MODEL.md:4060`) for the second.

**Why it matters.** Both statements are incomplete rather than wrong, which is
what has let them survive two passes. The first names two carriers of the ISO
5360 agent colour where there are three, so a reader auditing agent identity
against the specification would find `_running_agent_display` undocumented -
and it is the carrier that stands in the selector's place for the whole of a
run, which is most of the time a reader is looking at the screen.

The second is the one worth recording deliberately. This interface never renders
an identity-carrying control disabled, so it never claims SC 1.4.3's exemption
for text that is part of an inactive component. That exemption is what made the
`PL-61WW` defect formally conformant while it was on screen, so declining to
claim it is a bar this interface holds itself to rather than an accident of the
current widget tree - and an accident is exactly what it will become if the next
rewrite is not told.

**Sequencing.** `PL-L9RD` re-expresses the theme for Qt and `PL-25KS` rewrites
the widget tree. Writing the bar down *before* those land is the point: it is
the statement that survives the port and constrains it.

**Done when.** § "Agent identity" names all three carriers of the agent colour,
and § "Color contrast, and the standard this interface is held to" lists the
never-disabled bar among the ones this interface holds above AA, with the
reasoning for declining the exemption.
