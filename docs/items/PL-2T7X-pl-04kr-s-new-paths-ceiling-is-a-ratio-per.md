---
id: PL-2T7X
title: PL-04KR's new-paths ceiling is a ratio per filing, so it rises when filings fall: 2026-10-26..11-01 named 11 new apparatus paths, down from 34, over 19 filings, down from 117, and reads 0.58 against the 0.13 ceiling, flagging converging inflow as growth
status: untriaged
added: 2026-11-03
---

**Problem.** PL-04KR's new-paths ceiling is a ratio per filing, so it rises when filings fall: 2026-10-26..11-01 named 11 new apparatus paths, down from 34, over 19 filings, down from 117, and reads 0.58 against the 0.13 ceiling, flagging converging inflow as growth

**Measured 2026-11-03** by `PL-CK1W`'s verdict, with `docket.inflow.analyze` on `main` at `4620917c`. New apparatus paths by week: 30 (2026-10-12 to 10-18), 34 (10-19 to 10-25), 11 (10-26 to 11-01). Filings over the same weeks: 107, 117 and 19. `bin/docket inflow` and `docket.inflow.missed` report the last week as "11 new apparatus paths over 19 filings, 0.58 a filing, above the 0.13 ceiling: the surface is still growing". The count of new paths fell by two thirds, so the surface grew more slowly, not faster.

**Why it matters.** `CLAUDE.md` § "What this project is" expects apparatus inflow to decline now that the functionality is settled. A ratio per filing rises whenever filings fall faster than new paths, so the check reads the expected decline as a broken prediction, and each such week costs an investigation item like `PL-CK1W`. The same week also reports one `P1` filing outside the generator tier, `PL-D59R`, which is a separate prediction.

**Done when.** The new-paths prediction is stated in a form that a falling filing count cannot break on its own, such as an absolute count per week or a ratio read only above a minimum number of filings, and `docket.inflow.missed` reads it that way. `PL-04KR` pre-registered the prediction, so the change records why the restatement is not moving the goalposts.
