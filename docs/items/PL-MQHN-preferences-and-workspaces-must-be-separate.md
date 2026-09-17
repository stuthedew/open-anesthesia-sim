---
id: PL-MQHN
title: Preferences and Workspaces must be separate stores, and PL-WV9K, PL-SSQW and PL-KXTL are being designed now - folding display unit or price into the Workspace JSON makes Blender's Save/Revert/Load-Factory Preferences workflow impossible to add later
priority: P2
effort: S
status: done
classes: planning, ux
feature: preferences-store
touches: ROADMAP.md
added: 2026-09-16
closed: 2026-09-17
verify: python3 tools/doc_check.py check && grep -qF 'decided by instance multiplicity rather than by Workspace membership' ROADMAP.md
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

**Why it matters.** `PL-WV9K` (the Workspace object) is the item that decides
what a Workspace carries, and it is blocked on `PL-1FT6` rather than finished,
so the sentence it needs can still be written cheaply. Written late it is a
migration; written now it is one paragraph. What made it urgent enough to
answer rather than park is that the obvious answer is wrong in a way that is
hard to reverse: a Workspace already persists, is already versioned JSON, and
already has shipped defaults, so a display setting can just ride along in it,
and unpicking that later means rewriting every saved Workspace.

## The decision (project owner, 2026-09-17)

**The tier a setting belongs to is decided by instance multiplicity, not by
Workspace membership, and the Workspace is the container for one tier rather
than a peer of the other two.** Recorded in `ROADMAP.md` § "v0.6.0 - the layout
is the reader's" -> "Required scope" item 11, which is what `PL-WV9K`'s session
reads.

- **Run state** - the simulated values - is one set of numbers every Editor
  draws from and no reader setting reaches.
- **Per-Editor-instance view state** is how *this* Editor draws them: which
  compartments it shows, its axis denomination and range, its time window. The
  Editor serializes it into the Workspace containing it, by the delegation
  `docs/interface-provenance.md` § "Persistence, and what happens when an editor
  is missing" already adopts from Blender's `SpaceType`.
- **Reader preferences** are the settings for which a second simultaneous value
  is incoherent rather than merely unusual. The agent price and its currency is
  the one this project has today, and `PL-B396` already records that default as
  a preference rather than Workspace state.

The test is *can a reader sensibly have two of these on screen at once?* Yes
routes to the Editor; incoherent routes to preferences; a setting that changes
the numbers rather than their drawing is neither and stays in the versioned data
files.

**The owner's case is what settled it** (2026-09-17): one graph showing the
vessel-rich group against the MAC-awake band and the 1 MAC line, a smaller one
below it with every compartment on, and a third in a squarer Area zoomed to the
first fifteen minutes to read the wash-in - **all three in the same Workspace**.
So two instances of one Editor kind disagree inside a single Workspace, and a
rule keyed on Workspace pairs cannot even state the case. `.claude/rules/ui-areas.md`
rule 2 already asks "who owns it when two areas show the same editor", with
`PL-VN6M` as the standing counter-example, and rule 3 already requires a view to
be instantiable more than once.

**Two independent reset scopes, one file.** Blender's preference reset reads
`use_data = false, use_userdef = true`, resetting preferences alone while
leaving the document's workspaces untouched - two scopes over one read path,
not two files. Its file split exists because one `userpref.blend` serves *many*
`.blend` documents; both stores here are single-per-user, so that relation does
not hold and a second file buys nothing over two reset operations over two
sections. `PL-SSQW` already owes five things for one file; it is not owed them
twice.

## What this item got wrong, recorded so it is not re-derived

The original brief argued "a unit and a price are not layout, therefore they are
preferences", by analogy to Blender. **Blender does the opposite**: `UnitSettings`
is a member of `Scene` (`DNA_scene_types.h`, "Display/Editing unit options for
each scene"), so a display unit is document state on the very side a preferences
reset does not touch. `WorkSpace` being an ID datablock is correct; the
classification drawn from it is not. Three routings that followed from the weaker
argument contradict decisions already recorded, and each is listed here because
the argument is more tempting than its conclusion:

- **Display unit.** `docs/MODEL.md` refuses a selector outright - "Both units are
  always shown rather than selected, because a unit selector would make the axis
  unit a mode, and a chart read under the wrong assumed unit is a misreading no
  disclaimer catches."
- **Axis range.** `docs/MODEL.md` fixes the MAC ceiling "anchored to a real
  device limit rather than to a preference", and whether a reader may depart from
  it is `PL-V67Q`'s open question, which owes a human-factors literature read.
- **Slider ranges.** "The ranges are the model's, not the interface's"
  (`PL-0MLQ`); they define the verification domain and out-of-range is refused,
  not clamped. `ROADMAP.md` planned item 24 listing them is the stale text.

**This holds while a run is ephemeral, which is a condition rather than a
permanent property.** Planned-milestone items 9, 10, 12, 26 and 30 add a saved
scenario; a scenario is a fourth tier, and where it sits is placed when the first
of them is scoped rather than assumed now.

**Done when.** The tier split, its test and its expiry condition are recorded in
`ROADMAP.md`'s v0.6.0 `Required scope` item 11, where `PL-WV9K` will read them.
Building either store is not this item's: `PL-WV9K` and `PL-SSQW` are chartered
for it and blocked on a layout model nobody has started.
