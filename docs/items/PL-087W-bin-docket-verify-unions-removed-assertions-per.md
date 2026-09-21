---
id: PL-087W
title: bin/docket verify unions removed assertions per commit and never nets them against a later restore, so a line a session puts back on the check's own advice keeps refusing the branch
priority: P2
effort: M
status: ready
classes: defect, infra
feature: verify-assertion-evidence
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-20
payoff: putting a flagged assertion back clears the check, so the response the check asks for is one a session can actually complete
verify: grep -q 'def test_an_assertion_restored_in_a_later_commit_is_not_counted' subprojects/docket/tests/test_verify.py
---

**Problem.** bin/docket verify unions removed assertions per commit and never nets them against a later restore, so a line a session puts back on the check's own advice keeps refusing the branch

**Found 2026-09-20 on `PL-0RZ0`'s branch**, by doing what the check asked.

`verify_item` selects its diff from the commits naming the item and reads
removed assertions out of that union. A line removed in one commit and restored
verbatim in a later one is therefore still counted, though the branch's final
tree contains it.

Reproduced on `claude/optimistic-babbage-ycycwq`:

```
$ git show f7d9afa -- tests/ | grep '^-.*assert'
-    assert chart.readout_at(time_s, on_trunk + 2.0 * percent_per_pixel) == readout
-    assert chart.readout_at(time_s, on_trunk - 2.0 * percent_per_pixel) == readout
$ git show ed360cd -- tests/ | grep 'on_trunk - 2.0'
+    assert chart.readout_at(time_s, on_trunk - 2.0 * percent_per_pixel) == readout
$ git diff origin/main...HEAD -- tests/ | grep -c '^-.*assert'
5
$ bin/docket verify --self PL-0RZ0
  FAIL  no existing assertion removed - 6 line(s)
```

Five in the net diff, six in the check. The sixth is the `- 2.0` line, which
the second commit restored **because the first run of the check had flagged
it**.

**Why it is worth fixing rather than knowing about.** The check's whole purpose
is to make a session account for a removed assertion, and the intended response
to a legitimate flag is to put the assertion back. That response cannot clear
the check, so a session that does the right thing sees the same refusal and
learns that the count is not about its tree. That is the "advisory being routed
around" shape `CLAUDE.md` names, arriving through a count rather than through
wording.

**Where.** `subprojects/docket/src/docket/verify.py`, `verify_item` - the
`removed_assertions` selection, upstream of `replacements`, `literal_swaps`
and the `dropped` list. The other five folds all ask *why* a line went; this
asks whether it went at all, so it belongs before them.

**A caution for whoever takes it.** Netting must not silently excuse a line
removed from one file and coincidentally added to another, and it must not
depend on commit order. Comparing the branch's final tree against the base -
the same `origin/main...HEAD` shape the reproduction above uses - is the
obvious route and wants checking against `verify`'s per-id diff selection,
which exists so a branch closing several items is audited per item.

**Why it matters.** The check's whole purpose is to make a session account for
a removed assertion, and the intended response to a legitimate flag is to put
the assertion back. That response cannot clear the check, so a session that
does the right thing sees the same refusal and learns that the count is not
about its tree. That is the second of `CLAUDE.md`'s compounding-friction
tests - an advisory being routed around - arriving through a count rather than
through wording, and it is why this ranks above the other two items in
`feature: verify-assertion-evidence`.

**Done when.** A branch that removes an assertion in one commit and restores it
verbatim in a later one clears `no existing assertion removed`, the net diff
against the base is what the count is taken from, and a test under
`subprojects/docket/tests/test_verify.py` drives a two-commit remove-then-restore
against a branch whose final tree holds the line.

## Narrowed by PL-C4W8's Gate 2 staleness sweep, 2026-09-21

**"Never nets them" is wrong, and the correction matters because it moves the
defect to another item.** `_net_line_changes` keys `per_file` on the `diff
--git` header line itself, so an added line and an identical removed line for
the same file fold to nothing across every commit the walk selects, in any
order. A scratch-repo reproduction confirms it: where commit A removes two
assertion lines and commit B restores one with a subject naming the same id,
the netting reports exactly one removed assertion, matching `git diff
main...feature`.

**What actually produced the observed 6-versus-5 discrepancy** is the
*selection* feeding the fold, not the fold. `item_commits` takes only commits
whose subject carries the id, so a restoring commit whose subject names a
different item is never in the diff being netted. That is `PL-2DTK`, which this
sweep confirmed still reproduces.

So this item is either a duplicate of `PL-2DTK` or a thin wrapper on it. Decide
which before working it; do not rebuild the netting, which is correct.
