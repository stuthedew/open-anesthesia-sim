---
id: PL-YZY4
title: Read the first compaction summary after PL-NK5K's Compact Instructions landed, and record whether it kept the item ids, the sources cited, the routes refuted and a verified-or-inferred mark on each conclusion
priority: P3
effort: S
status: ready
classes: session-cost
feature: compaction-reset
touches: CLAUDE.md, docs/items
added: 2026-10-01
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
