---
id: PL-1DN9
title: A pull request body loses an angle-bracket placeholder to HTML stripping, so a session ships a command that reads origin/ with no branch
priority: P3
effort: S
status: done
classes: docs, session-cost
feature: dev-tooling
milestone: v0.4.3
touches: CLAUDE.md
added: 2026-09-01
closed: 2026-09-05
pr: 369
verify: grep -qF 'read the published body back' CLAUDE.md
---

**Problem.** A pull request body written with an angle-bracket placeholder
loses it to HTML stripping, silently. Observed 2026-09-01 on PR #132: the body
for `PL-1Q3S` named the fix as `git branch -dr origin/<branch>` in three
places, inside code spans. GitHub read `<branch>` as an HTML tag and dropped
it, so the published body read "the local `origin/` survives" and "the rule
therefore names `git branch -dr origin/`". The command a reviewer would have
copied was not a command.

The committed `CLAUDE.md` text was unaffected - this is a property of the pull
request body, not of the repository - which is what makes it easy to miss: the
session verifies the file it wrote and never re-reads what the server
published.

**Why it matters.** A pull request body is where the reviewer meets the change,
and one naming a wrong command is correct work misrepresented at the point
somebody acts on it. It is silent: no error, no warning, and the create call
returns success with the number. And it recurs, because `<branch>`, `<id>`,
`<ref>` and `<version>` are the natural way to write a placeholder. Angle
brackets are only the instance - any server-side rewriting of a body is
invisible to a session that does not read the result back.

**Where.** `CLAUDE.md`'s commit-and-push bullet, which is where a session meets
the pull-request convention before writing one. Not a check: nothing
repository-side runs at the moment a pull request is created, which is the same
reason `PL-1Q3S` landed as prose rather than as a hook. The marginal cost is a
clause on a bullet that is already resident, not a new bullet.

**Done when.** `CLAUDE.md` tells a session to read the published body back
after creating a pull request and compare it against what was sent, and says
why - the server rewrites bodies silently, so a placeholder can vanish with no
error anywhere. Writing placeholders as bare words is the narrower alternative
and does not close this: it fixes angle brackets and nothing else.

**Triaged 2026-09-01.** P3, `docs`/`session-cost`, `dev-tooling`. Not debt and
not a v0.2.8 gate entry: nothing in the tree is broken - the tool behaved as
documented, and what is missing is a convention. P3 rather than P2 because the
damage is bounded and correctable in place once seen; above `dropped` because
it is silent and does not heal. Contrast `PL-FLZ4` (the restart leaves a
dangling branch upstream), captured in the same session and dropped: that one
clears itself on the next push and this one does not.

The `verify:` command was run on the current tree before being written down and
exits 1, as it must until the clause exists.

**Closed 2026-09-05**, as a clause on the commit-and-push bullet rather than a
bullet of its own, which is where the brief placed it: that bullet is where a
session meets the pull-request convention, and the marginal cost is a sentence
rather than an entry.

**+337 resident characters, and the second of `doc_check`'s two answers is the
one this takes.** There is no cheaper carrier. A check cannot see it - nothing
repository-side runs when a pull request is created, which is the same reason
`PL-1Q3S` landed as prose - and neither a path-scoped rule nor the `docket`
skill fires at the moment in question, because writing a body is preceded by
no read of any file and is not a queue workflow. A session violates this before
it would think to look anything up, which is exactly the resident test.

Stated as *read the body back*, not *avoid angle brackets*. The narrower rule
fixes one instance of server-side rewriting and leaves every other kind
invisible, and the brief is explicit that it does not close this.

The `verify:` command was run on the tree and, on the first attempt, **failed
after the work was written** - the phrase had wrapped across two lines and
`grep -F` matches within one. The clause was rewrapped rather than the command
loosened: a phrase a reader can find in one line is what the command is
asserting.
