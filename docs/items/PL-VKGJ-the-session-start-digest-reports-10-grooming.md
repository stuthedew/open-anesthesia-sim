---
id: PL-VKGJ
title: The session-start digest reports 10 grooming advisories where bin/docket check reports 19, so a session is told the grooming debt is half its actual size
status: untriaged
added: 2026-09-19
---

**Problem.** The session-start digest and `bin/docket check` disagree on the
size of the grooming debt, and the digest is the one that under-reports.
Measured live 2026-09-19:

```
$ bin/docket digest | grep -i groom
  Grooming due: 10 advisories (`make docket` to see them).
$ bin/docket check | grep -cE 'records no .?pr.?, but #'
9
```

10 + 9 = 19. The cause is explicit in the source — `checks.py`, in the
`pr`-backfill check:

```python
if closures is None:  # a caller that did not ask; every command but `check`
    return
```

The digest never asks for closure data, so the nine `PL-xxxx: marked done on
origin/main and records no pr` advisories are structurally invisible to it. The
comment shows the guard is deliberate; nothing indicates the *count* the digest
prints was meant to exclude them.

**Why it matters.** This is a violation of the floor in
`.claude/rules/apparatus-standard.md`: "What this apparatus tells a session must
be true, or must say what it could not read. Handing over a partial reading as a
complete one is the violation, because at the point of use the two are
indistinguishable." The digest is on the answer-giving surface that floor binds,
and it is handing over a partial reading as a complete one.

The concrete consequence: a session told "Grooming due: 10" sizes its remaining
debt against 10, and a session that then runs `make docket` and sees 19 has been
misinformed by the one line it reads before anything else. `docket check` already
has the vocabulary for this case — `report.declined` exists so that what went
unread travels with the answer — and the digest path does not use it.

**Note on scope.** Two adjacent items already exist and this is neither of them:
`PL-XYQW` collapses the nine identical advisories into one line (a noise fix,
which would *also* change this count), and `PL-T8PT` concerns
`tools/pr_title_check.py`. Whichever of the three lands first should check
whether it has already resolved the others; if `PL-XYQW` collapses the nine to
one, the honest digest figure becomes 11 rather than 19 and this item reduces to
making the digest say which number it is reporting.
