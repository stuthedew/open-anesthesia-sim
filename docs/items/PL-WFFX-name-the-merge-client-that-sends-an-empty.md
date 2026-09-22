---
id: PL-WFFX
title: Name the merge client that sends an empty commit_message, which only the project owner can do: affected merges cluster by sitting at 98.3% and by owner-local hour at p=5e-5, but GitHub records no client identity
priority: P2
effort: S
status: needs-decision
classes: defect
feature: pr-body-integrity
touches: docs/items, docs/maintainer.md
added: 2026-09-20
payoff: turns a 27% silent loss of design reasoning from something detected after the fact into something that stops happening, by naming the one variable only the owner can see
root-cause-of: PL-843V, PL-M7W1, PL-G7ST, PL-BXNH, PL-F8Q7
generator: live - squash commits take client-sent commit_title/commit_message that no check reads; 8 bodies lost since #800, 4 unrecovered on 2026-09-22 (PL-KVDK)
---

**Problem.** `PL-843V` established the mechanism by which 187 of 683 squash
commits reached `main` with no body: the merge is submitted with an
*explicitly empty* `commit_message`, which GitHub honours literally over this
repository's `squash_merge_commit_message: PR_BODY`. It also established that
what sends it is a property of the *sitting* rather than of the pull request.
What it could not establish is which client that is, and that is the only half
that turns detection into prevention.

**The evidence, all of it from `merged_at` and the `auto_merge` object.**

- Merges less than 60 seconds apart agree on affected-or-not **98.3%** of the
  time against 60.2% by chance; 15-minute sittings of three or more merges are
  label-pure **80.9%** against 25.0% expected.
- Owner-local hour separates at permutation **p = 5e-5**, holding when labels
  are shuffled within each calendar day. **05h is 15/15 affected, 17h is
  27/38**, while **00h, 14h, 22h and 23h hold 97 merges and zero**. The band
  replicates blind on a held-out second half, 45.9% against 11.8%.
- Affected merges land a median **483 s** after CI goes green, against **70 s**
  for the rest - away-from-desk against at-desk.
- Of the pull requests whose `auto_merge` object survived, **9 of 9 affected
  carry `commit_message: ""`** against 0 of 73 unaffected.

**Why this cannot be answered from the tree.** GitHub records no client
identity on a merge: `performed_via_github_app` is null and `committer.login`
is `web-flow` on all 683. Nothing in this repository enables auto-merge either
- `PL-H8YD` records the project owner doing it by hand. So no script, no API
call and no session can close this. It is a question about what the owner was
holding at five in the morning.

**Why it matters.** The loss is silent and permanent. A pull request body is
this repository's squash commit message, so what goes missing is the design
reasoning itself - and it goes missing in a way nothing surfaces: the pull
request still reads correctly on GitHub, and `git log` shows a subject line
that looks deliberate. `PL-843V` recovered the 187 already lost and added a
check that reports the next one, but recovery only works while the body is
still on GitHub. A body edited, or a repository migrated, takes it for good.
At the measured rate, roughly one merge in four is still losing its reasoning,
and every one of those is a race between the next session noticing the
advisory and the record becoming unrecoverable.

**Decision needed.** Which client do you use to merge when you are away from your
desk - the GitHub mobile app, the web UI on a phone browser, something else?
And when you enable auto-merge, is it from that same client? If the answer is
the mobile app, the remedy is one habit: merge from the desktop web UI, or
check the squash body before confirming.

**The client is named** (project owner, 2026-09-20): "I use github app to
merge when away and do use auto merge at times." That closes the timing half -
the away-from-desk hours the affected merges cluster in are the hours the
GitHub mobile app is being used - and leaves only the direct observation.

**Auto-merge is not the cause, and is the safer of the two routes.**
Cross-tabulated over all 683 squash merges, every pull request fetched
individually rather than sampled:

| `auto_merge` shape | body lost | body kept |
| --- | --- | --- |
| `commit_message: ""` | **9** | 0 |
| `commit_message: null` | 0 | 49 |
| `commit_message: text` | 0 | 24 |
| no `auto_merge` object (merged directly) | 178 | 423 |

An empty string loses the body every time and a null never does, which is the
mechanism. But auto-merge as a *route* loses 9 of 82 (11.0%) against 178 of
601 (29.6%) for a direct merge - so stopping auto-merge would move merges onto
the worse path. Six of the nine empty-string cases fall in the away-from-desk
hour band against 11 of the 73 safe ones.

`#800`, whose auto-merge the owner enabled at 2026-09-20T20:17Z, carries
`commit_message: null` - the safe shape - so the pull request that recovered
the 187 will not join them.

**What is still not observed directly.** No client is recorded on any merge, so
the chain is circumstantial: an empty string always loses the body (9 of 9),
the affected merges cluster in away-from-desk hours, and the owner uses the
mobile app when away. The 178 direct merges carry no `auto_merge` object at
all, so for those the field cannot be read either way. **The decisive test is
one merge**: enable auto-merge from the mobile app on any open pull request and
read `auto_merge.commit_message` before it merges - `""` confirms the app,
`null` exonerates it and moves the suspicion to the direct-merge path.

**Done when** the mobile app is confirmed or exonerated by the one-merge test
above, and either a habit or a tooling change prevents the next empty body - or
it is recorded that no prevention is available and detection via
`tools/pr_body_check.py` is the whole remedy.
