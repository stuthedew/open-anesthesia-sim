---
id: PL-93RN
title: docs/ARCHITECTURE.md's tree entry for tools/workflow_paths_check.py says a crossing item is offered to nobody, where docket next without a lane has offered crossing items since the lane split (#287)
status: untriaged
feature: parallel-sessions
added: 2026-09-27
---

**Problem.** docs/ARCHITECTURE.md's tree entry for tools/workflow_paths_check.py says a crossing item is offered to nobody, where docket next without a lane has offered crossing items since the lane split (#287)

**Evidence, 2026-09-27.** The entry reads "an item declaring one alongside the
script it tests is set aside from both lanes and offered to nobody".
`docket next workflow` and `docket next product` list such an item under "Set
aside, reaching both halves", and that line ends "`docket next` without a lane
offers these" (`cli.py`'s `_say_lane_holdouts`, since `PL-2NSX` and `PL-8165`).
`PL-W40L` corrected the same claim in `docket.toml` and
`tests/unit/test_workflow_paths_check.py`, which its work already touched;
`docs/ARCHITECTURE.md` is on the simulator's side of the lane boundary, so
fixing it there would have made `PL-W40L` itself `crossing`. A one-phrase edit:
"offered by neither lane" is true, "offered to nobody" is not.
