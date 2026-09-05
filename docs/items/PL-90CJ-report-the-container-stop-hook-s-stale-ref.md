---
id: PL-90CJ
title: Report the container stop hook's stale-ref unpushed count upstream, since PL-WW08 fixes it for this project only
priority: P3
effort: S
status: ready
classes: infra
feature: dev-tooling
touches: docs/maintainer.md
added: 2026-09-04
not-delegable: the deliverable is a defect report to the maintainers of the container's stop hook, outside this repository; no command in this tree can prove it filed
---

**Problem.** `PL-WW08` corrected the container's stop hook: it picked its
comparison point from a ref that merely resolved locally, so a merged branch's
stale tracking ref made it demand a push that would have recreated a dead
branch. The fix is `.claude/hooks/stop_hook_patch.py`, which rewrites the hook at
session start - and it fixes it for this repository only. Every other project
using the same container still gets the false demand.

**Why it matters.** The failure it corrects is not cosmetic: acting on the
demand pushes a branch that was deliberately abandoned, and `CLAUDE.md`'s
stale-ref rule exists because such a ref can be the only surviving copy of
captured work. A patch applied per project also has to keep working against a
hook the session does not own, so reporting it upstream is the only route to it
not needing to.

**Where.** Outside this repository. What is here is the evidence a report needs:
`.claude/hooks/stop_hook_patch.py` carries the correction and the commands that
disprove
the demand, `tests/unit/test_stop_hook_patch.py` holds it to what git actually
answers, and `PL-WW08` records the diagnosis.

**Done when.** The behaviour is reported to the container's maintainers with the
reproduction, and `docs/maintainer.md` records that it was - so a later session
neither re-reports it nor assumes it was done.
