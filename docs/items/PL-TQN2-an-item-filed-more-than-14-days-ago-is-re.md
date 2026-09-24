---
id: PL-TQN2
title: An item filed more than 14 days ago is re-confirmed before it is worked: docket show prints what changed since it was filed, and the start mode drops or rewrites it when the problem is gone
priority: P2
effort: M
status: done
classes: infra
feature: debt-aging
milestone: v0.5.9
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/config.py, subprojects/docket/README.md, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_vcs_silence.py, .claude/skills/docket/modes/start.md, .claude/skills/docket/modes/picking.md
blocked-by: PL-1P5V
added: 2026-09-22
closed: 2026-09-23
pr: 976
payoff: a session starting an old item sees at once whether the code it describes has moved or gone, so it confirms, rewrites or drops the item before spending itself on a problem that may no longer exist
verify: grep -q 'def test_show_says_what_changed_since_an_item_was_filed' subprojects/docket/tests/test_cli.py
---

**Problem.** An item describes the tree as it was on its `added:` date, and
this tree moves fast. The project is a month old. The interface moved from
Flet to Qt at v0.4.26, and `app/simulation_view.py` went from 3,850 lines to
580 (`.claude/rules/citation-drift.md`). An old item can describe code that no
longer exists. The session that starts it finds out only after re-deriving the
problem, or never, and then fixes something that is not broken. `PL-027`
(confirm the slider write-back on a live Flet client) is the live example. Its
own brief has flagged since 2026-09-10 that the Qt port may have mooted it,
and it is still open, 29 days after filing. `PL-Q89J` (`docket next
--oldest`) will hand out exactly these items first, so they need a check at
the moment they are picked up.

**Why it matters.** The project owner asked for it (2026-09-22): with how fast
this is moving, old items should get a special check that they are still
relevant. `ROADMAP.md` § "What counts" already counts the other outcome as
progress: "Clearing means `done` **or** `dropped` with the reason recorded."
So the check converts a stale item into a closed one rather than into a wasted
session.

**Design (project owner, 2026-09-22, ratified - chosen over a store-wide
`docket check` advisory naming every item past the line).** Split
on the line `CLAUDE.md` draws, the same one `tools/doc_check.py` draws:
compute the facts, never the verdict.

- **Decidable half, in code.** For an open item, `bin/docket show` prints its
  age and, for each `touches` path, whether it still exists and how many
  commits have changed it since `added:`. The `start` mode already has a
  session run `show`, so every start sees it however the item was picked. It
  is one `git log --since` read over the declared paths. It says "not read"
  under `--no-git` or where history is missing, never zero.
- **The line: a `recheck_after_days` setting, default 14.** Past it, `show`
  adds one line: re-confirm this item against the tree before starting. 50
  of the owed items no gate holds were past it on 2026-09-22.
- **It fires on the item being opened, never as a store-wide advisory.** 50+
  items are already past the line. An advisory naming them all on every
  `docket check` is one sessions learn to skim, which `CLAUDE.md` § "Prefer
  deterministic tooling over repeated model work" treats as a defect in the
  check.
- **Judgment half, in `.claude/skills/docket/modes/start.md`.** Past the line,
  before writing code, read the brief against the tree with those facts.
  Still true: work it. Changed shape: rewrite the brief first. Gone: drop it,
  with the reason recorded. A dropped item clears it as surely as fixing it.
  **A touched path that no longer exists is a question, not the answer**
  (added 2026-09-22 from the literature check; it says what "gone" in the
  ratified step means, and changes nothing else). A problem can move with the
  code rather than leave with it. Zampetti, Serebrenik and Di Penta found
  20-50% of self-admitted-debt removals were accidental: the comment was
  deleted along with the class or method that held it ("Was self-admitted
  technical debt removal a real removal?", MSR 2018,
  doi:10.1145/3196398.3196423). So the step asks whether the *problem* is
  gone, not the file. `PL-027` (confirm the slider write-back on a live Flet
  client) is the case to try it on. The Flet client is gone, and whether its
  question went with it or moved to the Qt view is exactly what the step asks.
- **Shares a helper with `PL-8JY7`** (a `touches` path is never checked
  against the tree). That item decided an advisory in `docket check` for
  paths that do not resolve. The path-existence test is the same, so
  whichever lands second reuses the first's.

**Done when.** `bin/docket show <id>` prints the age and the per-path facts
(exists or not, commits since `added:`) for an open item. It adds the
re-confirm line past `recheck_after_days`. It says "not read" rather than
zero without history. `modes/start.md` carries the three-way step. The
README documents the facts and why they are not an advisory. Tests cover: a
deleted path; a path changed after `added:`; a path unchanged; the
threshold's edge; the `--no-git` wording.

**Held (project owner, 2026-09-22, ratified, over starting it now).** It adds
output to `docket show` and a rule to the start mode, which is a new workflow
mechanism, and `CLAUDE.md` § "What this project is" pauses those while any open
item carries `generator: live`. Start it once `bin/docket generators` marks no
head "still generating" (`next` leaves out one in flight, `PL-CT07`), or on the
project owner's explicit request, which lifts the pause for that request.
`blocked-by` names `PL-1P5V`, the live head open on 2026-09-23, so that `next`
stops offering this item while the pause holds.

**Started on the project owner's request (2026-09-23), which lifted the pause
for this item alone.** The owner named the item to a session while
`bin/docket generators` still marked `PL-MB2W`, `PL-B8HZ`, `PL-HMZZ` and
`PL-QHCW` "still generating"; `PL-1P5V` itself had closed. Nothing else the
pause holds was built with it (`PL-6Q9L`).

**What landed.** `vcs.since_filed` is the one read: `git log --since` from
`HEAD` over the declared paths, without merges or rename detection, from the
first instant of `added:` in UTC. `vcs.in_tree` is the existence test, read
from the filesystem so it answers under `--no-git`; `PL-8JY7` reuses it.
`SinceFiled` carries `declined`, so a count nobody read prints as "not read"
(under `--no-git`, in a shallow clone, or on any git silence) and never as
"unchanged". `render.format_since_filed` prints the block last before the
brief, and `recheck_after_days` (default 14) adds the `RE-CONFIRM` line on
"more than 14 days": day 14 is inside the line, day 15 past it. An item with
no `added:` says its age is unknown, because an absent re-confirm line reads as
"young". The judgment half is in `.claude/skills/docket/modes/start.md`, and
the README's § "An old item is re-confirmed before it is worked" documents
both halves.

**`PL-027` closed before this landed.** It was dropped on 2026-09-22 as mooted
by the Qt port, after a check that its question had not moved to the Qt view.
That is the step this item writes down, done by hand the day this was filed,
and its reason is the model for a drop's recorded evidence. The case run
instead was `PL-024` (document what the venous pool does to early mixed-venous
readings), the oldest open item at 30 days: `docs/MODEL.md` changed by 152
commits since filing and `src/anesthesia_sim/app/dashboard_frame.py` by 16, with the
re-confirm line firing. 79 open items were past the line on 2026-09-23.
