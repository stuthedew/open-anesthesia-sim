---
id: PL-P4XB
title: test_verify.py's _commission helper commits unconditionally, so calling it with fields identical to the base store's copy dies inside subprocess with CalledProcessError rather than saying nothing changed
priority: P3
effort: S
status: done
classes: defect, test
touches: subprojects/docket/tests/test_verify.py
added: 2026-09-20
closed: 2026-09-22
pr: 893
payoff: the next author calling _commission with unchanged fields reads what happened instead of a CalledProcessError four frames inside subprocess
verify: grep -qE 'allow-empty|nothing changed' subprojects/docket/tests/test_verify.py
---

**Problem.** test_verify.py's _commission helper commits unconditionally, so calling it with fields identical to the base store's copy dies inside subprocess with CalledProcessError rather than saying nothing changed

**Found 2026-09-20** while writing `PL-ZMGR`'s tests. `_commission` rewrites an
item in the store and runs `git commit`, which exits 1 when the rewrite changed
nothing — so a test that means "the base holds this item at `status: ready`",
which is already `_repo`'s default, fails with

```text
subprocess.CalledProcessError: Command '['git', 'commit', '-qm',
'commission PL-K7QX']' returned non-zero exit status 1
```

four frames inside `subprocess`, naming neither the helper nor the test. The
call was dropped in that one test instead, which is correct there and does not
help the next author.

Small and apparatus-side, so the bar is the one
`.claude/rules/apparatus-standard.md` sets: worth doing only if it is a line or
two. A guard in `_commission` that says what happened — or `--allow-empty`,
which keeps the base ref count the calling tests' `HEAD~1` depends on — are both
that size. Not a behaviour change: no existing test passes a no-op rewrite.

**Why it matters.** The failure surfaces four frames inside `subprocess`,
naming neither the helper nor the test that called it, so the next author reads
a `CalledProcessError` from `git commit` and looks for a git problem. That is
the apparatus floor in `.claude/rules/apparatus-standard.md`: what the
apparatus tells a session must be true or must say what it could not do, and a
helper that dies rather than saying "nothing changed" fails it in the cheapest
possible place to fix.

**Reproduced 2026-09-20.** `subprojects/docket/tests/test_verify.py`'s
`_commission` runs `git commit` unconditionally after the rewrite, and neither
`--allow-empty` nor any guard on an unchanged tree appears in the file.

**Done when.** Calling `_commission` with fields the base store already records
either says so or commits empty rather than raising out of `subprocess`, the
base ref count the calling tests' `HEAD~1` depends on is unchanged, and the
repair is the line or two `.claude/rules/apparatus-standard.md` allows rather
than a rework of the helper.
