---
id: PL-MQHN
title: Preferences and Workspaces must be separate stores, and PL-WV9K, PL-SSQW and PL-KXTL are being designed now - folding display unit or price into the Workspace JSON makes Blender's Save/Revert/Load-Factory Preferences workflow impossible to add later
status: untriaged
feature: preferences-store
added: 2026-09-16
---

**Problem.** Preferences and Workspaces must be separate stores, and PL-WV9K, PL-SSQW and PL-KXTL are being designed now - folding display unit or price into the Workspace JSON makes Blender's Save/Revert/Load-Factory Preferences workflow impossible to add later

**The direction** (project owner, 2026-09-16). "Like blender, all settings
will eventually be able to be set as the users starting default... Pretty much
identical to blender's save settings workflow, so the user doesn't have to
reset to custom defaults every time." The screenshot supplied is Blender's
Preferences -> Save & Load menu: Auto-Save Preferences, Save Preferences,
Revert to Saved Preferences, Load Factory Preferences. The ask is not to build
it now but to "not make things harder on ourselves down the road with
decisions now".

**The decision it lands on, and it lands now.** Blender keeps two stores, and
the separation is the whole reason its four menu entries can exist: preferences
live in `userpref.blend` and are saved, reverted and factory-reset on their
own, while Workspaces live in the startup file with the scene. `PL-WV9K` (the
Workspace object), `PL-SSQW` (Workspace persistence) and `PL-KXTL` (the three
shipped default Workspaces) are all v0.6.0 items being designed now, and the
tempting simplification is one store: a Workspace already persists, is already
versioned JSON, and already has shipped defaults, so the display unit and the
agent price could just ride along in it.

**They must not.** A unit and a price are not layout. Folded into the
Workspace, "Load Factory Preferences" would reset the reader's layout too, and
switching Workspace would silently change the displayed unit — a mode change
with no announcement, which `.claude/rules/expert-review.md` rules out
directly. Unpicking that later means a migration of every saved Workspace.

**Done when** `PL-WV9K`'s Workspace object explicitly excludes preference
state, a preferences store exists as its own versioned artifact on the same
pattern, and `docs/MODEL.md` or the interface document states which of the two
any new setting belongs in, so the question is answered once rather than per
setting.
