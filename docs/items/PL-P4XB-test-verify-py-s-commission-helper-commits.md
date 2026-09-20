---
id: PL-P4XB
title: test_verify.py's _commission helper commits unconditionally, so calling it with fields identical to the base store's copy dies inside subprocess with CalledProcessError rather than saying nothing changed
status: untriaged
added: 2026-09-20
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
