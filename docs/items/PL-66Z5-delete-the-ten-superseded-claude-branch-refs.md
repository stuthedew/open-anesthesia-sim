---
id: PL-66Z5
title: Delete the ten superseded claude/* branch refs whose work is already whole on main
priority: P2
effort: S
status: done
classes: housekeeping
feature: remote-ref-deletion
milestone: v0.4.33
touches: docs/items
added: 2026-09-20
closed: 2026-09-20
pr: 749
payoff: every stranded, flight and concurrent read stops walking ten dead refs, so the two live branches stop being buried among twelve
verify: ! git ls-remote --heads origin 'refs/heads/claude/fervent-knuth-pr9ex7' 'refs/heads/claude/amazing-thompson-3hwksq' 'refs/heads/claude/awesome-brown-x29b1e' 'refs/heads/claude/tender-goldberg-psn2x7' 'refs/heads/claude/tender-keller-omy3ec' 'refs/heads/claude/magical-bohr-brjvi4' 'refs/heads/claude/optimistic-brahmagupta-63pa72' 'refs/heads/claude/nifty-gauss-rgoya2' 'refs/heads/claude/funny-turing-bul2ux' 'refs/heads/claude/happy-shannon-e9eeen' | grep -q .
---

**Problem.** Delete the ten superseded claude/* branch refs whose work is already whole on main

Twelve `claude/*` refs stand on the remote besides `main`. Two are live and
ten are superseded. Every `stranded` and `flight` read walks all twelve.

**Established 2026-09-20, per branch.** For each ref, every file it changed
against its merge-base was compared three ways — base, branch tip, `origin/main`
— and no file came back `main never moved`, the reading that would mean the
branch's change never landed. Where `main` and the branch differ, `main` holds
the later state in all cases: `status: done` with `closed:` and `pr:` set, against
the branch's `status: untriaged` stub. `bin/docket stranded` independently reports
only `lucid-pascal` carrying items `main` lacks.

| Ref | Its pull request | Why it is superseded |
| --- | --- | --- |
| `claude/funny-turing-bul2ux` | #723, merged | `PL-BSYZ` landed via #728 off another branch |
| `claude/happy-shannon-e9eeen` | #707, merged | `PL-GL5P` landed via #718 off another branch |
| `claude/tender-keller-omy3ec` | #691, merged | `PL-5QLP` landed via #708 |
| `claude/tender-goldberg-psn2x7` | none | same `PL-5QLP` file, landed via #708 |
| `claude/nifty-gauss-rgoya2` | #584 merged, #587 closed unmerged | `PL-8KPD`/`PL-0QLX` landed via #586 |
| `claude/amazing-thompson-3hwksq` | none | `PL-DMDF` #664, `PL-SWP3` #667, `PL-3DC7` #655 |
| `claude/awesome-brown-x29b1e` | none | `PL-FXBS` landed via #661 |
| `claude/fervent-knuth-pr9ex7` | none | 12 item files, all later on `main`; `PL-SYG4` is `ready` there |
| `claude/magical-bohr-brjvi4` | none | `PL-NZC0`/`PL-050P` byte-identical to `main`; `PL-VX5H` later on `main` |
| `claude/optimistic-brahmagupta-63pa72` | none | `PL-6T44` is `needs-decision` on `main`, `untriaged` here |

**Not these two.** `claude/lucid-pascal-9eaz1c` carries `PL-6WNZ` and `PL-V3GD`,
which exist nowhere else, and session `session_0183Myr5AvRNGnQKkoGr3yUV` was
running on it at the time of writing. `claude/practical-brown-wr7u6i` is this
item's own branch.

**Rollback.** Tip SHAs, so any ref above can be restored by name:

```
claude/fervent-knuth-pr9ex7          f49b6977d981dccefb3894b3e1ea7f27d18009b1
claude/amazing-thompson-3hwksq       ea1500c9a15372b89b774e08c579e281fe077a66
claude/awesome-brown-x29b1e          ed272da34e851c4f5511f07f12747dfb31a08a40
claude/tender-goldberg-psn2x7        61480954477758f22d0382bcba641f1a11f6878d
claude/tender-keller-omy3ec          ef83cd8fc5b3c70670789e3f8c4999579817970d
claude/magical-bohr-brjvi4           b768e35239c4046f73e5ee4fb1682ae78483cc50
claude/optimistic-brahmagupta-63pa72 312029a9cdd768dfc53af9d6c0b566a1c7f5dee5
claude/nifty-gauss-rgoya2            a19f3f4c63a1cf70a0a89a47fa2f8a6c6663c695
claude/funny-turing-bul2ux           2ce3c5310ebc3fcbc325176ad0c8f9da7b76c2a9
claude/happy-shannon-e9eeen          f8526f526540f67a8066c61ffeca3a848572db72
```

**The deletion is the project owner's, and this was re-measured rather than
recalled.** `docs/worker.md` § "Ref operations a session cannot perform" says a
session cannot do it; asked on 2026-09-20 to do the cleanup anyway, this session
ran the attempt rather than citing the table, since `PL-K2C8` withholds the
operation *unasked* and the owner had asked. It failed, and `git ls-remote`
confirmed the ref survived. The transcript is in `PL-ZM48`, which corrects what
the table says about it.
