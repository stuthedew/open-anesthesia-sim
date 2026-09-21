---
id: PL-DZM1
title: Recover the item-brief sections that only bin/docket stranded's new ahead list can see: PL-DMDF carries a ratified project-owner decision on origin/claude/amazing-thompson-3hwksq that never reached main, and seven more sit on five branches with no open pull request
status: untriaged
feature: unmerged-item-edits
added: 2026-09-21
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
