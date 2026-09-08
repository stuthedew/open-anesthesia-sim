---
id: PL-20PT
title: bin/docket verify's item-front-matter guard compares git show <base>:<bare filename> because Item.path holds no directory, so the lookup always fails, the miss is swallowed as 'a new item file' and the check reports PASS on a branch that marked its own item done
status: untriaged
added: 2026-09-08
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
