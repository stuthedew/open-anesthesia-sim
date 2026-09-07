---
id: PL-K8YM
title: docs/MODEL.md does not record that identity-carrying controls are never rendered disabled, nor the running-agent chip beside the selector and header
status: untriaged
added: 2026-09-07
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
