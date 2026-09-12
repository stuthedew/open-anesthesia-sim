---
id: PL-B5YN
title: bin/docket verify reports FAIL item front matter unchanged on every self-audited close-out, because closing an item edits its own front matter
status: untriaged
added: 2026-09-12
---

**Problem.** bin/docket verify reports FAIL item front matter unchanged on every self-audited close-out, because closing an item edits its own front matter

**Observed 2026-09-12**, closing `PL-ZWBK`: `FAIL item front matter unchanged -
classes, closed, effort, feature, priority, status, touches, verify`. Every one
of those is an edit the close-out and the triage pass are *required* to make.

**Why the check is right and the result is still wrong.** `front_matter_check`
exists so that a delegated worker cannot mark its own item done, re-scope
`touches`, or rewrite the `verify:` command it was measured against - the
reviewer's fields. `PL-20PT` rebuilt it after it had reported PASS on every
branch there had ever been, so its strictness is hard-won and should not be
relaxed. But the session running `bin/docket verify` on its own close-out is
not a delegated worker: it *is* the reviewer, and the fields it moved are the
ones a close-out moves.

**So the check fires by construction on the one path a session is told to take.**
`.claude/skills/docket/SKILL.md`'s close-out asks for `status: done` and
`closed:` in the same commit as the work, and then the audit reports that as a
finding. That is the shape `CLAUDE.md` calls a defect in the check rather than
coverage - it trains a reader to skim a `FAIL` block in which the
protected-path line, the one that matters, also sits.

**Approach, undecided, and it is probably the same answer as `PL-4LT9` and
`PL-69JZ`.** All three are `docket verify` unable to tell a delegated branch
from a self-audit. A single distinction - the command being told, or working
out, which of the two it is looking at - would settle all three, and is worth
costing once rather than three times. The alternative worth pricing is
narrower: allow exactly the close-out's own field set (`status`, `closed`,
`milestone`, `pr`) to change while still refusing `touches` and `verify`, which
are the two that make the measurement meaningless.
