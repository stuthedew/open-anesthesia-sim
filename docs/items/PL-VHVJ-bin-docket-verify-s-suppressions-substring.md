---
id: PL-VHVJ
title: bin/docket verify's SUPPRESSIONS substring-matches xfail, so any diff line containing pytest's --maxfail option reads as a suppression and REJECTs correct work
priority: P2
effort: S
status: done
classes: defect
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-19
closed: 2026-09-19
pr: 711
verify: grep -q 'def test_a_pytest_option_containing_a_suppression_name_is_not_one' subprojects/docket/tests/test_verify.py
---

**Problem.** bin/docket verify's SUPPRESSIONS substring-matches xfail, so any diff line containing pytest's --maxfail option reads as a suppression and REJECTs correct work

**Where it comes from.** `PL-09G9`'s close-out audit, 2026-09-19. The branch
added one line listing the pytest options that consume the token after them:

    {"-n", "-p", "-o", "-c", "-r", "--dist", "--maxfail", "--durations", "--rootdir", "--ignore"}

`bin/docket verify --self` reported `FAIL  no suppression added - 1 line(s)`
against it. `SUPPRESSIONS` is matched with `s in line`, and `xfail` is a
substring of `--maxfail`, so a diff listing pytest's own `--maxfail` option
reads as a test being marked expected-to-fail.

**Why it matters.** Every entry in that tuple names a *token*, and only this
one can sit inside a longer word — but the cost is not confined to the one
collision. A `REJECT` on correct work is the failure `PL-69JZ` and `PL-7XTS`
already paid for once: it trains a reader to skim the block, and the block is
where a real protected-path or removed-assertion finding is printed. The four
integrity checks are the ones `--self` may not relax, so this is the half of
the audit that is supposed to be absolute, reporting a fault that is not there.

It is also the shape `.claude/rules/apparatus-standard.md`'s floor names: the
answer a session is handed has to be true. This one was confidently false, and
the only way past it was for the session to explain it away — which is the
routing-around `CLAUDE.md`'s second compounding-friction test describes.

**The fix.** Anchor each entry on the left with `\b`, and only where it begins
with a word character: two entries open on `#` and `@`, which are not word
characters, so `\b` before one of those asserts the opposite of what is wanted
and would match only where a word character precedes it. The right-hand side
stays open deliberately — `@skip` should still find `@skipif`.

Measured before and after over five lines: `--maxfail` stops matching and
`@pytest.mark.xfail`, `# type: ignore[misc]`, `pytest.skip("later")` and
`@skipif(True)` all still do. That is one behaviour change and no lost finding.

**Not `noqa`.** The comment above `SUPPRESSIONS` explains why that one is
deliberately absent, and nothing here reopens it: this is a matching bug in the
entries the list does carry.

**Done when** a diff line containing `--maxfail` no longer reports a
suppression, a real `xfail` still does, and both are pinned by test.
