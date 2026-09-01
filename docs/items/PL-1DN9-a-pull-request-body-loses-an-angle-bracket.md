---
id: PL-1DN9
title: A pull request body loses an angle-bracket placeholder to HTML stripping, so a session ships a command that reads origin/ with no branch
status: untriaged
added: 2026-09-01
---

**Problem.** A pull request body loses an angle-bracket placeholder to HTML stripping, so a session ships a command that reads origin/ with no branch

**Why it matters.**

**Where.**

**Done when.**

**Observed 2026-09-01, on PR #132.** The body written for `PL-1Q3S` named the
fix as `git branch -dr origin/<branch>` in three places, inside code spans.
GitHub read `<branch>` as an HTML tag and dropped it, so the published body
read `the local `origin/` survives` and `the rule therefore names `git branch
-dr origin/``. The command a reviewer would have copied was not a command.

The committed `CLAUDE.md` text was unaffected - this is a property of the pull
request body, not of the repository - which is what makes it easy to miss: the
session verifies the file it wrote and never re-reads what GitHub published.

**Why it matters.** A pull request body is where the reviewer meets the change,
and a body naming a wrong git command is the same class of defect as a wrong
label on a displayed value: correct work, misrepresented at the point somebody
acts on it. It is silent - no error, no warning, and the create call returns
success - and it recurs, because `<branch>`, `<id>`, `<ref>` and `<version>`
are the natural way to write a placeholder.

**Candidate fixes, unranked.** Write placeholders as bare words (`BRANCH`);
or escape them; or re-read the body after creating a pull request and compare
it against what was sent, which is the only one that catches the general case
and could be a check rather than a habit. The re-read is cheap - the create
call already returns the number - but the comparison is not free of judgment,
since the server also rewrites the attribution footer.

**Where.** Not a repository file. It is a habit, and possibly a small check in
`tools/`, wherever the pull-request convention is written down.
