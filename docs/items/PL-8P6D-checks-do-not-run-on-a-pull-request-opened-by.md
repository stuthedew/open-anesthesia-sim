---
id: PL-8P6D
title: Checks refuse a pull request whose branch carries no item id, so the owner's own web edits and any contributor's pull request fail CI
priority: P2
effort: S
status: needs-decision
classes: defect, infra
feature: public-readiness
touches: tools/branch_id_check.py, .github/workflows/quality.yml, tests/unit/test_branch_id_check.py
added: 2026-09-06
---

**Problem.** Reported by the project owner, 2026-09-06, as "current checks only
allow for claude PR requests". Diagnosed the same day, against the runs rather
than from the tree alone: the checks *run* on a non-agent pull request. They
refuse it.

`tools/branch_id_check.py` fails a branch ahead of the default base that
carries no `PL-` id in its branch name and leads no commit subject with one.
Observed on #394 ("Add pre-release warning to README", branch
`stuthedew-patch-1`, opened by the owner from the GitHub web UI), where the
`checks` job ran and exited 1 after nine seconds at the floor step:

```
branch-id: 2 commit(s) ahead of origin/main, and no item id names any of them.
  branch: stuthedew-patch-1
```

`pr-title` passed on the same head, correctly - the branch closes no item, so
`pr_title_check.py` owes it no id. `branch_id_check.py` is the whole wall.

Nothing else was implicated, and each was checked rather than assumed:

- Both `pull_request` triggers are unfiltered. `quality.yml` fires on `push:
  branches: [main]` and a bare `pull_request:`; `pr-title.yml` on
  `pull_request: types: [opened, synchronize, reopened, edited]`. Neither
  filters by author, head branch or association, and `quality.yml`'s `checks`
  job carries no `if:`.
- No repository setting is involved. The fork-approval hypothesis does not
  apply: #394 was a same-repository branch, and its run started six seconds
  after the pull request opened.
- Authorship cannot be the discriminator at all. Every pull request in this
  repository is authored by `stuthedew`, because agent sessions open theirs
  under the owner's account. The only thing separating an agent pull request
  from a hand-made one is the branch name and the commit subjects - which is
  exactly what `branch_id_check.py` reads.

**Why it matters.** The rule is an agent-session convention enforced against
everyone. `branch_id_check.py`'s own docstring justifies it by what `docket
flight`, `show`, `next`, `concurrent` and the session-start digest can see -
guards that exist so two concurrent agent sessions do not duplicate work. A
contributor has no queue, no id, and no reason to have one, and the remedy the
failure prints asks them to run `bin/docket new` and amend their commit. The
repository is public as of 2026-09-06, so this sits directly on the path of
the first drive-by pull request, and a red required check is what a
contributor sees rather than an explanation. It also blocks the owner's own
one-line web-UI edits, which is how it was found.

**Where.** `tools/branch_id_check.py`; the floor section of
`.github/workflows/quality.yml` that runs it before `setup-uv`; whatever in
`tests/unit/` covers it; `CONTRIBUTING`-facing docs if the answer is partly
"say so to contributors".

**Done when.** The rule binds the sessions it was written for and nobody else,
and a pull request opened by the owner by hand or by an outside contributor
can go green without filing a queue item. The decision this needs first is
*how* to scope it, and the candidates are not equivalent:

1. Scope the CI step to agent branches - run it only where `github.head_ref`
   matches the `claude/` prefix the sessions use. Matches the docstring's own
   justification, and leaves `make check` failing locally for every session
   regardless, which is where the guard actually earns its place.
2. Demote it to a non-failing annotation on CI and keep the hard failure in
   `make check` only. Weaker: an agent session that never runs `make check`
   before pushing is the case the CI half exists to catch.
3. Gate on author association rather than branch name. Fragile here, since
   every pull request has the same author.

Whichever is chosen, add the regression test for the case that produced this:
a branch ahead of the base with no id anywhere, opened as a pull request,
passing. Do not treat "a contributor should file an item" as the answer -
requiring a queue entry to fix a README typo converts the queue into a log,
which `branch_id_check.py`'s own docstring already refuses to do.

**Decision needed.** How is `branch_id_check.py` scoped so that it binds the
agent sessions it was written for and nobody else? The brief's three
candidates, and they are not equivalent: run the CI step only where
`github.head_ref` matches the `claude/` prefix; demote it to a non-failing
annotation on CI while keeping the hard failure in `make check`; or gate on
author association, which is fragile here because every pull request carries
the same author. Whichever is chosen, the regression test is a branch ahead of
the base with no id anywhere, opened as a pull request, passing.
