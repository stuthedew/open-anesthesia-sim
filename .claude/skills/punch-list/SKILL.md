---
name: punch-list
description: Read, add to, and triage this repository's development punch list in docs/PUNCH_LIST.md. Use when the project owner asks what to work on next, what is left, what the priorities are, or whether to start the next roadmap milestone; when they have usage time available and no particular plan; when they flag a bug, cleanup, optimization, or idea to track for later; or when a session's own work turns up a finding that will not be fixed in that session. Also use when they name an item to start working on ("let's do PL-013"), and when asked to reprioritize, groom, or close out punch-list items.
---

# Punch list

`docs/PUNCH_LIST.md` is the prioritized queue of discrete development
tasks. `ROADMAP.md` holds releases; `docs/WORKING_NOTES.md` holds the
narrative behind open threads. Read `docs/PUNCH_LIST.md`'s own header for
the entry format and the priority, effort, status, and class definitions —
this skill covers the workflows, not the file format.

The point of the file is that a session can start work cold from an entry
without re-deriving the problem, and that a planning session can name six
things to do without having to do them before it runs out of usage.

## Mode: recommend what to work on

Triggered by "what should we work on next", "I have some time", "what's
left", "are we in a good spot to move on".

1. Run `make punch-list` before anything else. It is instant, and it gives
   exact counts and any pending advisories — more current than the
   session-start digest, which does not know about items added since. Its
   advisories are a judgment call to put to the project owner, not one to
   act on unilaterally.
2. **Open the reply with the state of the queue, before naming any task.**
   Two lines at most:
   - How many items are open, broken down by priority.
   - Whether grooming is due. If advisories are pending, say how many and
     what they are about, and offer the grooming pass *before* recommending
     work. Do not skip this because there is appealing work at the top of
     the queue — a stale queue gives bad recommendations, and the project
     owner cannot ask for a pass they were never told was due.

   If the owner would rather get on with the work, that is their call: note
   it and continue to the recommendation. The obligation is to surface the
   state, not to insist on acting on it.
3. Then run `python3 tools/punch_list.py list` for the queue itself: one
   line per item, carrying band, effort, status, and model guidance — every
   field the choice below actually turns on. Read the full briefs only for
   the two or three items you are going to name, and the whole file only
   when this is a grooming pass. The listing costs a fortieth of the file
   and the file is mostly brief prose that matters once an item is chosen,
   not while choosing between them.

   Do not survey the codebase first — the queue exists so that step is
   unnecessary. Equally, do not recommend from the listing alone: a
   one-line title is exactly the kind of thing that looks actionable and is
   not, and the brief is what says whether the item is still real.
4. Ask how much time or usage is available if it is not obvious, since it
   changes the answer between an `S` and an `M`. Ask once, briefly, and
   only if it is genuinely ambiguous.
5. Recommend in this order:
   - Any `P0`. These come before feature work; say so plainly and follow
     "Mode: hotfix" below.
   - The highest-priority `ready` item whose effort fits the time
     available. Prefer finishing a priority band before dipping into the
     next one, but do not recommend an `M` when only an `S` fits.
   - If everything that fits is `needs-decision`, offer the decision
     itself as the work — resolving it is usually short and it unblocks
     the item for a later session.
   - If the punch list is in good shape and the question is really "should
     we move on to the next feature", the answer is milestone work: scope
     the next milestone in `ROADMAP.md`. Never start unscoped feature work.
6. Give a short recommendation with the reasoning, not a dump of the file.
   Name the top candidate, one or two alternatives with their effort, and
   what each would take. The project owner picks.
7. **State which model the work warrants, independent of what this
   session happens to be running.** This is not a suggestion to weigh —
   `CLAUDE.md`'s "Session and tool-use efficiency" section states the rule:
   an item tagged `safety` or `science`, or one still at `needs-decision`
   (an unresolved design question is exactly the "ambiguous problem or
   genuine trade-off" that section names), is reasoning-heavy work and
   warrants the strongest available model at a high effort setting — for
   both writing the change and reviewing the final diff — regardless of
   whether the current session is on a cheaper model. Everything else is
   routine execution, where the default model is fine.

   `tools/punch_list.py` encodes this same rule (`Entry.model_guidance`)
   and the session-start digest already applies it to the top P0/P1 lines,
   but check it explicitly for whatever is actually being recommended,
   since the digest may be stale or the recommendation may differ from the
   digest's top pick. Say it plainly: "this is safety/science-tagged (or:
   has an open design decision) — start it in `opusplan` or your strongest
   model at high effort," or "this is routine execution — your current
   model is fine." A model switch mid-session costs a cold cache
   (`CLAUDE.md`), so say this *before* work starts, as part of the
   recommendation, not after.
8. Recommend that the work start in a *fresh session* rather than
   continuing this one whenever either is true:
   - the work is substantial or safety-critical; or
   - this session is already long, or was about something else. This
     includes the session that just finished editing the punch list
     itself, whose context is about the queue rather than about any item
     in it.

   The second case is the one that gets missed. A short item is cheap to
   start, but not at the end of a long session whose whole context is
   resent on every turn and has nothing to do with the item. Recommending
   an item and starting it here are different acts; do not let the first
   slide into the second by default.

   This step only advises. When the owner then names one of the candidates,
   "Mode: start an item" below decides where the work happens and acts on
   that decision without asking. The criteria there are these, stated for
   the moment the work actually begins.

   When handing off, say what the fresh session should read first:
   `CLAUDE.md`, the entry itself, and any `docs/WORKING_NOTES.md` thread it
   cites. Entries are written to be actionable cold precisely so that this
   handoff costs nothing.

   End the handoff with the exact line to paste as that session's first
   message, on its own and nothing else on it:

   ```text
   PL-013 Triage the review harness's remaining findings
   ```

   Do not paraphrase this into "open a session about PL-013". On a surface
   that derives the session name and the branch name from the opening
   message, that message is the only thing that can still set the branch
   name, and it names both correctly only if the ID and title are actually
   in it: `claude/pl-013-triage-review-harness-findings`, from a session
   already called "PL-013 Triage the review harness's remaining findings".
   See "Naming the work after the item" below.

## Mode: start an item

Triggered by the project owner naming an item to work on — "let's do
PL-013", "start the halted-step decision", or picking one out of a
recommendation this session just gave.

**Decide where the work happens and act on the decision. Do not ask.** The
choice is between this session and a fresh one; it is a cost question with an
objective answer, and it does not change what gets built.

1. Read the entry's brief first. None of what follows is decidable from a
   title, and an item that turns out to be `needs-decision`, blocked, or
   already stale changes the answer before the question of *where* arises.
2. Continue in **this** session when its context is an asset:
   - it is short, or already about this item — including the session that
     just recommended it, when that recommendation was its only work;
   - it just diagnosed the problem the entry describes, or holds discussion
     that the entry does not;
   - the item is `S` and nothing unrelated has landed here yet.
3. Start a **fresh** session when this one's context is a liability:
   - it has already completed a different item, or is about a different
     topic;
   - it is long, so the item's every turn resends context that does not help
     it;
   - the item warrants a model this session is not running (step 7 above). A
     model switch costs a cold cache either way, so the fresh session is
     strictly cheaper and starts correctly named;
   - the item is `M` or larger and this session has any unrelated history.

   When signals disagree, "already completed a different item" and "needs a
   different model" decide it: both make every later turn here cost more than
   the same turn elsewhere. Otherwise prefer continuing — an unasked-for
   session the owner has to go find is its own kind of cost.
4. If continuing here: name the work per "Naming the work after the item"
   below, renaming the session *before* the first edit, and start.
5. If starting fresh, open it rather than describing it. On Claude Code on
   the web and other remote sessions, `create_session` on the
   `claude-code-remote` MCP server takes everything the naming rule needs:

   - `title` — `PL-013 Triage the review harness's remaining findings`.
   - `outcome_branch` — `claude/pl-013-triage-review-harness-findings`. This
     is the one path on this surface where a session controls a branch name
     outright, so always set it; it is why spawning beats telling the owner
     to open a session by hand.
   - `model` — what the item warrants, not what this session happens to run.
   - `tags` — `["pl-013"]`, so the session is findable from the entry alone.
   - `prompt` — a standalone instruction, since the new session starts from
     nothing. Name the id and title, point it at `CLAUDE.md`, the entry in
     `docs/PUNCH_LIST.md`, and any `docs/WORKING_NOTES.md` thread the entry
     cites, and say which branch it is on. Do not restate the brief: the
     entry is written to be read cold, and copying it into a prompt is how
     the two drift apart.

   Leave `permission_mode` unset so it inherits this session's. Never pass
   `plan` to a session nobody is watching — it blocks on an approval prompt
   that never comes.
6. Report the decision in a line or two: which session, title, and branch the
   work went to, or that it is proceeding here, and the reason. Never spawn
   silently. Then stop — do not also start the work here. Two sessions on one
   item is worse than either choice made badly.
7. On a surface with no such tool, the fresh-session path is a handoff
   instead: end with the paste-ready line from step 8 above and say the
   branch name that will follow from it.

## Naming the work after the item

`CLAUDE.md` requires the ID on the session name, the commit subjects, and
the pull request title. The commits and the pull request title are available
in every session and outlive the branch, which is deleted at merge. The
other two depend on the surface.

**The session name.** Rename as soon as the item is chosen, before the first
commit — the whole point is that someone scanning a session list later can
find the work from the entry alone, and a session still called "next
priorities" is unfindable however good its commits are. Name every item the
session addresses, not only the first: "PL-035, PL-039 Two related
punch-list fixes".

- On Claude Code on the web, and any other remote session, call
  `set_session_title` on the `claude-code-remote` MCP server. It needs the
  session's own id, which `get_session` returns when called with no id.
- A local CLI session has no title to set. There is no `/rename`, and
  `/clear <name>` labels the *previous* conversation rather than this one,
  so there the commit subjects carry the whole load.

Unlike the branch, this is settable at any point in the session, so a
session that discovers mid-run which item it is really working on still
renames itself. "The branch was already named" is not a reason to skip it.

**The branch name.** Best-effort, and the difference is the surface rather
than the session:

- A branch the session creates itself — a local checkout, or any
  `git checkout -b` it runs — can be named after the item the moment the
  item is chosen. Name it `claude/pl-0NN-short-slug`.
- A branch created *for* the session before it starts is fixed before the
  queue has been read. Claude Code on the web derives one from the opening
  message and adds a random suffix, so a session that opens with a question
  ("what should we work on next?") gets a branch that names the question,
  not the item it goes on to work. Pushing a differently named branch
  instead is possible with the project owner's permission, but it strands
  the generated branch on the remote as litter and detaches the session from
  the changes the web interface offers to open a pull request from.

So the branch is best-effort and the commit subjects are not. A session on a
branch whose name carries no ID has not broken the rule; it owes the ID to
the commits and the pull request title, and one line in its reply saying so.
The session-start digest raises this by itself on any branch without an ID
in the name.

The one moment a generated branch name can still be chosen is the handoff in
step 8 above: whatever the recommendation tells the project owner to paste
becomes the next session's first message, and that message becomes its
branch name.

## Mode: capture a new item

Triggered by the project owner flagging something — including mid-task, as
an aside, while this session is working on something else — or by a finding
a session makes on its own that will not be fixed in that session.

**Decide where it goes first, and decide it from what this session is
already doing rather than from how good the finding is.**

- **`docs/inbox/`** is the default, and it is the whole answer to "can I
  raise this while you are in the middle of something". A note is a new file
  carrying no `PL-` id, so it cannot conflict with a note another branch
  added and cannot race another session for the same id — the two ways a
  mid-task punch-list edit actually breaks things. `docs/inbox/README.md`
  carries the format and the reasoning.
- **`docs/PUNCH_LIST.md` directly** in two cases. When this session's work
  *is* the queue — a grooming pass, a recommendation, a close-out — the
  entry is the commit rather than a detour inside one, and there is nothing
  in flight for it to collide with. And when the finding is `P0` or
  safety-critical, which has to be visible in the queue and in the
  session-start digest now, not after a triage pass; take the conflict risk
  and say in your reply that you did.

Never hold a finding in the conversation until the current work lands. A
session's container is ephemeral, so a thought that is only in the
conversation is a thought that is one interruption from being lost, and
that is the failure this whole file exists to prevent.

### Writing it

1. Write it for a reader with no memory of the originating conversation:
   problem, why it matters, where in the code, first step, and the condition
   that closes it. Do this in the capturing session even for a note — the
   context is live here and gone by triage, and the brief is the expensive
   half. If the thought is genuinely half-formed, say what was observed and
   what is not yet known rather than inventing a brief around it.
2. For a note, stop there: name the file for the day it was captured, as
   YYYY-MM-DD-short-slug.md under `docs/inbox/`, add the
   proposed band as the optional metadata line only if this session knows it,
   and commit it on its own so it survives a branch that is later abandoned.
   The next two steps are triage's, not yours.
3. For an entry, allocate the next unused `PL-` id — one past the highest
   that appears anywhere in the file, including "Recently completed" and
   "Archive" — and place it at its correct priority, which may demote
   something else.
   Anything on a safety-critical path per `CLAUDE.md` starts at `P0` or
   `P1`, regardless of how small it is.

   Work classed `session-cost` — work that reduces what a session spends on
   process rather than on the product — is also worth promoting, because its
   payoff compounds across every session after it. Tag it `session-cost`,
   not `perf`: `perf` is the running application, `session-cost` is the cost
   of developing it. But that promotion has a ceiling, and it is the one
   rule here that has actually misfired: process work accumulated until it
   held four of the seven items in `P1`, ahead of the simulator's own
   science and safety items. **Process work does not enter `P1` when doing
   so would leave it outnumbering the product work already there.** Put it
   at `P2` instead and say why. `make punch-list` checks this.
4. If the reasoning is longer than the brief holds, put the long form in
   `docs/WORKING_NOTES.md` and cite the `PL-` id in that thread's heading.
   A note has no id to cite yet, so keep its reasoning in the note and move
   it at triage.
5. Do not ask permission to record something. Capture at `P3` rather than
   dropping it, and mention in your reply that you did — and say which of the
   two places it went, since one of them still needs a triage pass.
6. Capturing is not doing. Unless the project owner asked for the fix,
   record it and continue the current task. This is what makes an aside cost
   the session almost nothing: one file, one commit, back to the work.

## Mode: triage the inbox

Triggered by the session-start digest or `make punch-list` reporting notes
pending, or by a grooming pass, which should always start here — grooming a
queue that is missing half its recent input reprioritizes the wrong set.

Triage is where the ids are allocated and the bands are chosen, so unlike
capture it is not safe to do from two places at once. Do it when the punch
list is otherwise idle: on a branch of its own from current `main`, or as
the first act of a session whose work is the queue. Do not triage from
inside unrelated feature work — that reintroduces exactly the conflict the
inbox removed.

1. `make punch-list` lists what is pending, with each note's proposed band.
2. Read each note in full. The proposed band is a starting point from a
   session that had the context, not a decision: place the entry where it
   belongs against the queue as it stands now, which may demote something
   else, and apply the same rules capture does — safety-critical work starts
   at `P0` or `P1`, process work does not enter `P1` when it would outnumber
   the product work there.
3. Allocate ids in filename order, so the ids run in capture order.
4. Delete each note in the same commit that adds its entry. A note that
   survives its own triage becomes a duplicate finding.
5. A note that should not become an entry still leaves a record: put a line
   in `Archive` with the date and a one-clause reason. An idea dropped
   silently is an idea that gets raised again, and the project owner cannot
   tell a rejection from an oversight.
6. Re-run `make punch-list`. It should report a clean file and an empty
   inbox.

## Mode: close out a completed item

Triggered whenever work from an entry lands. Run this before reporting the
item done, not after the project owner asks whether the docs were updated.

1. Move the entry to "Recently completed" with its commit reference, and
   delete any now-resolved `docs/WORKING_NOTES.md` thread for it. Leaving
   the thread is what trips the checker's advisory. Never delete the entry
   outright: "Recently completed" is a window on the permanent "Archive"
   ledger, not a substitute for it.
2. Sweep the docs for drift the change just caused, per `CLAUDE.md`'s
   "Sweep the docs before calling an item done." Do not start by grepping:
   two commands do the mechanical half, and doing it by hand at the end of a
   session is what has let drift through before.

   - `make doc-check` decides the three failure modes that need no judgment:
     a module missing from `docs/ARCHITECTURE.md`'s package map or left there
     after deletion, a data-file constant missing from `docs/MODEL.md`'s
     provenance table or carrying a value the JSON no longer holds, and a
     cited path or section heading that resolves to nothing. These are
     errors, so `make check` and CI already refuse the change; fix them.
   - `python3 tools/doc_check.py candidates --base <ref>` prints the
     documentation lines that mention anything this diff touched. That is the
     grep, already run. Read the list.

   Then spend the judgment on what no tool can decide, which is whether each
   statement is still *true*. The recurring failure modes in this repository,
   all of which have actually happened:
   - a shipped feature still described as deferred or out of scope;
   - a `docs/MODEL.md` `must`/`must not` the code no longer satisfies;
   - a `WORKING_NOTES.md` thread describing a problem that has been solved;
   - a paragraph that is accurate about the code but describes it as the
     reason for a decision that no longer applies.

   A finding the checker reports is a defect in one of the two: decide
   whether the document or the code is wrong, and say which, rather than
   editing the document until the tool goes quiet.
3. Fix the drift in the same change as the code. A doc fix deferred to
   "later" is drift that outlives the session that could still explain it.
4. Distinguish history from current state. A completed milestone's
   out-of-scope list is a record of what that milestone chose, and stays as
   written; annotate it with what landed afterwards rather than rewriting
   it. Statements of what the project *is* today must match today.
5. Capture anything found but not fixed as its own entry, per the capture
   rule, rather than leaving it in the reply only.
6. Re-run `make check` after the doc edits — it runs both checkers — then
   say in your reply which files you checked.

## Mode: hotfix a P0

1. Branch rather than working on `main`. Existing conventions in this repo:
   `build/vX.Y.Z-slug` for milestone work, so use `fix/pl-00N-slug` for a
   hotfix.
2. Bump the patch version in `pyproject.toml`. That is the single source —
   `app_metadata.py` resolves the displayed version from package metadata,
   so nothing else needs editing.
3. Add a regression test that would have caught it. This is required, not
   optional, for anything on a safety-critical path.
4. Run `make check` (Ruff format, Ruff lint, strict mypy, pytest) before
   committing.
5. Move the entry to "Recently completed" with its commit reference in the
   same change.

## Mode: groom

Triggered by the session-start digest reporting advisories, by `make
punch-list` output, or by a direct request.

1. Run `make punch-list` first. It reports the mechanical findings, so the
   session spends its judgment on the rest rather than on rereading the
   file. Errors mean the file is broken and must be fixed; advisories are
   the agenda for this pass.
2. Re-read the priorities as a set, not one at a time. Ask whether the top
   `P1` is still the thing that should happen next.

   Most of a grooming pass is the shape of the top band, not the length of
   the file — a session reads the band it would pick from, not the whole
   queue. Three things make that band unreadable, and `make punch-list`
   reports each of them directly: it holds more than about five items, most
   of what is in it is `needs-decision` rather than `ready`, or process work
   (`session-cost`, `docs`, `infra`) outnumbers the product work beside it.
   The remedy for all three is demotion, not deletion. Where the third one
   fires, the items to demote are the process ones, however compounding
   their payoff: `CLAUDE.md` ranks the simulator's correctness above the
   workflow that builds it.
3. Promote `blocked` items whose blocker has landed.
4. Split any entry that has grown two independent halves — a smaller piece
   that fits leftover time is more useful than one large item that never
   gets picked up.
5. Promote `L` items into scoped `ROADMAP.md` milestones, or leave them in
   the icebox with a note saying scoping is the next step.
6. Record every disposal in "Archive"; never delete an entry outright.
   An item dropped, folded into another entry, or superseded gets an
   `Archive` line with the date and a one-clause reason — the reason is
   what stops the next session re-raising the same finding. Trimming
   "Recently completed" also means *moving* its lines to "Archive", not
   deleting them: `ROADMAP.md` and `docs/WORKING_NOTES.md` cite completed
   ids permanently, and the checker errors on a reference it cannot
   resolve.
7. Delete resolved `docs/WORKING_NOTES.md` threads rather than leaving them
   stale.
8. Re-run `make punch-list` before finishing; it should come back clean.

## Always

Run `make punch-list` after editing the file. It is instant, it gates
`make check` and CI, and its errors mean an item is about to be silently
lost.

Prefer `python3 tools/punch_list.py list` over reading `docs/PUNCH_LIST.md`
whenever the question is *which* item rather than *what* an item says. Read
the file whole when grooming or reprioritizing, where the briefs are the
subject; read a single entry when implementing it.

Commit punch-list changes with the work they describe when there is
related work, or on their own when there is not. An uncommitted punch list
is a lost punch list — this session's container is ephemeral.
