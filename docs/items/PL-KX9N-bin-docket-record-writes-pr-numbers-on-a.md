---
id: PL-KX9N
title: bin/docket record writes pr numbers on a shallow clone that docket check declines to verify on the same clone, so it silently records wrong provenance
status: untriaged
added: 2026-09-06
---

**Problem.** bin/docket record writes pr numbers on a shallow clone that docket check declines to verify on the same clone, so it silently records wrong provenance

**Why it matters.**

**Where.**

**Done when.**

**Problem.** Observed 2026-09-06 in a web session working `PL-GYH2`. The
container had no checkout, so the repository was cloned per the harness
instruction with `git clone --depth 1`, which is shallow *and* single-branch.
`bin/docket check` raised its ordinary advisory - five items closed on the base
recording no `pr`, each "recoverable from its merge commit" - and the `docket`
skill's instruction for that is to let `bin/docket record` ride the commit you
are already making. It did. **Four of the five numbers it wrote were wrong.**

| Item | `record` wrote | Actually merged in |
| --- | --- | --- |
| `PL-6Q8N` | 401 | **399** |
| `PL-GJDW` | 401 | **400** |
| `PL-N2X4` | 401 | **400** |
| `PL-VRMK` | 401 | **402** |
| `PL-S5LB` | 401 | 401 (correct) |

The mechanism: a depth-1 clone holds one commit of `main`, so the walk that
recovers a number from the newest merge subject naming an id reached only the
newest commit it had, whose subject named `PL-S5LB` and `#401`. Every other id
resolved to that same commit by default. Re-run after
`git fetch --depth=200`, `record` produced all four correctly.

**Why this is the silent-wrong-answer case rather than an inconvenience.**
`docket check` on the *same* checkout already declines the verification half,
printing "recorded pull requests: the checkout is a shallow clone, so the
commits it is missing are the oldest ones and the longest-settled provenance
would read as broken" under **Not checked**. So the store knows the clone is
truncated when it would *verify* a number, and writes one anyway. After the
write, `docket check` reports `0 errors`: the field is present and
syntactically fine, and the one check that could have contradicted it has
already excused itself. This is `CLAUDE.md`'s first compounding-friction test
exactly - a check passing while the guarantee it stands for is void.

It survived only by accident. Four of the five collided at a merge conflict
against sessions that had written the right numbers with fuller history, which
is what surfaced it; had those sessions not existed, or had they run `record`
later, the wrong numbers would have merged unremarked. `pr` is provenance -
`PL-YDL6` and `PL-JZ1D` are both about recovering the right number - so a
wrong one is worse than an absent one, and the skill forbids hand-editing the
field precisely so the command is trusted.

**Fix, in the shape the store already has.** `record` should apply the same
completeness test its verifier applies and decline on a truncated checkout,
naming the fetch that would let it answer - the way `PL-99Y4` made the missing
`pr` advisory decline rather than error on an incomplete clone. Declining is
cheap: a session that wants the write runs one bounded fetch first.

**Where.** `subprojects/docket/src/docket/vcs.py`,
`subprojects/docket/src/docket/cli.py` (`cmd_record`); the completeness test
the checker already uses is the thing to reuse rather than to reinvent.

**Found by** `PL-GYH2`, whose own commit carried four of the wrong numbers
until the merge exposed them.
