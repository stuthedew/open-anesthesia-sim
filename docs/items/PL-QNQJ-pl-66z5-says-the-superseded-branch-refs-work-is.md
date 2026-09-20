---
id: PL-QNQJ
title: PL-66Z5 says the superseded branch refs' work is already whole on main, but the last one left holds a ROADMAP.md paragraph main has never had, and that ref is what keeps PL-66Z5 and PL-ZM48 marked in flight
status: untriaged
added: 2026-09-20
---

**Problem.** PL-66Z5 says the superseded branch refs' work is already whole on main, but the last one left holds a ROADMAP.md paragraph main has never had, and that ref is what keeps PL-66Z5 and PL-ZM48 marked in flight

**Measured 2026-09-20**, while running the refresh rule 14 of
`.claude/rules/instruction-writing.md` requires before a closing block.

`PL-66Z5` is titled "Delete the ten superseded `claude/*` branch refs whose
work is already whole on main". Both halves of that have moved on:

- **Ten are already gone.** `git ls-remote --heads origin 'refs/heads/claude/*'`
  returns **four**, and three are live sessions. The archived "Unused branches
  cleanup" session deleted the rest.
- **The one left is not whole on main.** `origin/claude/practical-brown-wr7u6i`
  carries a `ROADMAP.md` paragraph that `origin/main` has never held - the
  post-freeze gate disposition opening "**`PL-ZM48`, added 2026-09-20, after
  the freeze and declined with it.**", 17 lines explaining why that entry was
  declined to Gate 2. `git show origin/main:ROADMAP.md | grep -c 'after the
  freeze and declined with it'` returns 0; the same grep on the branch returns
  1.

**It is not obviously a loss, which is the part needing judgment.** `main`
*does* carry `PL-ZM48` in its `### Declined to Gate 2` list, at 209 entries
against the branch's 206, and worded differently - so main is the later state
and took a different route to recording the same decision. Whether the
paragraph is superseded prose or a dropped explanation is a read of the two
texts, not something a command settles, and `bin/docket stranded` cannot see it
at all: that check reads item files, and this is roadmap prose.

**Why it matters.** That ref is what marks `PL-66Z5` and `PL-ZM48` `IN FLIGHT`,
and `bin/docket next` excludes in-flight work - so the item for deleting the
spent refs is itself suppressed by the last spent ref, and cannot be reached
except by being named directly. `PL-ZM48` is suppressed beside it.

**Done when.** `PL-66Z5`'s brief states the true remaining scope - one ref, not
ten - and records whether the branch's `ROADMAP.md` paragraph is superseded or
must be carried onto `main` before the ref is deleted. Deleting a ref on the
remote stays the project owner's (`PL-K2C8`).
