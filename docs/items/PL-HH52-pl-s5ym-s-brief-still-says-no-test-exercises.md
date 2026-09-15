---
id: PL-HH52
title: PL-S5YM's brief still says no test exercises the covered-directory branch, but test_childless_directory_covers_its_whole_subtree has asserted the positive direction since PL-032, and #598's merge rewrote the item without correcting it
priority: P3
effort: S
status: dropped
classes: docs
touches: docs/items/
added: 2026-09-15
closed: 2026-09-15
not-delegable: The outcome was produced by #599 on `origin/main`, not by this
  branch, so no command run against this tree distinguishes a branch that did the
  work from one that did not. `git show origin/main:docs/items/PL-S5YM-...md` is
  what was checked.
reason: Superseded by PL-Y1W6 (#599), merged as f3c83ebf. This item was filed as
  insurance in case that branch was closed unmerged; it was merged instead, and
  the correction it carries is the one this item asked for.
---

**Problem.** PL-S5YM's brief still says no test exercises the covered-directory branch, but test_childless_directory_covers_its_whole_subtree has asserted the positive direction since PL-032, and #598's merge rewrote the item without correcting it

**Why it matters.** `PL-S5YM` is open and `ready`. Whoever starts it reads its
**Problem.** section, which says of the three covered-directory code paths:
"None is exercised by `tests/unit/test_doc_check.py`". That is false and was
false when written. `test_childless_directory_covers_its_whole_subtree` sits at
`tests/unit/test_doc_check.py:208` and asserts the positive direction against a
fixture whose tree draws `harness/` bare with `run.py` beneath it.

What is genuinely missing is only the **negative** direction - that a file
*outside* a childless directory still needs its own line - which the item's own
**Approach.** section asks for. So the item overstates its own scope by half,
and a session acting on the brief would write a duplicate of a test that
already passes.

**How it survived.** Three sessions diagnosed the red `main` this item's stale
`verify:` caused (`PL-99YZ`). Only one of the three - `#599`, `PL-Y1W6` -
noticed the false claim and corrected it in place. `#598` (`PL-B5VM`) is the
one that merged, and it rewrote the item's `verify:` and added an account of
the selector failure without touching the sentence. Confirmed on `origin/main`
at `17403970`: the claim is still there at lines 18-19, and the test is still
at line 208.

`#599` remains open as of filing and carries the correction; if it is merged
this item is already done, and if it is closed unmerged the correction has to
be made here. Check before starting.

**Done when.** `PL-S5YM`'s **Problem.** section names
`test_childless_directory_covers_its_whole_subtree` as already covering the
positive direction, and scopes the item to the negative direction and the
`docs/ARCHITECTURE.md` clause its **Done when.** already names.

**Update, same hour: `#599` is now doing exactly this.** That pull request was
repurposed at 23:05 — retitled "PL-Y1W6: drop as a duplicate of PL-B5VM, and
correct PL-S5YM's brief", with `origin/main` merged in, `PL-Y1W6` dropped as a
duplicate of `PL-B5VM`, and the brief correction kept as the one thing `#598`
did not find. Its commit message also reports a second false line this item did
not name: `PL-B5VM`'s own brief says "`covered_dirs` appears nowhere in
`tests/unit/test_doc_check.py`", which is true of the symbol and not of the
behaviour.

So **this item is insurance, not work**: it closes the moment `#599` merges,
and is only startable if `#599` is closed unmerged. Check that first. It is
kept rather than dropped because the correction would otherwise exist on one
unlanded branch alone, which is how `PL-99YZ` describes this whole episode
going wrong.

**Closed 2026-09-15, having done nothing, which is the right outcome.** `#599`
merged as `f3c83ebf` and `PL-S5YM`'s brief on `origin/main` now reads:

```
`test_childless_directory_covers_its_whole_subtree` (line 208, there since
`PL-032`) asserts that a file *beneath* a childless directory needs no line,
```

with its own note recording what the **Problem.** paragraph used to claim.
`dropped` rather than `done` because this branch produced none of it - the
project's convention for a finding another branch resolved first, and the same
one `#600` took for `PL-7VSK` and `PL-MR6S` in the same hour.
