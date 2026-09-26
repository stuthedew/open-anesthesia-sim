---
id: PL-NZC0
title: A Claude Code Projects trial needs project instructions carrying the approach gate and the queue as the only source of work: the coordinator starts threads by default, and thread limits asked for in conversation are preferences rather than caps
priority: P2
effort: S
status: ready
classes: docs
feature: projects-trial
touches: docs/items
added: 2026-09-19
not-delegable: the work is a trial run in a Claude Code Project and the owner's verdict on it; no command can prove a coordinator saved the owner attention. What proves it is this brief recording the two numbers under Done when, measured at the trial's end.
---

**Problem.** A Claude Code Projects trial needs project instructions carrying the approach gate and the queue as the only source of work: the coordinator starts threads by default, and thread limits asked for in conversation are preferences rather than caps

**Reopened 2026-09-25.** Dropped on 2026-09-19 when the owner declined a trial ("I have it but no thanks. Don't need projects for now"), as a not-yet whose stated reopening was the owner choosing one. On 2026-09-25 they chose one, for the generator sub-goal (project owner, 2026-09-25, ratified, over a coordinator session in this repository driving child sessions through `create_session`, whose children cannot message the parent and send nothing on a clean finish, so the coordinator spends its own context budget polling). The go-ahead lifts the generator pause for this request (`PL-6Q9L`, the owner-lift rule).

Why the 09-19 decline and this trial are both right: for the usual shape of work, one item picked and worked per session, Projects adds nothing, because the owner still starts, reads and merges each one. It pays only for a known, ordered batch the coordinator can start by itself. What it takes off the owner: starting sessions, the per-PR Update branch / wait / squash sequence (the **Merge it** button sends "merge it" to the thread, which arms and brings `main` in per `docs/maintainer.md`), and reading one closing block per session (threads report to one conversation, sorted by the Overview into Waiting on you, Ready for review and Landing). What it cannot take off: the design decisions, and the merge approval itself.

How the 09-19 risks are handled:

- The coordinator starts threads on its own, and a first project posts setup recommendations with routines switched on: send the first message at creation, switch recommended routines off, and the instructions below make the queue the only source of work.
- Thread limits are preferences, not caps: git is the backstop. Recorded claims make a second thread on a held item visible (`show`, `flight` and `next` read them since `#1002`), and a third concurrent code thread surfaces as a merge conflict rather than a silent error.
- Project memory is prose Anthropic stores outside git: the instructions put decisions in item files, and the trial's end checks **Project settings > Memory**.
- Hooks and permission rules load only in a single-repository project: the project has one.
- Not raised on 09-19: the docs load `CLAUDE.md` from each thread's clone and do not say the coordinator conversation has one, so the instructions carry the approach gate themselves.

Sources: https://code.claude.com/docs/en/claude-projects (fetched 2026-09-25); the evidence on coordination (Kim et al., arXiv:2512.08296: independent agents amplify errors 17.2x against 4.4x under central coordination, and lose 70% on sequential work) is why the plan runs two serial streams rather than one thread per item.

**Stress-test additions, decided 2026-09-25** (project owner, 2026-09-25, ratified, over `PL-P0FP`'s proposal as written, which put `PL-KR69` in Stream B although it changes `verify.py`, the file Stream A's `PL-B8HZ` build changes, so the two would have run at once in one file). Folded into the instructions below:

- **The claims paragraph.** Push, claim, and confirm the claim in `flight` before opening a pull request; never commit to a branch whose pull request has merged. Why: `claim` exited 0 without pushing in `PL-P0FP`'s own session (`PL-1X56`) and refused the web harness's branch shape until the branch was pushed (`PL-KX73`). The trial's backstop against two threads on one item is a claim other sessions can see. An item-files-only pull request whose claim is not visible is armed by `bin/docket arm` and merges, after which `branch` and `arm` advise committing to the merged branch (`PL-8BR0`), and an answer recorded there never reaches main. The chain is inferred from the stress test's simulation, not run end to end.
- **`bin/docket yield` for design threads.** Added by the session recording this decision: a claim holds its pull request unarmed until the claim is released (`arming.py`), and a design thread's item stays open for its build, so without a yield its pull request would stay a draft indefinitely.
- **`PL-KX73`, `PL-1X56` and `PL-ZLJ9`** (defects in the claim record) in Stream B before the `PL-MB2W` close-out, which should not close while the record it built carries them. They change `claiming.py` and `claims.py`, which no other stream touches, so the placement is for order, not to avoid a collision.
- **`PL-KR69`** (a rename out of `src/anesthesia_sim/core/` passes `verify --self`'s protected-path audit) first in Stream A: it changes `verify.py` with the `PL-B8HZ` build, needs no design answer, and is a check that passes while the guarantee it stands for is void.

All four were untriaged on 2026-09-25, so the thread that takes one triages it first.

**Stream A refill, decided 2026-09-25** (project owner, 2026-09-25, ratified, over working the new heads in fresh sessions outside the trial, and over the pending recommendation to move the claim fixes and `PL-QHCW` to Stream A; two of those fixes have since landed, `PL-KX73` in #1020 and `PL-1X56`). The heads the 2026-09-25 triage recorded live join the trial. Stream A takes `PL-8HSX` first (P1, a member of `PL-PVW2`), then `PL-Q4DF`, `PL-XBV4`, `PL-PVW2` with `PL-6P0F` as its first slice, and `PL-GPJ7`. `PL-979D` rides Stream B with `PL-HMZZ`'s build. The instructions below carry it, and it takes effect when the owner pastes them into the project.

**`PL-QHCW` moved out of Stream B, decided 2026-09-26** (project owner, 2026-09-26, ratified, over leaving it to Stream B and over building only `PL-VYK1`'s part in their session). The owner named `PL-VYK1`, a `PL-QHCW` member, in a session of their own. The build that closes it is done there, on `claude/focused-davinci-dklbov`, under a claim on `PL-QHCW` and its four members, so a Stream B thread reaching it is turned away at `claim`. Stream B ends with `PL-979D`'s thread. The instructions below carry the change. It takes effect when the owner pastes them into the project or tells the coordinator.

**Setup.** One repository, `stuthedew/open-anesthesia-sim`. Environment: `Default` (the account's only one, created 2026-08-22), chosen explicitly, since threads otherwise start in a generic Anthropic-hosted one. Thread model Opus at high effort; coordinator effort medium, not the Projects default of low, which the effort docs reserve for work that is not intelligence-sensitive: the coordinator's job here is sequencing against the Order list, and one slip costs a whole thread; not high, since Opus 5.5 at medium matches or beats Opus 5 at high on Anthropic's coding and knowledge-work evaluations and the job is rule-following rather than hard reasoning (settings > Usage shows the conversation's share: above about 10-15% with no slips, drop to low; a slip more thought would have caught, raise to high); the three design threads on Fable. The desktop app, for notifications (a browser shows only a dot).

**Project instructions, verbatim** (Project settings > Memory > Project instructions):

```
Goal: retire the four live generator heads in stuthedew/open-anesthesia-sim:
PL-B8HZ (which copy of an item verify --self reads), PL-HMZZ (record the pull
request that carried an item's work), PL-QHCW (record the commit a release was
cut on), PL-MB2W (record who holds an item). Done when `bin/docket generators`
shows none of these four as "still generating". Added 2026-09-25, same test:
PL-Q4DF, PL-XBV4, PL-PVW2, PL-GPJ7, PL-979D. Other new heads are out of scope.

Source of work: only items in docs/items, read through bin/docket. Never start
work the queue does not hold, and never substitute a different deliverable for
the one an item describes: put the case to me and wait. Findings are filed with
`bin/docket new`, not worked here, unless they block a listed item.

Order:
1. Design threads first, one per head: PL-B8HZ (fold in PL-PZ6T, PL-TKFD),
   PL-HMZZ (fold in PL-LPWK), PL-QHCW. Model: Fable. Each writes a marked
   recommendation beside the open question in the item file, changes no
   status, pushes item files only, and stops for my answer. After recording
   my answer in the item, it runs `bin/docket yield`, so its pull request
   can arm.
2. After I answer, at most two code threads at once, each stream strictly
   one at a time, in order.
   Stream A: PL-8HSX, then PL-Q4DF, PL-XBV4, PL-PVW2 (PL-6P0F first) and
   PL-GPJ7, each build then its open members. PL-KR69 and the PL-B8HZ
   build are done.
   Stream B: PL-ZLJ9, the PL-MB2W close-out, the PL-HMZZ build and members
   with PL-979D. PL-FX5Q, PL-J16N, PL-KX73 and PL-1X56 are done, and the
   PL-QHCW build and members moved to an owner session.
   Start the next thread in a stream only after the previous pull request
   merged. An untriaged item is triaged first, in the thread that takes it.

Every thread: follow CLAUDE.md and the docket skill; one item; commit
subjects lead with the id; open the pull request when checks are green; let
`bin/docket arm` decide arming. Never merge on your own. When I send "Merge
it", arm auto-merge and bring main in yourself (docs/maintainer.md).

Claims: claim before opening any pull request. Run `git push -u origin HEAD`
first, then `bin/docket claim`; if it prints "not pushed", run `git push`.
`bin/docket flight` must then show your claim, or stop and tell me.
Never commit to a branch whose pull request has merged: branch again from
origin/main.

Stop and wait for me when: a brief is unclear or needs a decision; main is red
for a reason outside your item; the same check fails twice; you reach the
CLAUDE.md context budget (push first, then report).

Decisions and rules go in item files, never in project memory. Do not create
routines, add repositories, or start threads for anything outside this list.
When a thread finishes, report one line: the item id and what it is, the pull
request number, what you need from me, and any items filed.
```

**Why it matters.** The owner described the cost directly: babysitting one session per small item. The generator sub-goal is about 16 items and was expected to grow to about 25 (`PL-04KR` measured 0.696 captures per item worked). Done one session at a time, that is 20-30 session starts, closing-block reads and merge sequences.

**Done when.** The trial has run to its stop (none of the four heads still generating, or a stop condition fired), and this brief records:

- owner touches per closed item, not counting the one design sitting: the trial failed above 1.5;
- captures filed per item worked: above 1.0, the run grew the queue faster than it drained it;
- any thread left in Waiting on you unseen for more than an hour;
- anything Claude wrote to project memory, and whether it moved into the repository or was deleted;
- the owner's decision whether the protocol becomes a committed docket skill mode, which is a new workflow mechanism and needs the generator pause ended or lifted.

**If it fails either bar, `PL-2866`'s fallback follows** (project owner, 2026-09-25, ratified, over a pick rule that ends in a prompt the owner pastes): build the pick into `bin/docket next`, so that after a product item it offers the top startable root cause and after a root cause a product item, and the digest's top line is then the pick. That is a new workflow mechanism too, so it needs the generator pause ended or lifted, as the decision above does. Heads found in product sessions while the trial runs wait for it, outside its Goal line, until the owner adds them there (`CLAUDE.md` § "A root cause of more than two items is pulled, not queued").
