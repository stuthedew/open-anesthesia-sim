---
id: PL-20PT
title: bin/docket verify's item-front-matter guard compares git show <base>:<bare filename> because Item.path holds no directory, so the lookup always fails, the miss is swallowed as 'a new item file' and the check reports PASS on a branch that marked its own item done
priority: P2
effort: S
status: done
classes: defect, infra
feature: delegation
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/model.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md, docs/worker.md
added: 2026-09-08
closed: 2026-09-08
pr: 483
verify: uv run pytest subprojects/docket/tests/test_verify.py && grep -q 'def test_a_branch_that_edits_its_own_front_matter_is_refused' subprojects/docket/tests/test_verify.py
---

**Problem.** bin/docket verify's item-front-matter guard compares git show <base>:<bare filename> because Item.path holds no directory, so the lookup always fails, the miss is swallowed as 'a new item file' and the check reports PASS on a branch that marked its own item done

**The mechanism, measured rather than reasoned.** `Item.path` is the item
file's *bare filename* — `PL-W8XP-an-item-blocked-on-a-milestone-being-scoped.md`
— with no directory, as `store.read_items` sets it. `verify._front_matter_changed`
builds `git show {base}:{item.path}` from it, so the ref it asks for does not
exist at any base:

```
$ git show "origin/main:PL-W8XP-an-item-blocked-on-a-milestone-being-scoped.md"
exit 128
$ git show "origin/main:docs/items/PL-W8XP-an-item-blocked-on-a-milestone-being-scoped.md"
status: ready
```

The non-zero status is then swallowed by the branch meant for a genuinely new
item — `return ()  # a new item file has no previous front matter to differ
from` — and an empty tuple is indistinguishable from "nothing changed". So the
check renders `PASS  item front matter unchanged - unchanged`.

**Why it matters, and why it is not merely a bug.** `bin/docket verify` is the
delegation audit, and this is the guard that stops a delegated worker reporting
on a commission other than the one it was given: marking its own item `done`,
re-scoping `touches` to cover what it actually edited, or rewriting the
`verify:` command it was measured against. All three of those are exactly what
it cannot currently see. It has never been able to: the guard has no test that
constructs a front-matter change and asserts the guard notices, which is the
`test_checks.py` convention — "a checker that has only ever run against a clean
store proves nothing".

A check that fires on nothing is a lesser problem than one that *passes* on
everything. This one prints a green line asserting a property nobody verified,
beside checks that are real, which is `CLAUDE.md`'s first compounding-friction
test — a check passes while the guarantee it stands for is void.

**Where.** `subprojects/docket/src/docket/verify.py` — `_front_matter_changed`
at the `git show` call, and the `status != 0` branch that hides the miss.
`subprojects/docket/src/docket/store.py` sets `path`, and is the other end of
the choice.

**Two fixes, and they are not equivalent.** Resolving the path at the call site
— joining the store directory before the `git show` — is the smaller change and
leaves `Item.path` meaning what every other reader already assumes. Making
`Item.path` repo-relative is the larger one and would touch every consumer,
including `_where` in `checks.py`, whose messages currently read
`PL-ZZZ9-....md: blocked by ...` rather than `docs/items/PL-ZZZ9-....md`.
Prefer the first unless a survey of the consumers says otherwise; that survey
is part of the work.

Whichever is taken, `status != 0` must stop meaning "new file" on its own. A
path that resolves and a path that does not are different failures, and the
one that cannot be distinguished from success is the defect here.

**Done when.** A branch that changes an item's `status`, `touches` or `verify`
fails `bin/docket verify`'s front-matter check, asserted by a test that
constructs exactly that branch; a genuinely new item file still passes; and an
unresolvable path is reported rather than treated as either.

**Found.** 2026-09-08, closing `PL-W8XP` (blocked-by may name a milestone).
That branch changed `PL-W8XP`'s own `status`, `touches` and `closed`, and
`bin/docket verify PL-W8XP` reported `PASS  item front matter unchanged -
unchanged` for all three.

**Fixed.** 2026-09-08. The survey the brief asked for says the smaller route
is the right one: `Item.path` has exactly one producer (`store.read_items`,
setting `path.name`) and every other consumer already assumes a bare filename
— `cli.py` joins it to the store directory twice, `checks.py`'s `_where` uses
it as a message prefix, and `verify_item`'s own-file exemption takes its
basename. The repo-relative `path` values in `test_vcs.py` belong to
`StrandedItem` and `LostItem`, which are separate types. So the join happens at
the call site, and `Item.path` now carries the field comment it never had —
the field's meaning being unwritten is how the two spellings came to exist.

`_front_matter_changed` is replaced by `front_matter_check`, which returns the
`Check` rather than the changed keys. That is the substance of the fix: the
third outcome had nowhere to go, so "could not look" was returned as the empty
tuple that "looked, found nothing" returns. It now refuses — an item file that
resolves to nothing, and a base holding no store at all, are both FAIL with the
path named. A file the base does not hold is still a pass, since an item
captured on the branch that works it has no earlier commission.

Two things beyond the brief, both cheap and both closing the same hole. The
base copy is found by **id** rather than by name, because `store.write_item`
renames the file when the title changes — and the title is front matter, so a
lookup by current name would have missed the one edit that moves the file out
from under the guard. And `docs/worker.md` gains the prohibition it never
stated: the `**Worked.**` note goes below the fence, and `status`, `touches`
and `verify:` are the reviewer's. The guard had nothing to point at.

Measured: the seven new cases in `tests/test_verify.py` all fail against the
unfixed `verify.py` and pass against the fixed one. The fixture now seeds
`docs/items/` at the base commit, which every earlier test in the file lacked —
"a checker that has only ever run against a clean store proves nothing" applied
to the fixture itself.
