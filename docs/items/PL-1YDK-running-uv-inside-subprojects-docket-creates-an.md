---
id: PL-1YDK
title: Running uv inside subprojects/docket creates an untracked second uv.lock that nothing ignores
status: untriaged
added: 2026-09-01
---

**Problem.** `subprojects/docket/pyproject.toml` makes that directory a uv
project in its own right, so `uv run pytest ...` executed from inside it
resolves and writes `subprojects/docket/uv.lock`. The repository has no
`.gitignore` entry for it - `grep -n "uv.lock" .gitignore` matches nothing -
so the file lands in `git status` as untracked, beside the root `uv.lock` that
is tracked.

**Why it matters.** Two failure shapes, and the second is the expensive one.
A session that runs `git add -A` commits a second lock file which nobody
maintains and which will drift from the root's silently. And a session that
does not commit it still reads an unexplained untracked file in `git status`
while deciding what its own diff contains, which is exactly the moment a
stray file gets swept in.

It is easy to reach. Every `verify:` command in the store is written to run
from the repository root, but a session that has `cd`ed into the subproject to
read the code - or that copies a command shown in `subprojects/docket/README.md` -
runs it from there instead. That happened while closing `PL-Q2BJ` (2026-09-01),
which is how this was found.

**Where.** `.gitignore` at the repository root, which does not exist as a
tracked file today for this purpose - check before assuming. The alternative
is deciding the subproject should carry a committed lock of its own, which is
a different answer and a larger one: it makes `subprojects/docket` separately
installable and separately pinned, which nothing currently wants.

**Done when.** Running the docket test suite from inside `subprojects/docket`
leaves `git status` clean, and the decision - ignore it, or track it
deliberately - is recorded rather than implied.
