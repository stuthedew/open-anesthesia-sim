---
id: PL-L09X
title: An item blocked on a milestone that is decided but not yet named has no honest status: bare blocked errors, and blocked-by only accepts a version the roadmap already places
status: untriaged
added: 2026-09-10
---

**Problem.** An item blocked on a milestone that is decided but not yet named has no honest status: bare blocked errors, and blocked-by only accepts a version the roadmap already places


**Found 2026-09-10**, trying to record that `PL-GS3R` ships after the PySide6
port. Both halves of the finding are one attempt each:

| Written as | `docket check` says |
| --- | --- |
| `status: blocked`, no `blocked-by` | error: "marked blocked but names no blocking item or milestone" |
| `blocked-by: v0.5.0` | accepted, then advises "v0.5.0 is scoped ... ready to promote" |

**Neither is honest here.** The first is refused. The second would name the
wrong blocker - the port is not `v0.5.0`, which is the branched-run milestone -
and would then read as promotable, which is the opposite of the truth.

**Why the gap exists, and why it is narrow.** `_check_references` holds a
milestone blocker "to something real ... a typo would otherwise read as a
dependency on something that is never going to be scoped, which is
indistinguishable from a live block and never fires". That reasoning is right
and this item does not propose weakening it. What it names is the state between
a milestone being *decided* and being *scoped*: real, sometimes days long, and
currently unrepresentable.

**What it costs while unrepresentable.** `PL-GS3R` is `P1` and `safety`-classed,
so it ranks at the top of `bin/docket next` as startable work, while the one
thing a session must not do is build it - on the toolkit being replaced. The
guard is a paragraph at the top of its brief, which works only for a session
that reads the brief before acting, and nothing enforces it. That is the
"gives a wrong answer silently" test in `CLAUDE.md`'s compounding-friction rule.

**Not proposing a mechanism yet**, deliberately: the cheapest fix may simply be
that scoping a milestone is fast enough that the window never matters, in which
case this closes as "not worth a mechanism" with the reasoning recorded. Worth
deciding once rather than re-meeting; the alternatives worth costing are a
`blocked-by` entry that names a milestone the roadmap has *reserved* but not
scoped, and a `blocked-reason:` free-text field that blocks without an edge and
is therefore invisible to ranking.
