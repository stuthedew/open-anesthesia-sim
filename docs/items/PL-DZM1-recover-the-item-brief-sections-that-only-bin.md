---
id: PL-DZM1
title: Recover the item-brief sections that only bin/docket stranded's new ahead list can see: PL-DMDF carries a ratified project-owner decision on origin/claude/amazing-thompson-3hwksq that never reached main, and seven more sit on five branches with no open pull request
priority: P2
effort: S
status: done
classes: housekeeping
feature: unmerged-item-edits
touches: docs/items
added: 2026-09-21
closed: 2026-09-21
pr: 837
payoff: a ratified project-owner decision that shipped as _pathspec_chunks stops existing only on a deleted branch, so a session proposing the alternative it was chosen over finds the refusal already recorded
verify: grep -q 'chunk the pathspec' docs/items/PL-DMDF-docket-digest-asks-one-git-diff-per-item-file.md
---

**Problem.** Recover the item-brief sections that only bin/docket stranded's new ahead list can see: PL-DMDF carries a ratified project-owner decision on origin/claude/amazing-thompson-3hwksq that never reached main, and seven more sit on five branches with no open pull request

**Why it matters.** This is `PL-KSCW`'s prediction arriving with a list. An item
file is created once and appended to by every session that learns something
about it, so the unmerged *section* outnumbers the unmerged file - and nothing
reported one until `#825`. The most expensive of them is `PL-DMDF`, whose
branch copy carries a **ratified project-owner decision** ("Decided: chunk the
pathspec", 2026-09-17, with the alternative it was chosen over) that `main`'s
copy does not have. A decision nobody merged is one a later session will take
again, differently.

**What the report named on 2026-09-21**, after `#825` landed the ahead list.
Five of these branches have no open pull request, so nothing will merge them:

| Item | Branch | Open pull request |
| --- | --- | --- |
| `PL-DMDF` | `origin/claude/amazing-thompson-3hwksq` | none |
| `PL-3DC7` | `origin/claude/amazing-thompson-3hwksq` | none |
| `PL-BSYZ` | `origin/claude/funny-turing-bul2ux` | none |
| `PL-0QLX` | `origin/claude/nifty-gauss-rgoya2` | none |
| `PL-8KPD` | `origin/claude/nifty-gauss-rgoya2` | none |
| `PL-CJ5R` | `origin/claude/blissful-mendel-ccad0y` | none |
| `PL-34BG`, `PL-SHTR`, `PL-N3N5`, `PL-S8JT`, `PL-W7WL`, `PL-WXX8` | `origin/claude/tender-ramanujan-ugl0rp` | none - live session |
| `PL-25DD`, `PL-S8JT`, `PL-W7WL`, `PL-WXX8` | `origin/claude/sharp-lamport-t545rs` | `#823` |
| `PL-PT7M` | `origin/claude/epic-curie-3xncza` | `#824` |
| `PL-5B39`, `PL-FX0K`, `PL-V6CR` | `origin/claude/pl-9hd1-3ueojq` | none - live session |

The ones on a live session's branch and the ones on an open pull request need
nothing: they merge with their own work. The rows carrying `none` and no live
session are the recovery.

**Done when.** Each branch copy with no route to `main` has been read against
`main`'s, and what is worth keeping has been applied and committed on a branch
of its own. `bin/docket stranded`'s ahead list is then empty of everything but
live sessions' own work. Re-run the command rather than working from this
table: it is a snapshot, and a live branch here is a merged one tomorrow.

**How.** `bin/docket stranded` prints the `git diff <base>:<path>
<ref>:<path>` for each. Never `git checkout` one over `main`'s copy - that is
`PL-MBTZ`'s whole subject, and what the command deliberately no longer offers.

**Worked 2026-09-21, and the table above was mostly already stale when it was
written.** Every one of the six rows `bin/docket stranded`'s ahead list reports
was read — `git diff origin/main:<path> <ref>:<path>`, insert side only — and
**five of the six branch copies are older than `main`'s, not newer**:

| Item | On `main` today | What the branch copy adds |
| --- | --- | --- |
| `PL-DMDF` | `done`, `#664` | **the ratified decision — recovered here** |
| `PL-3DC7` | `dropped`, reason names `#655`/`PL-L4KX`/`verify.py:746-758` | a shorter note saying to drop it |
| `PL-BSYZ` | `done`, `#728` | a `**Where.**` pointer at a rule the fix has since changed |
| `PL-0QLX` | `dropped`, reason names `PL-Y6W9` and `#584` | the same reason, shorter |
| `PL-8KPD` | `done`, `#586` | the `classes`/`verify` that commit already wrote |
| `PL-CJ5R` | `done`, `#818` | `status: untriaged` and a truncated fragment |

So the recoverable content was one block, not eight: `PL-DMDF`'s **"Decided:
chunk the pathspec" (project owner, 2026-09-17, ratified)** with the
alternative it was chosen over, which shipped as `_pathspec_chunks`
(`subprojects/docket/src/docket/vcs.py:1330`) and had never been written down
on `main`. It is appended to `PL-DMDF` with its provenance.

**The window had already closed on three of the four branches.** `git ls-remote
--heads origin` on 2026-09-21 returned nothing for `claude/amazing-thompson-3hwksq`,
`claude/funny-turing-bul2ux` or `claude/nifty-gauss-rgoya2`: they were deleted
from the remote, and the only copy left anywhere was one container's unpruned
remote-tracking ref. That container is ephemeral. Had this item waited for a
later session in a fresh clone, `PL-DMDF`'s decision would have been
unrecoverable rather than late — which is the argument for treating an ahead-list
entry on a remote-deleted branch as time-bounded rather than as backlog.

**The second half of "Done when" above is unreachable as written, and that is
the finding rather than a failure.** "`bin/docket stranded`'s ahead list is then
empty of everything but live sessions' own work" cannot be satisfied by
recovering anything: the ahead list reports a *textual difference* between the
base's copy and a branch's, so a branch holding a stale copy stays listed
forever, and carrying content across widens the difference rather than closing
it. Emptiness is therefore the wrong completion test for this shape. Captured
separately rather than fixed here.
