---
id: PL-3V4N
title: The README freeze is a path-scoped rule, so it fires on reading README.md and cannot fire before a write that no read precedes
priority: P2
effort: S
status: dropped
classes: defect, infra
feature: dev-tooling
touches: .claude/rules/readme-hold.md, tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-05
closed: 2026-09-05
reason: Overtaken by PL-WB5K, which deleted the root README and the freeze rule together, so there is no longer a write to gate. The enforcement this item wanted exists as tools/readme_hold_check.py, guarding the file's absence rather than its contents; the general finding - a path-scoped rule fires on a read and so cannot gate a first write - is already stated in CLAUDE.md's routing list.
---

**Dropped 2026-09-05, under `PL-WB5K` (delete README.md until a deliberate
rewrite replaces it).** There is nothing left to enforce. The project owner
deleted the root README and the hold file with it, so the freeze this item
protects no longer exists and neither does the file it protected. The item's
own self-lifting design anticipated exactly this ending — "the check disappears
with the hold file" — it simply arrived before the check was ever built, which
is the cheaper of the two orders.

The finding underneath it is not lost, because it was never about the README:
a path-scoped rule fires on a **read**, so any rule that must fire before a
first write is routed to a disposition that cannot deliver it.
`.claude/rules/` carries other `paths:`-scoped rules and the next one written
to gate a write will hit the same wall. That general form belongs in the
routing guidance in `CLAUDE.md`, which already states it; this item is dropped
rather than generalized in place, so a reader is not left with a defect report
naming two deleted files.

The record below is the original text, kept for the reasoning.

**Problem.** `.claude/rules/readme-hold.md` carries `paths: ["/README.md"]`.
Claude Code loads a path-scoped rule when a session **reads** a matching file —
"Path-scoped rules trigger when Claude reads files matching the pattern, not on
every tool use". A session that edits `README.md` with a targeted replacement,
or through a script, or as one file in a wider sweep, may never read it first,
and then the freeze never enters that session's context at all.

`CLAUDE.md` already names this failure mode in its routing list: a path-scoped
rule is "wrong for one that must fire before a first write, which no read
precedes." The freeze is precisely such a rule, and it was routed to the one
disposition that cannot guarantee delivery. `PL-BTSW` records the first
instance, one day after the freeze was written. A second landed in #361 on
2026-09-05: the floor-job paragraph was rewritten by a session working on CI
billing, which had no reason to open `README.md` for reading and so never
loaded the hold. That edit also left the paragraph's command list at four
where CI now runs five, which is `PL-5N7T`. Twice breached, both times by a
session that edited without reading: the delivery gap is the whole defect,
not the discipline of the sessions.

**Why it matters.** The freeze is not a style preference. `PL-QTN6` recorded
that successive isolated edits made the document worse, and `PL-RM83` has since
settled the audience and boundary the rewrite will be judged against — so an
edit landing before `PL-N092` runs is an edit made against no agreed target.
A rule whose delivery is best-effort reads, to everyone who wrote it, as a rule
that is in force. That gap is worse than no rule, because it is trusted.

**Where.** `.claude/rules/readme-hold.md`; a check under `tools/`, wired into
`make check` and so into CI's bare-interpreter section.

**Approach.** This is the decidable half of an undecidable rule, which is where
`CLAUDE.md` says to reach for code: *does this diff touch `README.md` while
`.claude/rules/readme-hold.md` exists?* Both halves are mechanical, the answer
is identical every run, and the rule states itself where a reviewer can read
it. It needs no judgment, so it is a hard error rather than an advisory.

The self-lifting property is the neat part and worth keeping: the check exists
only while the hold file does, and `readme-hold.md` is already specified to be
deleted in the commit carrying the first README change. So the commit that
lifts the freeze disables its own enforcement, with nothing left behind to
retire — which is what `CLAUDE.md` asks of a check that has stopped earning its
place.

One case to get right rather than assume: a merge commit bringing someone
else's README change into a branch would trip a naive diff check. Compare
against the merge base rather than the first parent, or exempt a commit with
two parents.

**Done when.** A commit touching `README.md` while `.claude/rules/readme-hold.md`
exists fails `make check` with a message naming the freeze and `PL-XYRN` (decide
when the repository goes public), a merge that only carries someone else's
README change does not, and the check disappears with the hold file.
