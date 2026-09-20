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

**Done when** the client is named and either a habit or a tooling change
prevents the next empty body - or it is recorded that no prevention is
available and detection via `tools/pr_body_check.py` is the whole remedy.
