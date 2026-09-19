---
id: PL-29HL
title: cli's verify passes no runner to default_base, so a git that does not answer leaves it comparing against a 'main' that may not resolve and verify reports a clean scope
status: untriaged
added: 2026-09-19
---

**Problem.** cli's verify passes no runner to default_base, so a git that does not answer leaves it comparing against a 'main' that may not resolve and verify reports a clean scope

**Found while building `PL-Q9Z1`'s failure channel, 2026-09-19.** Every read in
`subprojects/docket/src/docket/vcs.py` now wraps its runner in `_Silences`, so a
git call that did not answer reaches the report as `declined` even where the
helper that met the silence could not say so in its own return type.
`default_base` is one of those helpers: it answers with a ref name and falls
back to `"main"`, so its silence is only visible to a caller that watched the
runner it was handed.

`subprojects/docket/src/docket/cli.py:1455` is the one call site that hands it
none:

```python
base = args.base or default_base(root)
```

So under a git that does not answer, `verify` compares against a `"main"` that
may not resolve, `git diff main...HEAD` exits 128, `_run_git` gives the empty
string, and the commission audit reports no paths outside the item's `touches`
- a clean scope established from a read that never happened. That is
`.claude/rules/apparatus-standard.md`'s floor breached on the command whose
whole job is to certify a branch.

**Done when** `verify`'s base read declines rather than falling back silently,
and a fault-injection test drives it.
