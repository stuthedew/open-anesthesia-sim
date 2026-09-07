---
id: PL-3MJH
title: CLAUDE.md's capture rule exempts a finding fixed in the same session but gives no session a way to enter that exemption, so every trivial fix becomes a queue item
priority: P2
effort: S
status: done
classes: defect, docs, session-cost
feature: worker-instructions
touches: CLAUDE.md, .claude/skills/docket/SKILL.md, ROADMAP.md, docs/WORKING_NOTES.md
added: 2026-09-01
closed: 2026-09-07
verify: python3 tools/doc_check.py check && grep -qF 'at most two per branch' CLAUDE.md
not-delegable: the deliverable is the wording of a rule every session reads before it acts. A shade too loose and it licenses the queue-bypass it exists to bound; a shade too tight and no session ever uses it. The brief also records two widenings deliberately set aside - both of which the cited source argues *for* - so a worker reading the same article is being asked to hold a line against it.
---

**Problem.** `CLAUDE.md`'s capture bullet scopes itself to any finding
"identified in a session **and not fixed in that same session**". That
conditional describes an exemption, and nothing in `CLAUDE.md`, the `docket`
skill or `docs/worker.md` tells a session when it may enter it. The exemption
is stated and unreachable, so every session takes the road that cannot be
wrong: capture. A two-line typo fix and a compartment-model defect enter the
queue by the same door and cost the same triage decision.

**Why it matters.** The cost is not the fixing, it is the bookkeeping around
it: a `docket new`, a triage slot filling five required fields
(`priority`, `effort`, `classes`, `touches`, `feature`), a hand edit to close,
and a queue line that every `docket list` and `docket next` reads past until
it closes. The project owner raised this unprompted on 2026-09-01 - "some
things feel a little bit, like, overkill" - which is precisely the signal
Fowler names as the thing to act on: "be aware of any time you feel
discouraged from doing a small refactoring, one that you're sure will only
take a minute or two. Any such barrier is a smell that should prompt a
conversation."

Note what this does *not* claim. It does not reduce the 73 items already open;
it slows the rate at which trivial ones are added. The compounding-friction
test in `CLAUDE.md` is therefore not obviously met, and this was not
recommended for immediate work on that basis.

**Where.** `CLAUDE.md`, the "Capture, always, and capture cheaply" bullet, and
the `docket` skill's "Mode: capture". Prose only - see the no-code constraint
below.

**The design, as agreed on 2026-09-01.** A session may fix a finding in the
session that found it, without filing an item, when all of these hold. Any one
failing means file the item instead.

1. **It needs no new test.** Absolute, everywhere. `CLAUDE.md` already
   requires a regression test for a safety-critical bug, so safety- and
   science-classed work fails this test automatically - the clinical paths
   need no separate carve-out, which is why this test is first.
2. **It touches no file outside what the current item's work already
   touches.** Deliberate divergence from Fowler - see below.
3. **No reasonable person could prefer the current state.** A typo, a stale
   doc line, a dead import, a wrong error string. Not a rename, an extracted
   helper, or anything where the present code is a defensible choice: that is
   a decision, and decisions are items.

**At most two per branch.** The third means stop and file. Fowler leaves this
to judgement ("skilful opportunistic refactoring requires good judgement,
where you decide when to call it a day"); a hard count is the deliberate
divergence, because knowing when to stop is the judgement an agent session is
most likely to rationalise past.

**How a fix is recorded.** Its own commit on the branch, subject led by the
*current* item's id, plus one line in the session's reply. No item file, no
triage. `bin/docket flight` recovers in-flight state by parsing commit
subjects, so the leading id keeps the work visible; the separate commit means
the project owner can drop it in a rebase without touching the item's work,
which is what makes granting this safe.

**Considered and set aside** (project owner, 2026-09-01, having read the
source: "I did like the direction your initial 3 rules were headed more than
his more expanded scope"). Both of these widen the rule, and the narrow
three-test version above is the one to build. Recorded so a later session does
not rediscover them and mistake them for improvements:

- *An extra test or two, in the apparatus only.* Fowler holds it "quite
  reasonable to throw in an extra test or two" within an opportunistic fix,
  which would have relaxed test 1 for `tools/`, `subprojects/docket/` and
  `.claude/` along `CLAUDE.md`'s own two-standards line. Set aside: test 1 is
  what makes the safety exclusion automatic, and an exception anywhere invites
  the argument everywhere.
- *A third disposition - within-branch deferral.* Fowler: "make a note of it
  and come back to it when you are ready. Don't leave it for long, come back
  the same day, before you've hit that final point of being done." Neither
  fix-now nor file-an-item; it removes the cost of interrupting the current
  thread. Set aside as a third path to reason about where two suffice.

**Two deliberate divergences from the cited source, and why.**

- *Locality.* Fowler: "That lack of locality shouldn't stop you from making
  the change now. There's often a temptation to leave a change in another part
  of a code base to another day - but another day often doesn't come." The
  argument rests on that last clause, and it does not hold here: this project
  has a working queue and a `bin/docket next` that surfaces what is in it, so
  the alternative to fixing now is a tracked item rather than oblivion.
  Mechanically, `bin/docket verify` reads the diff for files outside an item's
  declared `touches`, so ignoring locality either produces honest verify
  failures or tempts a session to widen `touches` - the single edit that
  defeats the audit.
- *Feature branches.* Fowler names branch-per-task as his primary structural
  objection, "particularly if the branches live longer than a couple of days".
  This project is branch-per-item by design, so the objection lands; it is
  mitigated only because a branch here lives one session. Recorded as the
  reason the rule is safe in this workflow, not as anything to change.

**No-code constraint.** Prose only: `CLAUDE.md` and the `docket` skill. If the
implementation turns out to want a `docket` subcommand, a new item status, a
ledger file or a script, it stops being a defect in existing instructions and
becomes new workflow capability - at which point it leaves whatever gate holds
it and returns to the queue on its own merits. This constraint is the whole
reason the work is bounded, and it is not to be relaxed in passing.

**Gate placement.** Argued on 2026-09-01 as admissible to v0.2.8's frozen list
- a defect in machinery that release's Goal already names ("the instructions a
session reads before it does anything else"), present before the 2026-08-30
freeze, and prose-only so it does not trip the "new tools, better tools"
exclusion. **The project owner declined that placement**, judging the design
too complicated to land inside a release that is 6 of 38 entries from done,
and directed it to "the next gate or two" - Gate 0 (recorded under v0.4.0) or
Gate 1. Membership is theirs to set when that gate is scoped. `CLAUDE.md`'s
"a behavior change takes effect in the session that asks for it" was
consciously overridden by that instruction rather than overlooked.

**Done when.** `CLAUDE.md`'s capture bullet states when a session may fix in
the session that found the problem, in terms a session can apply without
judgement it will rationalise past, in the three-test form above and not a
wider one; and the `docket` skill's capture mode routes to it rather than
restating it.

**References.**

- Martin Fowler, *Opportunistic Refactoring*, 1 November 2011.
  https://martinfowler.com/bliki/OpportunisticRefactoring.html - supplied by
  the project owner and read in full. Source of the camp-site rule, the
  rabbit-hole caution, the same-day deferral, the locality argument and the
  feature-branch objection quoted above.
- Fowler, *Workflows of Refactoring*.
  https://martinfowler.com/articles/workflowsOfRefactoring/ - not read; cited
  secondhand in session as holding that refactoring and feature work are
  usually too interwoven to separate into distinct commits. Verify before
  relying on it; the separate-commit mechanic above rests on `docket flight`
  parsing commit subjects, not on this.
- SmartBear/Cisco code-review study, as reported secondhand: defect detection
  falls from roughly 87% under 100 changed lines to roughly 28% over 1,000.
  Supports the two-per-branch cap. Primary source not reached; verify before
  citing it as fact.

**What landed.** `CLAUDE.md` gains one bullet directly under the capture rule -
"Or fix it now, through a door this narrow" - carrying the three tests
verbatim, the two-per-branch cap, and the recording mechanic (its own commit
led by the current item's id, one line in the reply, no item file and no
triage). The `docket` skill's "Mode: capture" routes to it in four lines and
restates none of it, per **Done when**.

Two reconciliations the design implied but did not name, both inside the
declared `touches`:

- The **housekeeping bullet immediately below it** made the new rule
  unreachable as written: it requires an item for any work taking "a commit of
  its own", which is exactly the shape the fix-now rule prescribes. Both
  `CLAUDE.md` and the skill's "Mode: housekeeping nobody filed" now carve the
  admitted fix out, on the ground the housekeeping rule actually rests on -
  visibility - since the fix's own commit still leads with the current item's
  id and every id-matcher still sees it. Two cross-references in that bullet
  reading "the rule above" now say "the capture rule" and "the fix-now rule",
  because the new bullet sits between them and their referent.
- **A session holding no item cannot use the rule at all**, stated in the
  bullet as a consequence rather than as a fourth test: there is no `touches`
  for test 2 to read and no id to lead the commit. This is the case that
  otherwise reads as an unstated gap, being the same shape of hole the item was
  filed against.

`docs/WORKING_NOTES.md`'s "Open: when a session may fix a small finding" thread
said in as many words that this design "is not built", which the change makes
false, so it is retitled and rewritten to what now stands - the two durable
lessons it carries about gate placement and about beating the cited source are
kept, being the reason that section exists. `docs/WORKING_NOTES.md` was added to
`touches` for it rather than the edit being made outside the declaration.

`docs/worker.md` needed nothing and was deliberately left alone. It is outside
`touches`, and its standing "Do not start anything not on your list, however
obvious the fix looks" already denies a delegated worker this rule - which is
the right answer, not an omission.

Resident cost: `CLAUDE.md` grows about 1.5k characters, which `doc_check`'s
resident advisory reports. Disposition 4 is the right one on `CLAUDE.md`'s own
four-way test - the rule fires when a session notices a small problem mid-work,
which no read precedes, so a `paths:`-scoped rule cannot carry it; test 3 is a
judgment, so no check can; and the whole point is that the decision happens
without reaching for the queue skill.
