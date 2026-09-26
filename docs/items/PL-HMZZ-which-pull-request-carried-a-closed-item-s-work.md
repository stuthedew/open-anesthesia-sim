---
id: PL-HMZZ
title: Which pull request carried a closed item's work is inferred from commit history after the merge and never recorded when the merge happens - ten items, four open
priority: P2
effort: M
status: ready
classes: defect
feature: commit-provenance
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed as a generator head
added: 2026-09-23
payoff: Which pull request carried an item becomes one recorded fact, so a new shape of history stops costing an item
verify: grep -q 'def test_a_closure_on_this_branch_is_written_the_pull_request_number' subprojects/docket/tests/test_cli.py
root-cause-of: PL-2XTF, PL-GW37, PL-YDL6, PL-S5LB, PL-KX9N, PL-YFXG, PL-LPWK, PL-QNYF, PL-GJPD, PL-WG7Q
generator: live - closures_on_base still infers the carrying pull request from merge subjects and _number_closing after the merge, and four members are open (PL-LPWK, PL-QNYF, PL-GJPD, PL-WG7Q)
misread: Which pull request carried an item's work
---

**Problem.** Which pull request carried a closed item's work is inferred from commit history after the merge and never recorded when the merge happens - ten items, four open

**Found 2026-09-23** by `PL-T7Y1`'s generator audit. It came up in the inflow
sweep and survived three skeptics. A second round asked whether `PL-XYQW`
(stored `pr:`) already covers it. All three skeptics said no: `PL-XYQW`'s
record and its spent verdict ("the cut ... writes pr: before the notes
render") cover the timing half, and this is the inference half.

**The mechanism.** Which pull request carried a closed item's work is never
recorded when the merge creates that fact. The merge-time write was removed
(`PL-N5WZ`, #265: a `GITHUB_TOKEN` push starts no workflow, which is in the
digest's dead ends). So `vcs.closures_on_base` infers it later,
from merge subjects (`_merges_naming`) and then `_number_closing`. Each new
shape of history misleads it: a queue-only closure, a triage pass that also
edited `ROADMAP.md`, a rider id that never leads a subject (`PL-GW37`).

**Members.** `PL-2XTF`, `PL-GW37`, `PL-YDL6`, `PL-S5LB`, `PL-KX9N` and
`PL-YFXG` (done); `PL-LPWK` (needs-decision), `PL-QNYF` and `PL-GJPD` (ready),
and `PL-WG7Q` (blocked) are open.

**Not the claim family.** The audit tested whether this is `PL-MB2W`'s record
(who holds an item), since both go through `vcs._annotates_only`. Three of
three skeptics refuted it: a shared function is not a shared record, and which
pull request landed an item is a fact the merge authors.

**Why it matters.** `pr:` is what `docket check` and the release notes attribute work by. Each misattribution is plausible-looking, and ten items in three weeks means inference keeps meeting new history shapes.

**Decision needed.** Where can the carrying pull request be recorded as a fact, given that a merge-time CI write cannot land? One option is the session that opened the pull request writing it on the branch before the merge. The other is keeping inference and closing this head spent. Recommendation: settle it inside `PL-LPWK`, which already holds the open design question.

**The owner's direction, 2026-09-23.** In their words: "I'd rather fix it right once, then fix it twice" (project owner, 2026-09-23). Against this
decision it rules out keeping the inference and closing this head spent. The
durable shape is a pull request number written as a fact before the merge,
not recovered from history afterwards. One candidate, a lead rather than a
finding: the session writes `pr:` once the pull request exists, and the pull
request's own CI checks it, since CI knows its own number. Settle it inside
`PL-LPWK`. Reading the direction this way is this session's call, so ordinary
evidence reopens it.

**Recommendation (design round, 2026-09-25).** Record the number before the
merge, on the branch that closes the item, and have the pull request's own CI
refuse to merge a closure that does not carry it. Then retire the inference.
Three parts:

1. **The writer is the closing branch.** `bin/docket record N` on a branch
   writes `pr: N` onto every closure the branch introduces - done at `HEAD`
   and not at the base, the set `tools/pr_title_check.py` already computes as
   `closes()` - rather than what `closed_by(HEAD)` alone finds. Where the
   draft pull request is already open when the closure is committed, which
   the start mode already permits at the claim push, the number rides the
   closure commit and nothing trails it. Where the pull request opens after
   the closure, per the commit-and-push bullet, the number rides one more
   push. `verify` already sanctions a diff that is only added `pr:` lines
   (`sanctioned_queue_edit`, kind `"pr"`).
2. **The guarantee is a check on the pull request, at the one point that
   knows its own number.** A step in `pr-title.yml`'s job, which is already
   required, already checks out both trees at `fetch-depth: 0` and already
   computes `closes()`: every item this pull request closes records `pr:`
   equal to `github.event.pull_request.number`, else the run fails. Standard
   library, a sibling of `tools/pr_title_check.py`. Because the check is
   required, a merge cannot land between the closure's push and the number's,
   so the `PL-D2GW`/`PL-P5S0` window does not reopen: the closure still
   travels with its work, and only the number may trail it, held by a red
   check until it lands. Building the check needs no lift from the generator
   pause, since it is the fix for a live head.
3. **The inference is retired, and the count says it costs nothing.** On
   `origin/main` at `44f6179f`, 1,099 of 1,103 done items carry `pr:`. The
   four without - `PL-08D4` and `PL-DRRG` in #1003, `PL-YJG1` in #1005,
   `PL-P0FP` in #1007 - landed in the last two days and their numbers are in
   the merge subjects, written once by the explicit `record N --merge SHA` or
   by the v0.5.12 cut. After that nothing on this store depends on
   `_merges_naming`, `_number_closing`, `_carried_work`,
   `_declares_queue_only`, `_walk_following_renames` or `_closed_at` - about
   340 lines of `subprojects/docket/src/docket/vcs.py` and their tests.
   `closures_on_base` shrinks to "which closures landed",
   `_numbers_before_notes` has nothing left to write, and the bare `record`
   goes with it. `_check_closures` keeps its error for a landed closure
   without a number - which can then only be a pre-rule closure or an admin
   bypass of the check - and names `bin/docket record N --merge SHA` as the
   remedy, which is the whole of `PL-QNYF`'s ask.

**Why this and not the alternatives.**

- *Commit-side recovery*, the runner-up: replace the item-side walks with one
  walk of the base's merge commits, newest first, asking `closed_by` what each
  closed. Exact wherever it can answer - a tree comparison by id, so no
  subjects, no renames and no `touches` proxy - in about 40 lines, with no
  CI step and no extra push. It loses because it keeps the timing half: the
  field stays empty until a later full-clone session runs `make fix` or the
  cut, and it declines wherever a parent is out of reach, which are the shapes
  `PL-XYQW`'s six members, `PL-99Y4` and `PL-KX9N` came from. The owner's
  direction above rules out recovering the number afterwards at all.
- *CI writes it onto the branch*: impossible with `GITHUB_TOKEN`, whose push
  starts no workflow and so leaves the head with no checks (`PL-N5WZ`); with
  a personal token it needs a secret to rotate, a bot commit every session
  has to pull before its next push, and a race with that push. Refused.
- *Keep the inference and close this head spent*: ten items in three weeks,
  four open; refused by the owner's direction above.

**What it costs.** One more push and CI run on a pull request opened after
its closure. A check to write, and a step in `pr-title.yml`. `record` learns
the branch form, and may replace the number on an *unlanded* closure only - a
pull request closed unmerged and reopened under a new number - never on a
landed one. `_check_provenance` must pass over an unlanded closure's number:
today it passes over only numbers above the high-water mark, so a branch that
opened #1010 while #1011 merged would fail `docket check` in CI. The close-out
mode's "Leave `pr` empty" and `subprojects/docket/README.md` § "When the `pr`
is owed" are rewritten, since neither stays true. `PL-XYQW`'s ratified "owed
only once shipped" is superseded rather than reopened: nothing is owed after
the merge because nothing can merge without it.

**The members, under this answer.** `PL-LPWK`: its recommendation sits beside
its own question - `pr` names the pull request whose merge closed the item,
which the same-commit rule makes the one that carried the work, and the README
says so. `PL-QNYF`: satisfied by the error rewrite in part 3. `PL-GJPD` and
`PL-WG7Q`: defects in code this retires, dropped with the count above as the
reason once it lands. `PL-XYQW` stays closed.

**Decided 2026-09-25: record before the merge** (project owner, 2026-09-25,
ratified, over commit-side recovery and over keeping the inference and closing
this head spent). The build follows the recommendation above as written: the
closing branch writes `pr:` while its pull request is open, the pull request's
own required check refuses a closure without it, and the inference is retired
with the count above as the evidence.

**Done when.** The pull request that carried an item is recorded as a fact at
a point that can record it, and the readers use that record. Or the owner
decides inference stays, and this head is closed spent with that recorded.
`PL-LPWK` is the open design question closest to this, so read it first.
