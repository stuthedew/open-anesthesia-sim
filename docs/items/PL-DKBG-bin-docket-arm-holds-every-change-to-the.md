---
id: PL-DKBG
title: bin/docket arm holds every change to the simulator's paths for the owner's read whatever it changes, so a pull request with nothing to judge, such as #1516's measured figures and tightened tests, waits on the owner and its ask invents points to judge; the owner's rule of 2026-10-17 sends the owner only a real decision or a high-risk change the session wants a second set of eyes on, and lets housekeeping merge on green
priority: P2
effort: M
status: done
classes: infra
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py, CLAUDE.md, docs/maintainer.md, docs/resident-instructions.md, tools/workflow_paths_check.py, docs/items/PL-N7LK-four-apparatus-documents-wrap-a-spaced-hyphen.md
added: 2026-10-17
closed: 2026-10-17
pr: 1522
payoff: a pull request reaches the owner only for a real decision or a high-risk change, with the case and its risks, and housekeeping merges on green
verify: grep -q 'def test_arm_holds_a_simulator_change_until_an_owner_read_record_covers_it' subprojects/docket/tests/test_cli.py && grep -q 'OWNER_READ = "Owner-read"' subprojects/docket/src/docket/arming.py
---

**Problem.** bin/docket arm holds every change to the simulator's paths for the owner's read whatever it changes, so a pull request with nothing to judge, such as #1516's measured figures and tightened tests, waits on the owner and its ask invents points to judge; the owner's rule of 2026-10-17 sends the owner only a real decision or a high-risk change the session wants a second set of eyes on, and lets housekeeping merge on green

**Why it matters.** Each ask with nothing in it spends the owner's attention
on a call a measurement already made, and trains a click-through that would
let the one change that does need the owner merge as unread as the rest. That is
the failure `PL-SQTR` retired the docket-wide hold for.

**The owner's rule** (project owner, 2026-10-17, in the Projects thread at
23:10Z): "Change the rule. Model comes to me only when there is a real decision
as discussed or making a high risk change you want a second set of eyes on then
you should present the case for the change, the risks etc. but house keeping
stuff I don't need to sign off everything". "As discussed" is the owner's
reply at 23:08Z to `#1516`'s read ask, which put two "points to judge" to the owner: measured
figures that followed from a correct fix, and 23.5 against 24.5 hours of
elimination, where the model's own supported run length rules out 24.5. They
asked "What am I judging? ... What is the trade off", and want a question only
where there is a real trade-off.

**Why the path list cannot carry it.** `arm` held every change under `src/`,
simulator `tests/`, `docs/MODEL.md` and `README.md` (`READ_PATHS`), so a test
tightened or a measured figure restated waited on the owner exactly as a changed
equation did, and the read ask then had to find something to put to them.
Whether a change is a decision, a risk or housekeeping is not a fact about its
paths.

**The design.** The session decides, and records the decision where `arm`
reads it, so the answer stays decided from the tree and the judgment is
auditable rather than a line in a reply that dies with the session.

- A commit trailer, `Owner-read: needed - <why>` or `Owner-read: not needed -
  <why>`, on a commit of the branch. The newest one decides.
- A branch changing a simulator path (the former read list) holds until a
  record covers its newest change there, so a session that forgets to judge
  holds rather than arms. The safety-critical standard is why it fails that
  way: a missed judgment on `src/` must not merge a clinical value unread.
- `not needed` arms it on green, the paths and the reason named beside the
  answer for the report and the pull request body.
- `needed` holds it for the owner, on any path, the workflow lane included.
- `arming.py` itself still always holds, so the gate cannot loosen itself
  (project owner, 2026-10-12, ratified, `PL-VKHD`). A change to it is a change
  to what merges without the owner, the high-risk case by definition.
- `needed` means a real decision, one `.claude/skills/docket/modes/design.md`
  step 4 already makes the owner's, or a high-risk change: one that changes a clinical value
  the simulator computes or displays, or what `docs/MODEL.md` says one means,
  beyond restating a measurement the change's own tests make; a rule sessions
  run under that the owner did not ask for in their own words; or a change whose
  breakage CI would not show or a revert would not undo.
- For a high-risk change the ask carries the case for the change, its risks
  and what was checked. How a decision is put is the existing rule's, and the
  ask points at it: its earlier wording asked for "numbered points for the
  owner to judge" wherever a clinical value or `docs/MODEL.md` changed, which
  contradicted that rule and is what produced `#1516`'s two points.

**Chosen over** two routes. Dropping the simulator paths from the list and
leaving the judgment to prose fails open: a session that never thinks about it
merges a clinical change unread. Keeping the paths and only rewording the ask
leaves housekeeping waiting on the owner, the thing they asked to stop.

**A departure from the coordinator's brief.** The brief counted every change
to how sessions are governed as high-risk. The owner's rule of 2026-10-12, in
their own words, is that workflow items need no merge confirmation (`PL-KPM2`),
so only a governance change the owner did not ask for is high-risk here.

**Done when.** `bin/docket arm` answers as above, its tests pin each case, and
`CLAUDE.md`, `docs/maintainer.md`, the `docket` skill and
`tools/workflow_paths_check.py` describe the new rule. `#1516` is left as it
stands, waiting on the owner's word.

**Generator check.** None. The path list was the owner's own rule
(`PL-KKHD`), narrowed once (`PL-552M`). Asks with nothing to judge followed
from it, so the rule's mechanism changes here and no reader misread a fact.
