---
id: PL-P4XB
title: test_verify.py's _commission helper commits unconditionally, so calling it with fields identical to the base store's copy dies inside subprocess with CalledProcessError rather than saying nothing changed
priority: P3
effort: S
status: done
classes: defect, test
milestone: v0.5.4
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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground". No paragraph there named it apart from this entry line, so it rested on the section's opening ground, which is quoted in `PL-36R4`'s brief.

> - PL-P4XB (S) `test_verify.py`'s `_commission` helper commits unconditionally, so a call with fields identical to the base store's copy dies inside `subprocess` rather than saying nothing changed
