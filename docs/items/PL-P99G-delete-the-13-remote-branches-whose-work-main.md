---
id: PL-P99G
title: Delete the 13 remote branches whose work main already holds, as checked 2026-09-26: each item they carry is closed on main with its pull request recorded
priority: P3
effort: S
status: ready
classes: housekeeping
touches: docs/items
added: 2026-09-26
payoff: the remote lists main and live work only, so git branch -r, flight and stranded stop re-reading thirteen branches whose work main already holds
not-delegable: the proof is the remote's branch list, which no file in the tree holds, so no admitted grep shape can read it: git ls-remote --heads origin with the thirteen names must print nothing, read from its output and never its exit status, which is 0 either way (PL-X9WZ)
---

**Problem.** Delete the 13 remote branches whose work main already holds, as checked 2026-09-26: each item they carry is closed on main with its pull request recorded

**The owner asked for it, 2026-09-26** ("clean up unused branches"). That lifts
the generator pause for this request.

**How each was judged.** `git ls-remote --heads origin` listed 15 heads against
`main` at `3eb95a61`. Each head's pull requests were read on GitHub, and each
commit it carries ahead of `main` was checked for whether the lines it adds are
on `main`. They almost all are. Where one is not, it is `status: untriaged` or
an earlier status that `main`'s copy has since moved past, or a checkpoint draft
of code that landed in a later pull request. `bin/docket stranded` agreed on
all 13. It found no item that exists only on a branch, and no branch carrying
work its own pull request left behind. It listed `PL-N162` and `PL-PNJF` as
edited on a branch. Neither edit needs carrying over: `PL-N162`'s two review
findings are both recorded as fixed on `main`, and `main`'s `PL-PNJF` is the
later, closed copy.

| Branch | Tip | Last commit | Pull request | What it carries, and where it stands on `main` |
| --- | --- | --- | --- | --- |
| `claude/wizardly-goodall-p5ltid` | `6302fbd59b` | 2026-09-20 | none | `PL-7TVT` capture; done, #927 |
| `claude/adoring-einstein-44v9pt` | `6fa7df508f` | 2026-09-20 | none | `PL-V3QB`, `PL-6T44`; done, #765 and #769 |
| `claude/cool-pascal-emsw3c` | `44299bd80a` | 2026-09-21 | #810 merged; tip pushed after | `PL-3QM9` capture; done, #924 |
| `claude/cool-sagan-fzlong` | `9ce0608fd6` | 2026-09-23 | none | `PL-J6HP`, `PL-B60Q`; done, #937 |
| `claude/exciting-mccarthy-fa8o39` | `403a00eed0` | 2026-09-23 | none | `PL-1PBV`; done, #938 |
| `claude/laughing-clarke-m1u08s` | `bf6fbeabfd` | 2026-09-23 | #938 merged; tip pushed after | `PL-GHHW` capture; done, #975 |
| `claude/inspiring-bardeen-38yf9z` | `dfce695fd1` | 2026-09-23 | none | `PL-KH3Q`, `PL-Z0SM`, `PL-PXZ3`; done, #939, #960, #975 |
| `claude/intelligent-gauss-0p4vcy` | `79733b2841` | 2026-09-24 | none | `PL-N162` slice 1 draft; done, #1002 |
| `claude/exciting-gates-38yfzt` | `873d586499` | 2026-09-24 | none | `PL-N162` slices 1-2 drafts; done, #1002 |
| `claude/funny-babbage-qht2y5` | `4a09c6e96c` | 2026-09-24 | none | `PL-N162` slices 1-2 drafts; done, #1002 |
| `claude/pl-mb2w-closeout-i7pg11` | `32e2b8a703` | 2026-09-26 | #1041 merged, #1045 closed unmerged | `PL-21KN` capture; on `main`, triaged to blocked |
| `claude/pl-979d-build-1y2bjk` | `6efa8396a8` | 2026-09-26 | none | `PL-979D` build plan, every line on `main`; done, #1068 |
| `claude/project-thread-f3ybg7` | `17e83c04bd` | 2026-09-26 | none | `PL-979D` checkpoints, `PL-PNJF`; done, #1068 |

**Left alone.** `claude/pl-0x0g-8kokh9` holds a live claim on `PL-0X0G`, with
its last commit minutes old. `claude/cleanup-unused-branches-bcecxv` is this
item's own branch.

**A session cannot do the deletion** (`docs/worker.md` § "Ref operations a
session cannot perform", `PL-ZM48`), so the owner runs it. A deleted head comes
back with `git push origin <tip>:refs/heads/<branch>` from any clone that still
holds the tip. A branch whose pull request is listed also comes back from that
pull request's **Restore branch** button.
