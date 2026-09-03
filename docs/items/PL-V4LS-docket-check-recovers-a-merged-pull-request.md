---
id: PL-V4LS
title: docket check recovers a merged pull request number and then asks a human to transcribe it, which is a decidable half left as prose
status: needs-decision
priority: P3
effort: S
classes: infra, session-cost
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, .claude/skills/docket/SKILL.md
added: 2026-09-03
---

**Problem.** After a merge, `docket check` reports:

    PL-J49T: marked done on `origin/main` and records no `pr`, but #249 is
    recoverable from its merge commit; write `pr: 249` into the item so the
    file carries it too

The tool has already found the number. It then asks a person to copy it into
the file it just read.

**Why it matters, and why it recurs forever.** This is not an oversight in how
items are closed - it is structural. `.claude/skills/docket/SKILL.md` requires
the closure to be committed *with the work*, in one commit, precisely because
splitting it out to learn the number reopens the window where a merge takes
the work and leaves the queue still calling the item open (`PL-D2GW`, then
`PL-P5S0`). So the number cannot be known when the closure is written, and
every item that ever closes will need this transcription afterwards.

`CLAUDE.md`: "work moved out of the model is paid for once and then runs free;
work left to the model is re-derived at full context in every session that
needs it." Measured on 2026-09-03, this session paid it twice - once after
#246 and once after #249 - and each time the payment was a commit and a pull
request whose entire content was two frontmatter lines.

It is also the same shape as `PL-J49T`, one layer along: a decidable fact
delivered as prose that only works if somebody reads and acts on it. The
difference is that here the tool does not merely know *whether* the field is
missing, it knows *what it should say*, which removes even the judgment half.

**Decision needed.** Whether a checker may write, and if not, what does:

1. **`docket record-pr`** - an explicit command that writes what `check`
   recovered, run as part of close-out. Keeps `check` read-only, which is
   worth something: a checker that edits files surprises whoever runs it in
   CI, and this one runs in `make check`.
2. **`docket check --fix`** - the same, behind a flag, so the default stays
   read-only. Fewer commands, but a `--fix` on a checker invites scope later.
3. **Leave it.** The advisory is narrow, names the exact number, and clears in
   one line. Three lines of prose against a command nobody has asked for.

Option 1 is the recommendation, on the grounds that it is the only one where
the work stops being re-derived, and `check` keeps the read-only property that
lets it run anywhere. The cost is one more command to know about.

Worth weighing against it: the transcription is genuinely one line, and this
item is itself process work, which `CLAUDE.md` warns is the most common way
this project wastes a session. If the answer is 3, record it and close this,
so the question is not re-opened by the next session that pays the toll twice.

**Where.** `subprojects/docket/src/docket/checks.py` raises the advisory and
already holds the recovered number; `cli.py` would carry a new subcommand;
`.claude/skills/docket/SKILL.md`'s close-out mode documents the manual step.

**Done when.** The decision is recorded, and if it is 1 or 2, closing out an
item no longer requires a human to copy a number the tool already printed.

**Found.** 2026-09-03, after paying it for the second time in one session.
