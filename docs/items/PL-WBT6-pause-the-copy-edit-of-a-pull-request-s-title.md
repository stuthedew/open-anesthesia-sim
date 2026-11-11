---
id: PL-WBT6
title: Pause the copy edit of a pull request's title and body on a branch that changes no simulator path, until PL-BF6K has measured the copy editor's audit reads
priority: P2
effort: S
status: done
classes: session-cost
feature: copy-editor
touches: .claude/skills/pull-request/SKILL.md, docs/items/PL-BF6K-compare-the-copy-editor-s-first-read-with-its.md
added: 2026-11-11
closed: 2026-11-11
pr: 2093
payoff: a pull request of items and workflow files opens without a 15-minute, 12-run copy edit of its text
verify: grep -qF 'skips that copy edit' .claude/skills/pull-request/SKILL.md
---

**Problem.** Pause the copy edit of a pull request's title and body on a branch that changes no simulator path, until PL-BF6K has measured the copy editor's audit reads

**Why it matters.** The pull-request skill sends every pull request's title
and body through the copy editor, because the squash merge makes them the
commit message on `main` (project owner, 2026-11-10, `PL-N2VQ`). On `#2088`,
which changed item files and two workflow files, that edit of a 381-word
title and body took 12 model runs, 15 minutes and $2.75. The published text
kept three changes of wording from it, and one useful query. The owner said
on 2026-11-10 that the copy editor helps but takes a long time and uses many
tokens. A branch of items and workflow files is the commonest kind of pull
request and the one whose text fewest readers need.

**Decision.** A branch that changes no simulator path skips the copy edit of
its title and body, until `PL-BF6K` (compare the copy editor's first read
with its last) has its measurement (project owner, 2026-11-11 at 00:06 UTC,
ratified, over keeping the edit on every pull request). A pull request that
changes a simulator path keeps the edit. The owner specified the edit of
pull request text on 2026-11-10, so this narrows a decision of their own, at
their word.

**What changed.** `.claude/skills/pull-request/SKILL.md` § "Open the pull
request with the work" states the pause and how a session tells which branch
it covers: `python3 tools/blind_review.py --count` prints 0. `PL-BF6K`'s
brief now says to put the pause back to the owner with its result.
`.claude/rules/plain-writing.md`, `docs/prose-review/README.md` and close-out
step 8 still say that the copy editor edits pull request titles and bodies.
That stays true of a simulator pull request, and each of them leaves the
procedure to the pull-request skill, so none was edited.

**Done when.** The pull-request skill states the pause, its test and what
ends it.

**Generator check.** Work the owner asked for. It narrows part of the fix
built for `PL-J1ZM` (sessions over-explain in every kind of text), so the
pause on new workflow mechanisms does not hold it, and it builds none.
