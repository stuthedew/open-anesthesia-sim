---
id: PL-1YDK
title: Running uv inside subprojects/docket creates an untracked second uv.lock that nothing ignores
priority: P3
effort: S
classes: infra
feature: dev-tooling
touches: .gitignore
verify: git check-ignore -q subprojects/docket/uv.lock
status: dropped
added: 2026-09-01
closed: 2026-09-13
reason: superseded by `PL-8PT6`, which landed the identical fix in #515 without knowing this item existed. The two are one finding filed twice - same path, same `.gitignore` entry, same approach - and `PL-8PT6` even adopted this item's `verify:` command verbatim as half of its own. Dropped rather than marked done because neither this item nor the branch that closes it did the work; what satisfies its `Done when` is `.gitignore:28`, `/subprojects/docket/uv.lock`, anchored exactly as this item anticipated ("a `subprojects/*/uv.lock` glob satisfies it as readily as the literal path"). The decision half of the `Done when` - ignore the file rather than track it - was recorded here on 2026-09-01 by the project owner and is unchanged; `PL-8PT6` carries the same conclusion with the anchoring reason beside the line. Found by `bin/docket check --verify` on `main`, which is the mechanism working: its error fired on the first run after `PL-8PT6` merged and is what this closure clears.
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

**Triaged 2026-09-01, with the approach settled.** The project owner chose the
first of the two answers in **Where.** above: ignore the file. Nothing wants
`subprojects/docket` separately installable or separately pinned, so a
committed lock of its own would be a second thing to maintain for no gain. One
`.gitignore` entry, and a comment beside it saying why the file appears at all.

Classed `infra` and not `defect`, deliberately. Nothing here is broken: the
repository simply has no ignore rule for a file its own tooling generates,
which is a configuration gap rather than a wrong answer. That keeps it off the
debt gate, which is the honest place for it - a missing `.gitignore` line is
not something a milestone should wait on.

The `verify:` command exits 1 on 2026-09-01 and exits 0 once the entry lands.
It asks git rather than looking for text in the file, so it stays true however
the pattern is written - a `subprojects/*/uv.lock` glob satisfies it as
readily as the literal path.

**Dropped 2026-09-13, and what it cost is worth one line.** This item sat
`ready` for twelve days while `PL-8PT6` was filed, triaged, worked and merged
against the same finding. Nothing compared the two at filing time; what caught
it was `bin/docket check --verify` on `main`, *after* the merge, by turning the
base branch red - which is the right mechanism reporting at the latest useful
moment rather than the earliest. `PL-BGMK` carries the cheaper signal that was
available and unused: these two items shared a `touches` path **and** a
`verify:` command substring, which is decidable without judging whether two
findings are "the same".
