---
id: PL-73P0
title: default_base falls back to the literal string main when no candidate ref resolves, so every comparison in vcs.py can be taken against a guessed base with nothing in the answer saying so
priority: P2
effort: M
status: ready
classes: defect
feature: evidence-declines
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-19
verify: grep -q 'def test_default_base_declines_when_no_candidate_resolves' subprojects/docket/tests/test_vcs.py
---

**Problem.** default_base falls back to the literal string main when no candidate ref resolves, so every comparison in vcs.py can be taken against a guessed base with nothing in the answer saying so

**Found in `PL-BHVM`'s design round, 2026-09-19**, which carries the wider
diagnosis. `default_base` tries each of `DEFAULT_BRANCHES` and ends:

```python
return "main"
```

Its docstring calls this "a repository this tool cannot answer about either
way", and for `verify` that is true — it reports finding no change rather than
a clean scope. But `default_base` is the base every other read in the module
compares against, so the fallback is not confined to that caller: a checkout
where no candidate resolves still gets a string that looks like an answer, and
`stranded`, `orphaned`, `branches_in_flight` and `branch_state` then compare
against a branch nobody established exists.

Measured 2026-09-19: under a runner that fails every call, `default_base`
returns `'main'` and `branch_state` returns `behind=0, ahead=0` — "you are
current with the base" — from a base that was guessed.

**Why it matters.** `.claude/rules/apparatus-standard.md`'s floor is that what
the apparatus tells a session must be true or must say what it could not read.
A guessed base is the one input whose wrongness cannot be seen in any answer
downstream of it, because every downstream answer is *about* that base.

**Done when** a checkout where no candidate default branch resolves is
distinguishable from one where `main` resolved — a sentinel, an optional
return, or a declined flag on the reports that consume it — and the reads that
compare against it decline rather than answering. Sits with `PL-Q9Z1` and
`PL-MM7F`: all three are the evidence layer having no way to say it could not
answer.

**One concrete call site, folded in from `PL-29HL` (dropped as superseded,
2026-09-19).** `PL-Q9Z1` gave every read in the module a runner wrapped in
`_Silences`, so a call git did not answer reaches the report as `declined` even
where the helper that met it - `default_base` among them - cannot say so in its
own return type. That cover has exactly one hole, and it is the command whose
whole job is to certify a branch:

```python
base = args.base or default_base(root)  # subprojects/docket/src/docket/cli.py:1455
```

No runner, so nothing watches the probe. Under a git that does not answer,
`verify` compares against a `"main"` that may not resolve, `git diff
main...HEAD` exits 128, `_run_git` gives the empty string, and the commission
audit reports no paths outside the item's `touches` - a clean scope established
from a read that never happened. Whatever shape this item's answer takes, that
line is the one that has to consume it.
