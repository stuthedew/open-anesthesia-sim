---
id: PL-WFFX
title: Name the merge client that sends an empty commit_message, which only the project owner can do: affected merges cluster by sitting at 98.3% and by owner-local hour at p=5e-5, but GitHub records no client identity
priority: P2
effort: S
status: done
classes: defect
feature: pr-body-integrity
milestone: v0.5.6
touches: docs/items, docs/maintainer.md
added: 2026-09-20
closed: 2026-09-22
pr: 921
payoff: turns a 27% silent loss of design reasoning from something detected after the fact into something that stops happening, by naming the one variable only the owner can see
verify: grep -q 'PL-WFFX' docs/maintainer.md
root-cause-of: PL-843V, PL-M7W1, PL-G7ST, PL-BXNH, PL-F8Q7
generator: spent - the empty commit_message came from the GitHub iPhone app, which the owner stopped merging in on 2026-09-22 (docs/maintainer.md), and sessions arm auto-merge with a tool that sends no title or message, so none of the 47 squash merges since #918 lost its body; a new empty body reopens it
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

**Both clients named, and the defect is a public, acknowledged one**
(2026-09-22). Asked which client merges, the project owner answered: "Website
and app on iPhone." Whether "website" means Safari on the phone, a desktop
browser or both is not recorded, so a test has to cover both phone clients.

- **The committer timestamp's offset records the route, not the client.**
  Over the 806 squash commits on `main` (`git log --first-parent`, subjects
  ending `(#N)`, bodies counted net of trailers): `+00:00` on 128, 9 bodies
  lost, which is the count of empty-string auto-merges above; `-05:00` on 678,
  192 lost (28.3%), the direct-merge rate. A direct merge carries the owner's
  local offset whichever client made it, so the tree still cannot name one.
- **GitHub's own forum carries the defect.** "Squash and Merge on Github
  Mobile doesn't match the same on web", community discussion #51016
  (https://github.com/orgs/community/discussions/51016), opened 2023-03-25:
  no obvious prompt to confirm the message, and the squash body omitted.
  GitHub staff put the message editor "behind a cog icon" (2023-04-04), cited
  an internal issue (2024-05-10) and a fix in progress (2025-07-09); the latest
  reply (2026-09-16) reports every squash merge that month landing with no
  body. That matches this item's pattern - intermittent, sitting-pure,
  away-from-desk - without being an observation in this repository.

**Recommendation, this session's, for the owner to decide: adopt the habit
now rather than wait on the one-merge test.** Squash-merge, and enable
auto-merge, from the website rather than the GitHub app; on a phone, check the
message box holds the pull request's description before confirming, since the
at-desk hours are the only evidence the website keeps it (97 merges, none
lost). In the app, if it is the only option, open the cog and confirm the
message first. The one-merge test becomes optional confirmation, and
`tools/pr_body_check.py` stays the backstop because a habit can lapse. Once
agreed, the habit goes in `docs/maintainer.md` and this item closes.

**The one-merge test ran, and the app is confirmed** (2026-09-22). Asked to
merge `#918` from the GitHub app, the project owner reported "merged from
phone"; its squash commit `f1e00087` reached `main` at 18:19 -05:00 with an
empty body while the pull request's description stands on GitHub. A direct
merge, so there is no `auto_merge` object to read, but the direct-merge path
is where 178 of the losses above sit.

**Decided: the habit** (project owner, 2026-09-22, ratified, over leaving
`tools/pr_body_check.py`'s after-the-fact detection as the whole remedy). The
owner agreed with the recommendation above. It is written into
`docs/maintainer.md` § "Merge on the Mac or by auto-merge, never in the
GitHub app", where the person merging reads it; detection stays as the
backstop, since a habit can lapse.

**The routes, stated whole** (project owner, 2026-09-22): "i never use my phones
browser. I use mac computer browser, you auto merge, and phone app." That
settles two things left open above. The website is the Mac's browser, so the
test's "merged from phone" was the GitHub app and nothing else. And auto-merge
armed through Claude is a route of its own: the GitHub tool a session arms it
with takes a merge method and no message, so it cannot send the empty string,
which fits the 49 auto-merges with no message set, all of which kept their
body.

**Done when** the mobile app is confirmed or exonerated by the one-merge test
above, and either a habit or a tooling change prevents the next empty body - or
it is recorded that no prevention is available and detection via
`tools/pr_body_check.py` is the whole remedy.
