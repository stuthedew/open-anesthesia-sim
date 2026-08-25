---
id: PL-G3TG
title: Add a `verify:` command to the item format and derive delegability from it
priority: P2
effort: M
status: ready
classes: infra, session-cost
feature: delegation
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_model.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md, docket.toml
added: 2026-08-25
---

**Problem.** An item states what "done" means in prose, under **Done when.**,
which a person reads and no tool can act on. There is no field naming the
command that would prove the work correct, so nothing can distinguish an item
whose success is mechanically demonstrable from one that needs a reviewer's
judgment.

**Why it matters.** It is the prerequisite for delegating work to a cheaper
model at all, and it pays for itself with no delegation whatsoever: an item
carrying its own proof command makes close-out mechanical instead of
remembered. Without it, "is this finished" is re-derived by every session that
asks.

**Where.** `subprojects/docket/src/docket/model.py` (the `Item` dataclass, its
`known` field set, `render_item`'s fixed field order, and a derived property
beside `model_guidance`), `checks.py` (`_check_item`), `config.py` (a
`protected_paths` setting), `render.py` (surface it where `model_guidance`
already appears), `docket.toml`, and `subprojects/docket/README.md`'s item
format section.

**First step.** Add two front-matter fields — `verify:`, a single-line shell
command, and `delegable:`, which accepts only `no` — then write
`Item.delegability` as a derived property. An item is delegable when all of:
`status: ready`; a non-empty `verify:`; a non-empty `touches` wholly disjoint
from `config.protected_paths`; `effort` in `S`/`M`; no `model_guidance` (so
safety- and science-classed work and open decisions are excluded by the rule
that already exists); and no `delegable: no`.

Set `protected_paths` in `docket.toml` to `src/anesthesia_sim/core/`,
`src/anesthesia_sim/data/`, and `docs/MODEL.md`. This partition is absolute
and is not overridable by a passing check: a delegated diff may add tests
*about* those paths but may never edit them, so no change to a displayed
clinical value can land on a diff nobody read. Deleting a dead method in
`core/` is excluded by this even though its check would be sound; that cost is
accepted deliberately.

Note the deliberate asymmetry: there is no `delegable: yes`. Delegability is
derived from facts and can only ever be *withheld*, never granted, so no
session — least of all a worker tidying front matter on its way past — can
mark its own work eligible. `delegable: no` requires a `reason`.

Surface the result where `model_guidance` already appears, so `docket list`
and `docket next` mark a delegable item as such. A dedicated `--delegable`
filter is deliberately out of scope until the pilot shows the queue is big
enough to need one.

**Done when.** `Item.delegability` is derived rather than stored, the
protected partition is configured and enforced, `docket check` rejects
`delegable: no` without a reason, the README documents the field and the
partition, and the 23 existing items still validate untouched (absence of
`verify:` means not delegable, which is the safe default).
