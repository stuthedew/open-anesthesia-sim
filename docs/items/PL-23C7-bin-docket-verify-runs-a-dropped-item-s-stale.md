---
id: PL-23C7
title: bin/docket verify runs a dropped item's stale verify: command and REJECTs the close-out on it - dropping PL-XQGH, PL-CNJH and PL-2DTK against PL-4W2L's decision REJECTed on their test-name greps with make check green
status: dropped
feature: verify-false-reject
touches: subprojects/docket/src/docket/verify.py
added: 2026-09-22
closed: 2026-09-23
reason: Duplicate of PL-BX1C (bin/docket verify runs a dropped item's stale verify: command and REJECTs the close-out on it), which is the surviving item: the same mechanism - _check_item in verify.py applies the dropped exemption only when verify: is absent, so a recorded command still runs - with the same file and the same fix, and docket new already recorded this capture as PL-BX1C's recurrence on 2026-09-22. This brief keeps the new evidence: #922's three REJECTs (PL-XQGH, PL-CNJH, PL-2DTK) with make check green, those greps passing since #929, a 2026-09-23 reproduction on dropped PL-4FD2, and 38 of 191 dropped items still carrying a verify:.
---

**Problem.** bin/docket verify runs a dropped item's stale verify: command and REJECTs the close-out on it - dropping PL-XQGH, PL-CNJH and PL-2DTK against PL-4W2L's decision REJECTed on their test-name greps with make check green

**The occurrence, from `#922` (e2316a46, 2026-09-22).** That commit dropped
`PL-XQGH`, `PL-CNJH` and `PL-2DTK` against `PL-4W2L`'s decision and recorded
`bin/docket verify --self PL-XQGH PL-CNJH PL-2DTK` in its message: every
integrity check passed, `make check` passed, and each item REJECTed on its own
`verify:` alone, a grep for a test the build had not written yet. `docket new`
recorded this capture as a recurrence on `PL-BX1C` in the same commit.

**Reproduced 2026-09-23.** Those three no longer fire. `PL-4W2L`'s build
(`#929`) added exactly the three test names their greps look for, so all three
commands now exit 0 and the same audit would ACCEPT. A dropped item's verdict
flipped on later work that had nothing to do with the drop, so its command
proves nothing about it in either direction. The defect itself is unchanged.
`verify_item`, the per-item half of `bin/docket verify --self`, was run
in-process so that `make check` did not run, on dropped `PL-4FD2` against
`7c33f0e1^`. No suppression added and no assertion removed both passed, and
the commission checks printed as notes. Then it printed
``FAIL  `verify:` command passes - grep -q 'def test_prose_naming_a_suppression_is_not_a_suppression' ...``
and `REJECT`. The cause is `_check_item` in
`subprojects/docket/src/docket/verify.py`. It computes the dropped exemption
but applies it only under `if not item.verify`, so a recorded command still
runs as an integrity check. 38 of `origin/main`'s 191 dropped items carry a
`verify:` today, against 29 of 170 after `PL-PT7M`'s deletions on 2026-09-21.

**Generator check.** A re-filing of the open `PL-BX1C`, not an instance of a
closed head. It is the same function, guard and fix, and `docket new` matched
it there as that item's first recurrence. The three drops that fired it were
`PL-G21K`'s members, but what fired was `PL-BX1C`'s exemption keyed on the
field's absence rather than the item's status. `PL-G21K`'s mechanism, intent
inferred from diff text, played no part. This is one item filed twice, so it
is not a generator.
