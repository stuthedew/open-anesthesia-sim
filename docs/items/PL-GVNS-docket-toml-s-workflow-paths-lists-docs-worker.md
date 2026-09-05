---
id: PL-GVNS
title: docket.toml's workflow_paths lists docs/worker.md but not docs/maintainer.md, so an apparatus item whose record lands in the maintainer doc ranks in the product lane
priority: P3
effort: S
status: ready
classes: defect, infra
touches: docket.toml, subprojects/docket/tests/test_config.py
added: 2026-09-05
verify: uv run pytest subprojects/docket/tests/test_config.py && grep -q 'docs/maintainer.md' docket.toml
---

**Problem.** `docket.toml`'s `workflow_paths` names `docs/worker.md` — what a
session is told — and not `docs/maintainer.md`, its counterpart holding what
only the project owner can act on. Neither file is read by the simulator or by
a reader of it, so the omission looks like an oversight rather than one of the
four absences the block documents deliberately (`ROADMAP.md`,
`docs/releases/`, `docs/ARCHITECTURE.md`, `README.md`, each with its reason
written out).

**Why it matters.** `touches` decides an item's lane, so an item whose only
in-repository deliverable is a line in `docs/maintainer.md` is offered to
`docket next product` — a simulator session — and hidden from the apparatus
session that should take it. `PL-W9DW` (set an Actions spending limit and a
usage alert) is the live instance, filed 2026-09-05: pure CI-cost work whose
record belongs in the maintainer doc, currently ranked as product.

The failure is quiet in the way the lane split was built to avoid. Nothing
reports a mis-placed item; it simply appears in the wrong session's list,
correctly ranked and wrong, which is the shape `PL-0D4X` cost a session to.

**Where.** `docket.toml`, the `workflow_paths` block;
`subprojects/docket/tests/test_config.py`.

**One thing to settle rather than assume.** Whether `docs/maintainer.md` is
absent by oversight or by a judgment nobody wrote down — the block records a
reason for each of its four deliberate exclusions, and this has none, which is
the evidence for oversight but not proof of it. If it is deliberate, the fix is
the missing sentence rather than the missing entry.

**Done when.** `docs/maintainer.md` is either listed in `workflow_paths` or
recorded there as a deliberate exclusion with its reason, and `bin/docket next
workflow` offers `PL-W9DW`.
