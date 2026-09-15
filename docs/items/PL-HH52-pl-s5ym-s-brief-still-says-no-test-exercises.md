---
id: PL-HH52
title: PL-S5YM's brief still says no test exercises the covered-directory branch, but test_childless_directory_covers_its_whole_subtree has asserted the positive direction since PL-032, and #598's merge rewrote the item without correcting it
status: untriaged
added: 2026-09-15
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
