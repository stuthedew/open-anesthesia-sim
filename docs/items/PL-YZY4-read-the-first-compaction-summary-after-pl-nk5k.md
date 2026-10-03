---
id: PL-YZY4
title: Read the first compaction summary after PL-NK5K's Compact Instructions landed, and record whether it kept the item ids, the sources cited, the routes refuted and a verified-or-inferred mark on each conclusion
priority: P3
effort: S
status: done
classes: session-cost
feature: compaction-reset
milestone: v0.5.21
touches: CLAUDE.md, docs/items, docs/resident-instructions.md
added: 2026-10-01
closed: 2026-10-03
pr: 1285
payoff: the Compact Instructions section either earns its resident cost by changing what a compaction keeps, or is removed
verify: grep -qE '^\*\*Summary read [0-9]{4}-[0-9]{2}-[0-9]{2}\.\*\*' docs/items/PL-YZY4*.md
not-delegable: the evidence is the summary a compacted session is handed, which exists only in a session the owner has compacted
---

**Problem.** Read the first compaction summary after PL-NK5K's Compact Instructions landed, and record whether it kept the item ids, the sources cited, the routes refuted and a verified-or-inferred mark on each conclusion

**Notes.** `PL-NK5K` added `CLAUDE.md` § "Compact Instructions" on 2026-10-01
and closed on the half a session can see: the section exists. Whether a
compaction summary follows it was not observed, because a session cannot run
`/compact` on itself. The first session compacted after the change merges is
the evidence: read the summary it was handed, and check it for the item ids in
play, the sources cited, the routes refuted, and a verified-or-inferred mark
on each conclusion carried forward. The baseline is the first live compaction
on 2026-09-25, which kept 8 of 20 cited references (`PL-NK5K`'s brief). If the
summary ignores the section, the instruction is not reaching the summarizer,
and the section should be removed rather than kept as resident cost.

**Why it matters.** `CLAUDE.md` § "Compact Instructions" is resident in every session and exists only to change what a compaction summary keeps; if the summarizer ignores it, it is resident cost with no effect, which `docs/resident-instructions.md`'s test retires.

**Done when.** The first compaction summary after the section landed is read, what it kept of the four things is recorded here under a `**Summary read <date>.**` heading against the 8-of-20 baseline, and the section is kept or removed accordingly.

**Generator check.** A follow-up measurement on `PL-NK5K`'s own change. One-off.

**Summary read 2026-10-03.** The first summary written with the section in
context is `PL-NJPB`'s session, `session_01GtSNGP53xY7ExgfX9xW8AY`: a manual
`/compact` at 2026-10-01 15:55:41 UTC, 219,731 tokens before it, summary event
`fa4eb7f7-c1a9-4b5e-93b9-913f06001abd`. The section was in its context,
verified: the session's claim commit `c7056f96` sits on `59d538e5`, which
carries `e22b062a` and the `## Compact Instructions` heading. What it kept of
the four:

- **Item ids with status: kept.** `PL-NJPB` "needs-decision, P3, effort M",
  and `PL-SM5V` "done; it shipped in v0.5.16", which is not the item in hand.
- **Sources with their URL, path or command: kept, on a light load.** All 3
  sources the session's replies had cited (Goldberg 1991 with its DOI, and two
  pull-request URLs), and all 10 references of the four kinds counted below.
  But the session compacted before writing its review reply - 7 text blocks,
  4,226 characters - so 3 is the whole denominator. The same count on the
  2026-09-25 baseline gives 3 of 20 sources kept as a URL, DOI or arXiv id;
  `PL-NK5K`'s 8 of 20 counted a source named in any form. So this summary does
  not measure retention under the baseline's load.
- **Routes refuted, with the reason: kept.** "Refused: two-copy segment
  (copies can disagree; PL-SM5V refused the same shape). Grid rounding
  (silently snaps values; puts interface resolution into core)." The baseline
  kept one ruled-out hook with its reason and left the rest as "Its brief
  covers ... the routes rejected".
- **Verified or inferred: half kept.** Seven conclusions marked verified, each
  naming its check ("verified by Python", "verified by grep", "verified at
  controller.py:1536"), and two marked inferred. Facts about the code in its
  concepts section carry no mark, so "each conclusion" is not met.
- The branch and the pull request were kept, as in every summary read here.

**Against controls.** Eleven summaries, each fetched with `get_event`, counted
by one script and the word counts re-run by hand. "Section" means the session
launched from a checkout carrying it; C3 and C4 launched before it merged, and
whether either re-read `CLAUDE.md` afterwards was not checked.

| Summary | Compacted (UTC) | Section | "verified" | "inferred" |
| --- | --- | --- | --- | --- |
| BASE | 2026-09-25 13:49 | no | 1 | 0 |
| C1 | 2026-10-01 02:46 | no | 1 | 0 |
| C2 | 2026-10-01 14:02 | no | 1 | 0 |
| C3 | 2026-10-01 15:06 | launched before | 0 | 0 |
| C4 | 2026-10-01 15:18 | launched before | 0 | 1 |
| P1 | 2026-10-01 15:55 | yes, the first | 7 | 2 |
| P2 | 2026-10-01 17:16 | yes | 7 | 0 |
| P3 | 2026-10-01 17:16 | yes, P1's second | 2 | 1 |
| P4 | 2026-10-01 17:45 | yes, P2's second | 1 | 0 |
| P5 | 2026-10-03 04:02 | yes, automatic | 6 | 2 |
| P6 | 2026-10-03 12:08 | yes, automatic | 3 | 0 |

Every summary written with the section marks something verified, 1 to 7 times
(median 4.5); none of the five without it does so more than once. "Inferred"
appears in 3 of 6 with it and 1 of 5 without. Item statuses, URL counts, the
branch and the pull request do not separate on a mechanical count. The two
automatic compactions follow it as the manual ones do.

**Kept.** The instruction reaches the summarizer, which is the test this item
set: a summary written with it marks what was checked and lists refused routes
with their reasons, which the nine-section prompt asks for nowhere and the
controls mostly do not do. Claude Code 2.1.288's compaction prompt still
carries "There may be additional summarization instructions provided in the
included context", with `## Compact Instructions` as its first example, read
from the installed binary on 2026-10-03. Not measured: whether it keeps sources
under a load like the baseline's 20. Externalizing first stays the carrier for
those, as `CLAUDE.md`'s reset bullet already requires.

**The `not-delegable:` premise was wrong.** A summary is in the compacted
session's event store, and any session can read it. `get_session` gives
`external_metadata.context_usage.after_boundary`, the latest
`compact_boundary` event. `get_event` on that gives `compact_metadata` -
trigger, `pre_tokens` and `preserved_segment.anchor_uuid` - and `get_event` on
the anchor is the summary. Earlier compactions are found by paging
`list_events` for `system` events with `subtype: "compact_boundary"`; `other`
events never carry one. The summaries read (session / summary event):

- BASE `session_01AnQhmzeBqh7Zjp3V3kGMhw` / `f4d96051-f22b-4c80-901f-8f4a9bf01540`
- C1 `session_01DyeXNg6wwNUxFx3b2CUUXf` / `955a64fd-05ec-4c1c-8e6d-c478e1238082`
- C2 `session_01WqP9EBUgP87GVRXJBft9ax` / `d189c84d-4a67-4f1f-96cf-8275417e841e`
- C3 `session_01UkLy3xnCyx5ceKb3xDyn4y` / `f217c188-f1dc-4591-9021-6fe556bd62e9`
- C4 `session_01PGkxiNSTXC1Dh6Kg65ZDiH` / `ec3d2026-bca8-493b-ad69-e521728a7dba`
- P1 `session_01GtSNGP53xY7ExgfX9xW8AY` / `fa4eb7f7-c1a9-4b5e-93b9-913f06001abd`
- P2 `session_015nq8MLeDYBxomzpZcg4W9d` / `43b6c471-99c6-46a4-b9dd-78538b8da793`
- P3 `session_01GtSNGP53xY7ExgfX9xW8AY` / `c7ed8e37-e0a3-453d-8db4-4f4a71870346`
- P4 `session_015nq8MLeDYBxomzpZcg4W9d` / `2600f484-e6e0-4877-9c01-dddcf77eb2b2`
- P5 `session_014zeaVuCep8y78SCMVYsXNP` / `b1230e8e-8b6d-4778-beb0-c1ec19c94d4f`
- P6 `session_01HvpwLFUXprsAuMjD5hphJk` / `ab1a0a5c-4b9c-43d8-9dc0-657e48434f97`
