---
id: PL-RCL9
title: docket trend --no-git builds its lines-written series from an empty Churn() that declines nothing, so a trend under the flag reads as a repository nobody committed to rather than saying the history went unread
status: dropped
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-23
closed: 2026-09-23
reason: Premise false when filed: under --no-git, docket trend omits the churn column and its key says it was not shown (trend.analyze's has_churn, present since PL-QPJZ added the command on 2026-09-07), so the trend never reads as a repository nobody committed to. The residuals, which are not this item, are in the brief: the key says git 'could not be read' where --no-git did not ask it, and the windows anchor at the first closure rather than the first commit.
---

**Problem.** docket trend --no-git builds its lines-written series from an empty Churn() that declines nothing, so a trend under the flag reads as a repository nobody committed to rather than saying the history went unread

**Reproduced 2026-09-23: the premise does not hold.** The first half is true.
`cmd_trend` builds `Churn()` under `--no-git`, and its empty `declined` means
the "Lines written: partial" line is not printed. The consequence is not.
`bin/docket trend --no-git` prints the closed-item columns and no churn column
at all, and its key says "churn    not shown: git could not be read in this
checkout." `trend.analyze` sets `has_churn=bool(churn)`, and the render omits
the column rather than printing zeros. It has done so since `PL-QPJZ` added the
command (2026-09-07, `83516afe`), so the premise was already false when this
was filed. Two smaller things are true and are not this item. The key's reason
is wrong under the flag, since git was not asked rather than unreadable. And
without commit days, `trend._first_day` anchors the weekly windows at the first
closure (2026-08-24) rather than the first commit (2026-08-21), so the
store-only columns re-bucket under the flag: the last row reads
`2026-09-21..09-23 94/20` where a normal run reads `2026-09-18..09-23 216/57`.

**Generator check.** Nothing to attribute. It was filed in `PL-NGBM`'s own
closing merge (`c91b8d99`), not after that head closed, and the flag behaves as
`PL-NGBM` intended, since `--no-git` asks git nothing here.
