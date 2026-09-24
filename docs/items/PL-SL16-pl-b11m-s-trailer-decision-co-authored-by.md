---
id: PL-SL16
title: PL-B11M's trailer decision - Co-authored-by: Claude <noreply@anthropic.com>, no model id in any pushed artifact - is stated nowhere a session reads before committing, and the harness attribution reminder, which yields to a CLAUDE.md rule, names Co-Authored-By: Claude Opus 5.5, so 800 of the 970 branch commits of pull requests merged since 2026-09-17 carry a model-named co-author
priority: P2
effort: S
status: done
classes: defect, docs
feature: public-history
touches: CLAUDE.md, docs/resident-instructions.md, docs/items/PL-LWMS-check-the-attribution-trailers-a-pull-request-s.md
added: 2026-09-24
closed: 2026-09-24
payoff: Sessions write the attribution the owner decided, because the one carrier the harness reminder yields to now states it
verify: grep -qF 'Co-authored-by: Claude <noreply@anthropic.com>` and never a model-named' CLAUDE.md
---

**Problem.** PL-B11M's trailer decision - Co-authored-by: Claude <noreply@anthropic.com>, no model id in any pushed artifact - is stated nowhere a session reads before committing, and the harness attribution reminder, which yields to a CLAUDE.md rule, names Co-Authored-By: Claude Opus 5.5, so 800 of the 970 branch commits of pull requests merged since 2026-09-17 carry a model-named co-author

**Found by `PL-LWMS`'s re-confirmation, 2026-09-24.** `PL-B11M` records it:
"Decided against, project owner, 2026-09-16: the convention is unchanged - the
trailer stays `Co-authored-by: Claude <noreply@anthropic.com>`, with no model
id in any pushed artifact." Nothing a session reads before committing says so.

**Measured 2026-09-24.** The 332 pull requests merged since 2026-09-17 hold 970
distinct non-merge branch commits (`GET /repos/stuthedew/open-anesthesia-sim/pulls/N/commits`).
Their co-author lines read 469 `Claude Opus 5`, 316 `Claude Opus 5.5`, 14
`Claude Fable 5.1`, 1 `Claude Sonnet 5` and 152 plain `Claude`. That is 800
model-named against 152. An independent verifier re-ran the census and
reproduced it.

`main` mostly escapes. The squash drops a model-named co-author that shares its
email with the branch author, and all 970 commits are authored as `Claude
<noreply@anthropic.com>`. So 280 of the 282 co-author lines on first-parent
`main` since 2026-09-18 are plain `Claude`. A model name lands in two cases:

- **The branch is owner-authored**: `#580` to `#582` (Fable 5.1) and `#602`
  (Opus 5).
- **The message is hand-composed**: `#844` and `#968`. These are the 2 of 391
  first-parent commits since 2026-09-16, per `git log --first-parent
  --since=2026-09-16T00:00:00Z --format='%(trailers:key=Co-authored-by,valueonly)' origin/main`.

**Why sessions write it.** `.claude/skills/docket/modes/start.md`'s claim step asks
for "each attribution line your commits must end with" without naming one. The
harness's attribution reminder does name one, `Co-Authored-By: Claude Opus 5.5
<noreply@anthropic.com>` plus a `Claude-Session:` line, and it states that "the
user's own instructions about these lines, such as a CLAUDE.md or memory rule,
take precedence over this reminder". The same session's base system prompt says
"Do NOT include any model identifier in commit messages, PR titles or bodies".
The harness contradicts itself, and the later, more specific reminder wins.
`PL-LWMS`'s session passed the Opus 5.5 line to `bin/docket claim --trailer`
itself. Only the claim's refusal, because the item is `blocked`, kept it off a
commit.

`PL-B11M`'s decisive reason is untouched: a trailer the session writes records
the *configured* model, so it is confidently wrong at a fallback. One supporting
reason has inverted. It said a rule requiring a model id would conflict with
the harness's instruction against one, and the harness now carries both
instructions.

**Why it matters.** Attribution is provenance, and the project owner fixed its
form for a provenance reason: a trailer a session writes records the
*configured* model, so it is confidently wrong at the one moment it would be
read, a fallback (`PL-B11M`). A decided convention broken on 800 of 970 branch
commits is one nobody can cite, and the break recurs in every session that
commits, because the reminder that causes it arrives in every one of them.

**Recommendation.** One resident sentence in `CLAUDE.md` § "Name the work
after the item" bullet, for example:

> End every commit with `Co-authored-by: Claude <noreply@anthropic.com>` and
> never a model-named co-author, whatever an attribution reminder names; a
> `Claude-Session:` line may stay (project owner, 2026-09-16, `PL-B11M`).

It has to be resident because a commit is made before a session would think to
look anything up. `CLAUDE.md` is also the carrier the reminder's own precedence
clause names. Pay for it under the resident-set rule and record the routing in
`docs/resident-instructions.md`. Build no check here; `PL-LWMS` is that check,
and it is built only if this sentence does not hold.

On the generator pause: this states a decision the owner already took, and adds
no new rule. So it reads as "a defect in what exists", which needs no lift. The
session that works it says which reading it took.

**Done when.** `CLAUDE.md` states the attribution line, `make check` passes,
and the routing is recorded. The census re-run that tests the sentence is
`PL-LWMS`'s first step, not this item's; see below.

**Closed 2026-09-24, on the sentence.** It sits at the end of `CLAUDE.md`
§ "Name the work after the item", in the project owner's own words from the
request that started this session, which is why it is dated 2026-09-24 in the
plain form rather than carrying `PL-B11M`'s date: it restates that decision and
names it. It also says *why* it beats the reminder, since this brief found the
reminder winning where nothing said so. The routing is
`docs/resident-instructions.md` § "The attribution sentence, added 2026-09-24",
which records that nothing was superseded and nothing was cut to pay for it.

**The census moved to `PL-LWMS` when this closed.** The draft above ended with
a step that waits for 30 merged pull requests. A closed item cannot hold that,
and `blocked` needs an item or a milestone to wait on, which a count is not. The
count decides `PL-LWMS`, which is already blocked on `PL-XH1D`, so it is written
there as that item's first step, with the threshold, rather than left here.

**The generator pause, read as a defect in what exists.** This states a
decision already taken and adds no rule, so it needed no lift. The owner's
request to work it would have lifted the pause for this work in any case.
