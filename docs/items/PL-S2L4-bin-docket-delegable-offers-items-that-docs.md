---
id: PL-S2L4
title: bin/docket delegable offers items that docs/worker.md forbids a worker to touch
priority: P3
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: docket.toml, docs/worker.md, subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_model.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
added: 2026-08-30
closed: 2026-09-08
verify: uv run pytest subprojects/docket/tests/test_model.py subprojects/docket/tests/test_cli.py && grep -q 'def test_an_item_touching_the_checks_themselves_is_not_delegable' subprojects/docket/tests/test_model.py
---

**Problem.** Two lists say what a delegated worker may not edit, and they
disagree. `docket.toml`'s `protected_paths` names the scientific paths -
`src/anesthesia_sim/core`, `src/anesthesia_sim/data`, `docs/MODEL.md` - and is
what `Item.delegability` reads. `docs/worker.md` adds a second, wider rule the
worker is told to obey: "**Never edit the checks themselves**: `Makefile`,
`pyproject.toml`, `.github/workflows/`, `.claude/`, `docket.toml`."

Nothing reads the second list. So `bin/docket delegable` offered PL-F5HB (the
Python 3.14 release-candidate fix) as work for a cheaper model while that
item's `touches` named `pyproject.toml`, which `docs/worker.md` forbids the
same worker to open. The worker would have had to break its own instructions
or return the item unfinished.

**Why it matters.** `delegable` exists so a session can hand work off without
reading the queue. A list that includes work the worker is forbidden to do
makes the command untrustworthy in exactly the case it was built for, and the
contradiction surfaces only after a worker has been spawned and has read its
brief.

**Where.** `docket.toml` (`protected_paths`), `docs/worker.md` (the "Never
edit the checks themselves" bullet), and
`subprojects/docket/src/docket/model.py` (`Item.delegability`,
`_is_protected`).

**Measured.** 2026-09-08, on `main` at the branch point, before any change:

- `bin/docket delegable` offers 86 open items. Fifteen of them declare a
  `touches` path inside `config.gate_paths` - `PL-483K`, `PL-6YYR`, `PL-7QKY`,
  `PL-8MJ3`, `PL-8XPQ`, `PL-CQRL`, `PL-G8TR`, `PL-GVC0`, `PL-GVNS`, `PL-HKF4`,
  `PL-K2C8`, `PL-S2L4`, `PL-TFWR`, `PL-VYK1`, `PL-YKXQ`. This item is one of
  them, and seven of the fifteen declare `.claude/skills/docket/SKILL.md`.
- There are **three** lists, not two. `gate_paths` already exists in
  `subprojects/docket/src/docket/config.py` and already holds exactly the
  paths `docs/worker.md` names, minus one: `Makefile`, `pyproject.toml`,
  `.github`, `.claude`, `docket.toml`. `docs/worker.md` also forbids `any
  ruff.toml`, which `gate_paths` does not cover, so a delegated diff relaxing
  `tools/ruff.toml` or `subprojects/docket/ruff.toml` passes the audit today.
- `verify.py` already fails such a diff outright - the check named "the checks
  themselves are unedited" reads `gate_paths` and is absolute. So each of the
  fifteen is work that `bin/docket verify` would REJECT after a worker had
  finished it, which is what settles the block-or-warn question below: the
  audit is already a block, and `delegable` disagreeing with it is the defect.
- This item's own `verify:` command selects nothing. `uv run pytest
  subprojects/docket/tests/test_model.py -k check_paths` exits 5 on
  "38 deselected / 0 selected" - the bare-`-k` shape the `docket` skill names.
  It is rewritten in the paired shape as part of the work.

**Approach.** One list has to become the other's source, and the source is
`gate_paths` rather than `protected_paths` (project owner, 2026-09-08). The
sketch this item was captured with - fold the check paths into
`protected_paths` - was put aside for three reasons found in the measurement
above. It would write a third statement of the list rather than removing the
second. It would make `verify`'s "no protected path modified" check fail for
a `Makefile` edit, which is a safety signal firing for a non-safety cause and
the surest way to teach a reader to skim it; `render.py` prints
`protected_paths` verbatim to a triaging session as the clinical-output rule,
so the same sentence would come to read `Makefile, docket.toml, ...`. And
`docket` is a subproject shared with other repositories, so a fix living only
in this repository's config leaves the defect in the package.

Block rather than warn, and that was not a judgment call in the end: `verify`
is already an absolute block on these paths, so a warning here would mean
offering work the acceptance audit is certain to refuse.

**Built.**

1. `Item.delegability` takes `gate_paths` beside `protected_paths` and refuses
   on either, with its own reason string - `touches the checks themselves: X`
   against `touches protected path(s) X` - reported second, so the clinical
   prohibition is the one a reader meets first when both apply. The two lists
   are read differently when empty, which the docstring and a test both carry:
   an empty `protected_paths` means a project never declared one and delegation
   closes, while an empty `gate_paths` can only mean a real default was cleared
   deliberately.
2. `docket.toml` writes `gate_paths` out - the five package defaults plus
   `tools/ruff.toml` and `subprojects/docket/ruff.toml`, which `docs/worker.md`
   forbade and no configured list covered. `.claude/hooks/ruff.toml` needs no
   entry, being under `.claude`.
3. `docs/worker.md` cites that list instead of restating it.
4. `format_delegable`'s empty answer and `bin/docket triage`'s printed rules
   name both prohibitions. The triage rule is nested inside the protected-paths
   one: where delegation is closed entirely there is nothing to qualify.
5. `subprojects/docket/tests/test_cli.py` carries the end-to-end guard - an
   item touching `Makefile`, withheld from `bin/docket delegable` through the
   package default rather than through the store's own config, which is the
   only thing that can catch a call site that forgets to pass the list.

**Done when.** An item whose `touches` names a path `docs/worker.md` forbids
is not listed by `bin/docket delegable`, and the prohibition is stated in one
place rather than two.
