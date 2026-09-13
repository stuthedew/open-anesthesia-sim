---
id: PL-GVNS
title: docket.toml's workflow_paths lists docs/worker.md but not docs/maintainer.md, so an apparatus item whose record lands in the maintainer doc ranks in the product lane
priority: P3
effort: S
status: done
classes: defect, infra
touches: docket.toml, tests/unit/test_workflow_paths_check.py
added: 2026-09-05
closed: 2026-09-13
verify: uv run pytest tests/unit/test_workflow_paths_check.py && grep -q 'docs/maintainer.md' docket.toml
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

**Settled: oversight, not judgment.** The block's four deliberate absences are
each a product path — `ROADMAP.md` and `docs/releases/` are product direction,
`docs/ARCHITECTURE.md` and `README.md` are written for a reader of the
simulator. `docs/maintainer.md` is neither. It is the declared counterpart of
`docs/worker.md`, which the list already carries: worker.md holds what a session
is told, maintainer.md what only the project owner can act on, and `CLAUDE.md`
routes to both in the same sentence. Nothing in the simulator or its
documentation reads either. So the entry was added, with a comment saying why it
is in rather than a fifth absence.

**The `PL-W9DW` half of "Done when" was already moot, and its premise was wrong
twice over.** `PL-W9DW` (set an Actions spending limit and a usage alert) closed
`done` under milestone v0.4.2 on 2026-09-05, the same day this item was filed,
so no lane can offer it at all; and its `touches` was `.github/workflows/quality.yml`
rather than `docs/maintainer.md`, so the entry added here would not have moved
it even while it was open. The project owner adds that the item's own problem
statement was untrue: it predates the repository going public and a limit was
already set.

**The live instances are `PL-90CJ` and `PL-TPS7`, measured through `Item.lane`
against this repository's real settings.** `PL-90CJ` (report the container stop
hook's stale-ref unpushed count upstream) declares `docs/maintainer.md` and
nothing else, and moves `product` -> `workflow`: apparatus work end to end that
was being offered to a simulator session and hidden from the apparatus one.
`PL-TPS7` (cut the prose in `docs/ARCHITECTURE.md` and `docs/maintainer.md`)
moves `product` -> `crossing`, which is also right — one reader-facing document
and one owner-facing one are two jobs, and the `crossing` set is where an item
waits for a session that can hold both.

**Done.** `docs/maintainer.md` added to `docket.toml`'s `workflow_paths` with
the reason beside it, and pinned by
`tests/unit/test_workflow_paths_check.py::test_the_owners_own_notes_are_apparatus_like_the_workers`,
which asserts through `Item.lane` — the code that actually decides which session
`bin/docket next` offers an item to — rather than through `is_covered`. Verified
failing before the config change (`+ product`) and passing after.
