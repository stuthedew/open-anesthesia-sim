---
id: PL-087W
title: bin/docket verify unions removed assertions per commit and never nets them against a later restore, so a line a session puts back on the check's own advice keeps refusing the branch
status: untriaged
feature: verify-assertion-evidence
added: 2026-09-20
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
