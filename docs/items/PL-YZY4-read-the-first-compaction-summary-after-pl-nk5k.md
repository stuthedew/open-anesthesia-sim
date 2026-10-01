---
id: PL-YZY4
title: Read the first compaction summary after PL-NK5K's Compact Instructions landed, and record whether it kept the item ids, the sources cited, the routes refuted and a verified-or-inferred mark on each conclusion
status: untriaged
feature: compaction-reset
added: 2026-10-01
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
