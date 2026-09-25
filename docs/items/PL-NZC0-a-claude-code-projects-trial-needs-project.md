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

**Stress test, 2026-09-25 (PL-P0FP): two lines for the instructions, and four riders for Stream B.** *Recommendation:* before the Project is created, add to the "Every thread" paragraph:

```
Claims: claim before opening any pull request. Run `git push -u origin HEAD`
first, then `bin/docket claim`; if it prints "not pushed", run `git push`.
`bin/docket flight` must then show your claim, or stop and tell me.
Never commit to a branch whose pull request has merged: branch again from
origin/main.
```

Why. `claim` exited 0 without pushing in PL-P0FP's own session (PL-1X56), and in simulation, with that session's real branch settings, it refused outright until the branch was pushed (PL-KX73). The trial's backstop, recorded claims, holds only for a pushed claim. A design thread pushes item files only. A claimed item-files-only pull request opens as a draft; one whose claim is not visible is armed by `bin/docket arm`. After such a pull request merges, `branch` and `arm` advise committing to the merged branch (PL-8BR0), and an answer recorded there never reaches main. That chain is inferred from the simulation's findings, not run end to end.

Add to Stream B, one thread each:
- PL-KR69 after PL-J16N: the same git rename-detection trap, in `verify.py` rather than `vcs.py`.
- PL-KX73, PL-1X56 and PL-ZLJ9 before the PL-MB2W close-out: defects in the claim record it built.

These touch the files Stream B changes, so a separate session would collide with it. They reach main with PL-P0FP's captures, which have to land before Stream B gets to them.

**Setup.** One repository, `stuthedew/open-anesthesia-sim`. Environment: `Default` (the account's only one, created 2026-08-22), chosen explicitly, since threads otherwise start in a generic Anthropic-hosted one. Thread model Opus at high effort; coordinator effort low; the three design threads on Fable. The desktop app, for notifications (a browser shows only a dot).

**Project instructions, verbatim** (Project settings > Memory > Project instructions):

```
Goal: retire the four live generator heads in stuthedew/open-anesthesia-sim:
PL-B8HZ (which copy of an item verify --self reads), PL-HMZZ (record the pull
request that carried an item's work), PL-QHCW (record the commit a release was
cut on), PL-MB2W (record who holds an item). Done when `bin/docket generators`
shows none of these four as "still generating". New heads are out of scope.

Source of work: only items in docs/items, read through bin/docket. Never start
work the queue does not hold, and never substitute a different deliverable for
the one an item describes: put the case to me and wait. Findings are filed with
`bin/docket new`, not worked here, unless they block a listed item.

Order:
1. Design threads first, one per head: PL-B8HZ (fold in PL-PZ6T, PL-TKFD),
   PL-HMZZ (fold in PL-LPWK), PL-QHCW. Model: Fable. Each writes a marked
   recommendation beside the open question in the item file, changes no
   status, pushes item files only, and stops for my answer.
2. After I answer, at most two code threads at once.
   Stream A: the PL-B8HZ build, then its open members.
   Stream B, strictly one at a time, in order: PL-FX5Q, PL-J16N, the PL-MB2W
   close-out, the PL-HMZZ build and members, the PL-QHCW build and members.
   Start the next thread in a stream only after the previous pull request merged.

Every thread: follow CLAUDE.md and the docket skill; one item; `bin/docket
claim`; commit subjects lead with the id; open the pull request when checks
are green; let `bin/docket arm` decide arming. Never merge on your own. When I
send "Merge it", arm auto-merge and bring main in yourself (docs/maintainer.md).

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
