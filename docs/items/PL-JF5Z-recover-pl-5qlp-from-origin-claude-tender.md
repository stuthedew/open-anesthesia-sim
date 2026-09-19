---
id: PL-JF5Z
title: Recover PL-5QLP from origin/claude/tender-keller-omy3ec, which carries one capture commit and no pull request, so the only copy of the rename finding is on a ref a prune would take
priority: P2
effort: S
status: ready
classes: infra
feature: slug-rename-on-write
touches: docs/items
added: 2026-09-19
verify: test -n "$(ls docs/items/PL-5QLP-* 2>/dev/null)"
---

**Problem.** Recover PL-5QLP from origin/claude/tender-keller-omy3ec, which carries one capture commit and no pull request, so the only copy of the rename finding is on a ref a prune would take

**State as of 2026-09-19 06:50 UTC.** `bin/docket stranded` names
`docs/items/PL-5QLP-bin-docket-record-renames-an-item-file-whose.md` as
existing only on `origin/claude/tender-keller-omy3ec`, whose tip is `ef83cd8`
("PL-5QLP: file the record rename found after #691 merged", 05:44 UTC). No open
pull request carries that branch — `#703` and `#704` are the only two open, on
`claude/gifted-ride-7g67kk` and `claude/cool-brahmagupta-i2wlai`.

**Not recovered in this session, deliberately.** The branch is an hour old and
carries exactly one capture commit, which is equally the shape of a live
session that has just captured and the shape of one that ended. `bin/docket
stranded` says that judgment is the reader's, and recovering into an open
release pull request would widen it on a guess. So this is filed rather than
done.

**Why it matters.** The ref is the only copy. Nothing else in the tree records
that `bin/docket record`'s `pr:` write can rename an item file, and `PL-QMC0`
— the same defect reached through `bin/docket release` — is blocked on reading
it. A `git fetch --prune` would take it, which is exactly the loss
`.claude/hooks/no-prune-guard.sh` exists to prevent and exactly the loss a
stranded ref keeps risking until somebody acts on it.

**Done when.** `docs/items/PL-5QLP-…md` is on the default branch, committed on its
own, and `bin/docket stranded` no longer names it. The remote branch deletions are
the project owner's and are outside this item.

**State at triage, 2026-09-19: a second ref now carries it.** `bin/docket stranded`
names two - `origin/claude/tender-keller-omy3ec` and
`origin/claude/tender-goldberg-psn2x7` - and the second was a session running
during this pass. So the recovery may land without this item ever being worked.
Whoever picks it up runs `bin/docket stranded` first: if the file has reached the
default branch, this is `dropped` with that as its reason rather than work to do.
