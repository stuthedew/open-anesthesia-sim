---
id: PL-V2X5
title: GitHub refuses to arm auto-merge on a pull request that is already green and current ('already in clean status'), and a session merges only by arming, so arming on green under the owner's merge rule and docs/maintainer.md's ask-the-session-to-merge route both leave such a pull request waiting on the owner's click; seen on #1086
priority: P2
effort: S
status: done
classes: defect, docs
feature: review-hold
milestone: v0.5.12
touches: docs/maintainer.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-09-26
pr: 1106
payoff: a pull request the owner asks a session to merge never sits green waiting on a merge nobody makes: the session arms it while its checks run, or tells him the click is his
verify: grep -qF 'the session tells you it cannot arm it' docs/maintainer.md && grep -qF 'cannot be merged immediately' docs/maintainer.md && grep -qF 'Answered 2026-09-26: keep the rule' docs/items/PL-V2X5-github-refuses-to-arm-auto-merge-on-a-pull.md
---

**Problem.** GitHub refuses to arm auto-merge on a pull request that is already green and current ('already in clean status'), and a session merges only by arming, so arming on green under the owner's merge rule and docs/maintainer.md's ask-the-session-to-merge route both leave such a pull request waiting on the owner's click; seen on #1086

**Evidence, 2026-09-26.** `#1086` (PL-GPJ7 step 2) went green on a head current with `main`, `bin/docket arm` answered `hold` for a read only, and the thread went to arm it on green, as the owner's merge rule has it. `enable_pr_auto_merge` answered: "The pull request is already in clean status (all checks passed). Auto-merge only applies when checks are pending — you can merge directly." `CLAUDE.md` has a session merge only by arming, so the green pull request waited on the owner's **Squash and merge**. The same state defeats `docs/maintainer.md`'s "ask the session that opened the pull request to merge it" whenever the branch is already current, since that route arms and brings the base in, and there is no base to bring.

**What arming while CI is pending would change.** A session that arms at its last push, rather than on green, never meets the clean state; a thread told to arm on green arms into the refusal. Which of those the owner's rule means, and whether `docs/maintainer.md` should say a current, green pull request is his to merge, is the triage question.

**GitHub's rule, checked 2026-09-26.** "The option to enable auto-merge is
shown only on pull requests that cannot be merged immediately," and auto-merge
"is disabled if someone without write permissions pushes new changes to the
head branch" (GitHub Docs, [Automatically merging a pull
request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request)).
So a pull request can be armed only while a check is pending, the branch is
behind or a review is owed, and a session's own later pushes, made with the
owner's write access, leave it armed.

**Why it matters.** A thread told to arm on green arms into that refusal and
leaves a green pull request waiting on the owner, which is the wait his rule
was written to spare him (`#1086`). And `docs/maintainer.md` offers a route,
asking the session that opened a pull request to merge it, that fails in
exactly the case where the pull request is ready: already green and current,
with no base to bring in and no check left to wait on.

**The owner's rule, read here.** His words, in the Fix generators project
timeline at 2026-09-25T22:11:36Z: "Don't need to wait on review for merge
unless there is a specific question for me. I don't need to eyeball when no
question". They release the wait on his review and say nothing about waiting
for CI. "Once its checks are green" came in with the coordinator's
acknowledgement of them, fourteen seconds later. An armed pull request merges
on green by itself, so arming at the push that marks a pull request ready,
while its checks run, is the same merge on green without the refusal. That
reading changes no outcome and is a session's to take, so this item takes it:
a pull request that `bin/docket arm` holds only for a read, with no question
for the owner, is armed at the push that marks it ready, not after its checks
pass. The project's coordinator already briefs threads that way.

**Decision needed.** What happens when the owner asks a session to merge a
pull request that is already green and current. GitHub will not arm it, and a
session merges only by arming, because its GitHub calls are the owner's and an
admin's merge passes the up-to-date rule `main` holds everyone else to
(`CLAUDE.md`, the bullet on bringing `origin/main` into an open pull request).
Two answers:

- **Keep the rule and say so in `docs/maintainer.md`.** The session answers
  that it cannot arm a pull request that can merge now, and the **Squash and
  merge** is his, as step 1 of "Bring a stale base in when you merge, with
  Update branch" already says for his own route.
- **Let a session merge that one pull request directly.** When GitHub refuses
  to arm because the pull request is clean, the session merges it through the
  API, pinned to the head it has just read as clean. It saves his click, but it
  is an admin merge: the API can pin the head and not the base, so a merge that
  lands between the read and the call leaves the branch behind, and this one
  merges anyway. That is the merge skew `PL-6MW8` made `main` refuse.

**Recommendation: keep the rule and document the case.** With the reading
above, a pull request reaches green unarmed only while it waits on a real
question, and the owner's answer to one is usually recorded by a push, which
reopens the window to arm. What is left is a merge asked for on a pull request
needing no push, on a base nothing has moved since its checks passed, which is
rare with several sessions merging, and it costs one click on the Mac. The
alternative trades that click for a standing exception to the only rule that
keeps a session's merge from passing branch protection.

**Answered 2026-09-26: keep the rule** (project owner, 2026-09-26, ratified,
over letting a session merge a green, current pull request directly through
the API). Chosen on a decision card in the Fix generators project, whose
consequence read: "docs/maintainer.md says that case is your Squash and merge
on the Mac, and the session tells you so." The paragraph of
`docs/maintainer.md` § "Bring a stale base in when you merge, with Update
branch" that offers asking the session to merge now says so.

**Done when.** The paragraph of `docs/maintainer.md` that offers asking the
session to merge says what happens when the pull request is already green and
current, as the owner's answer above has it, and this item records his answer
beside the question.

**Generator check.** One-off: the fact misread is GitHub's rule that
auto-merge is offered only on a pull request that cannot merge now, an external
behaviour nothing here records, and no other item misreads it (no other item
file mentions a clean status, a pull request that could merge immediately, or
arming refused).

**Joined the Fix generators project's list 2026-09-26** (project owner,
2026-09-26). Asked in the project timeline whether anything else was left for
generators, the coordinator named the seven items filed overnight, this one
among them, as staying out of scope unless he added them, and the owner
answered "Add them". Recorded here by the thread that took it.
