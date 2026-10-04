---
id: PL-PDVF
title: Rules the owner sets for sessions in the Projects trial's instructions reach no repository file, so a session outside the Project follows an older rule and a Project thread reads two that disagree: PL-8XQS, PL-F23S and the arm rule for read holds
priority: P1
effort: M
status: done
classes: defect, infra
feature: owner-rules-in-repo
touches: docs/maintainer.md, CLAUDE.md, .claude/skills/docket, .claude/rules/instruction-writing.md, docs/interface-provenance.md, docs/resident-instructions.md, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21) and not safety or science; the Projects trial began on 2026-09-25, so the problem was not present at the freeze, and nothing on the frozen list names it
added: 2026-10-03
closed: 2026-10-03
pr: 1320
payoff: a rule the owner gives in the Project reaches every session from one record, so no session follows a rule he has replaced and no thread chooses between two
verify: grep -qF '## Rules for sessions live in the repository' docs/maintainer.md
root-cause-of: PL-8XQS, PL-F23S, PL-KKHD
generator: spent - docs/maintainer.md § 'Rules for sessions live in the repository' routes every later rule into the repository in the sitting it is given, and the cut-down instructions say so themselves; a new member needs a rule given after 2026-10-03 and the paste not yet made
misread: The owner's current rules for sessions, as the Project's instructions and the repository hold them
---

**Problem.** Rules the owner sets for sessions in the Projects trial's instructions reach no repository file, so a session outside the Project follows an older rule and a Project thread reads two that disagree: PL-8XQS, PL-F23S and the arm rule for read holds

**The mechanism.** The Projects trial (`PL-NZC0`) gave the owner a second place
to set rules for sessions: the Project's instructions, which only the
coordinator and its threads receive and no repository file mirrors. A rule
given there, or written there by the coordinator for him, leaves the
repository's copy missing or older, so a session outside the Project follows
the old one and a Project thread receives both. `CLAUDE.md`'s "A behavior
change takes effect in the session that asks for it" binds the session that was
asked, and when that is the coordinator, the edit it makes is to the
instructions, or a section posted for the owner to paste.

**Members**, one fact read from two records:

- `PL-8XQS` (closed 2026-10-01): a review ask's plain-language summary was a
  "Review asks" rule in the instructions only. Its own check: "the request
  reached the Project's instructions and not the repository."
- `PL-F23S` (closed 2026-10-03): the instructions' Releases rule carried the
  owner's new wording for re-running `tag-release.yml`, while the release
  skill and `bin/docket release` still handed that step to him.
- `PL-KKHD` (2026-10-03): the arm rule for read holds.

`PL-NXRJ` met the same split from the other side for three days: the
instructions had asked for a direct squash merge since 2026-09-27, and the
repository's hook refused it from 2026-09-30.

**Why it matters.** Each such rule costs the owner twice. A session outside the
Project acts on the old rule (`PL-F23S` handed him a step he had already made a
session's), and a Project thread has to choose between two instructions that
each carry his authority. No check can catch it, since nothing in the
repository can read the Project's instructions.

**Why it is live.** The trial is running, and its instructions are still edited
as the owner gives rules: the arm paragraph cites `#1283` of 2026-10-03, and the
"Combining items" rule (asked 2026-09-30) has no counterpart in the repository
outside item files (`git grep`, 2026-10-03). `PL-NZC0`'s copy of the
instructions, taken 2026-09-25, already reads differently from today's.

**Recommendation: one record, the repository.**

1. Sweep the instructions once. Each rule about how a session works either has
   a repository home already, gets one by `CLAUDE.md`'s routing (a check, a
   skill, a path-scoped rule, then resident), or is the trial's own
   coordination: the Order, thread caps, model choice and where to post.
2. Cut the instructions to that coordination, plus one line: every rule about
   how a session works is the repository's, and where the two disagree the
   thread reports it rather than choosing. The owner pastes the result, since
   no session can edit the instructions.
3. One section in `docs/maintainer.md` for the owner's side: a rule for
   sessions given to the coordinator goes to a thread that writes it into the
   repository, and the instructions name it instead of restating it.

The cheaper route, a dated copy of the instructions in the repository for
sessions outside the Project to read, keeps both records and adds a third, and
`PL-NZC0`'s copy shows how it ends.

**Generator check.** This item is the head. No head's `misread:` in
`bin/docket generators --misread` states this fact (read 2026-10-03), and no
check can hold it, since the Project's instructions sit outside the tree.

**Done when.** Every rule about how a session works that the instructions carry
has a repository home, the instructions carry none of their own, and a
section of `docs/maintainer.md` says where a new one goes.

**Built 2026-10-03**, with `PL-KKHD` in the same pull request. The instructions
as this thread received them on 2026-10-03 were swept once, paragraph by
paragraph, against the repository. Where each rule went:

| Rule in the instructions | Where it lives now |
| --- | --- |
| The arm rule for read holds, in "Every thread" | `arming.READ_PATHS`, printed in every `arm` answer; `CLAUDE.md`'s commit-and-push bullet; `docs/maintainer.md` § "Read a simulator change before you arm it" (`PL-KKHD`) |
| The rest of "Every thread": follow `CLAUDE.md` and the skill, id-led subjects, open the pull request on green, ask `arm` before every push, what `arm`, `behind`, `landed` and `unknown` mean, the direct squash merge on "Merge it" | already `CLAUDE.md` § "The queue, and how the project owner works" and what `arm` prints under each answer (`PL-NXRJ` for the merge); dropped as a restatement |
| Review asks (asked 2026-09-27) | already `arming.READ_ASK`, printed under every hold (`PL-8XQS`); the project-chat half is coordination and stays |
| Claims: `claim` before the first push, exit 3 and 4, `flight` must show it, never commit to a merged branch | already `.claude/skills/docket/modes/start.md` and `CLAUDE.md`; dropped |
| Obvious calls (asked 2026-09-27) | `.claude/rules/instruction-writing.md` rule 14, in the owner's words |
| Design first | `.claude/skills/docket/modes/design.md`, new, with its row in `SKILL.md` and a pointer in `start.md`; the caps stay as coordination |
| Combining items (asked 2026-09-30) | `start.md`, after the rider paragraph |
| An untriaged item is triaged first, in the thread that takes it | `start.md` |
| A design thread on Workspaces, Areas or Views first reads planned-milestone item 34 and the items its own builds on | `modes/design.md`, step 2 |
| The Blender paragraph | `docs/interface-provenance.md` § "What a later design thread owes this study"; the licence rules were already its table under "The prose is the encumbered half" |
| Context: a thread that cannot be compacted | `CLAUDE.md`'s reset bullet |
| Stop and wait: `main` red for a reason outside the item, the same check failing twice | `CLAUDE.md`'s commit-and-push bullet; "a brief is unclear or needs a decision" was already § "Working with the project owner" |
| Releases: the cadence (`PL-LPH9`), no cut while another session holds the release train, the tag re-run (`PL-F23S`) | already `.claude/skills/docket/modes/release.md`; the Definition-of-done check before the cut is written there now, for every milestone's own release |
| Keeping current: `update-armed.yml` | already `CLAUDE.md`'s base-merge bullet; "refresh main" and the line on other projects' pull requests are coordination and stay |
| Source of work: never substitute a deliverable, a generating head is put to the owner with a recommendation | already `CLAUDE.md` § "Working with the project owner" and its generator rule; the Order-specific sentences stay |
| What v0.6.0 needs | `ROADMAP.md` § "v0.6.0 - the layout is the reader's" defines it; one pointer line stays |
| Goal, Report, Order and PAUSED, thread caps and models, where to post and record, Coordinator | the trial's own coordination; kept |

**Calls made in the build**, each said in the reply:

- **The Definition-of-done check is written for every milestone's own release**,
  with v0.6.0 as the instance. The owner asked it for v0.6.0 alone; a rule
  written for one milestone is re-asked at the next, and the roadmap's cadence
  gives every milestone a Definition of done to check against. Put to the
  owner in the review ask, since it widens what he asked.
- **Design first binds every session**, in a Project or not. `PL-NZC0`
  ratified it for the trial on 2026-09-25 and the instructions generalised it
  later, with its kind unrecorded; `modes/design.md` is the skill mode
  `PL-NZC0` § "Stress-test additions" anticipated.
- **Kinds are recorded as the instructions give them.** A rule the
  instructions mark "asked DATE" is written `(project owner, DATE)`; one they
  mark ratified, `(project owner, DATE, ratified, ...)`; one they mark neither
  way, `kind unrecorded`, so a later session reopens it on ordinary evidence
  and says the kind is unrecorded rather than claiming either.
- **The item closes with the paste as the owner's step.** The done-when's "the
  instructions carry none of their own" is his action, since no session can
  edit the instructions; the cut-down text is held here so it survives the
  reply, and goes to `/mnt/project-files/v0.6.0/project-instructions-cut.md`
  once this pull request has merged, as the brief asked.
- **The generator is spent on the paste.** `docs/maintainer.md` § "Rules for
  sessions live in the repository" routes every later rule to the repository
  in the sitting it is given, and the cut-down instructions say so in their
  own second paragraph; until the paste lands, the old text is read beside
  the repository's, and a thread reports a disagreement rather than choosing.

**The cut-down instructions**, as written 2026-10-03 for the owner to paste:

```text
Goal: ship v0.6.0 of stuthedew/open-anesthesia-sim, "the layout is the reader's", as ROADMAP.md scopes it, one feature at a time in the order I pick. Done when `bin/docket wave` reports version 0.6.0 and the v0.6.0 tag is on origin. ROADMAP.md § "v0.6.0 - the layout is the reader's" defines what it needs, and its "Explicitly out of scope for v0.6.0" list stays out; `bin/docket wave` computes where the gate stands, `bin/docket status` and `bin/docket feature NAME` give progress by feature, and `bin/docket show ID` prints an item's brief. Blender is the reference for how Workspaces, Areas and Views behave for the user, and docs/interface-provenance.md is the project's study of it: what was adopted, diverged from and refused, and what a later design thread owes it.

Rules are the repository's. Every rule about how a session works lives in the repository - CLAUDE.md, the docket skill, the rules under .claude/rules/, and what bin/docket prints - and these instructions carry only this project's coordination. Where a rule here and one in the repository disagree, the thread reports both to me rather than choosing. A rule I give here goes to a thread that writes it into the repository in the same sitting, and these instructions then name nothing about it (docs/maintainer.md § "Rules for sessions live in the repository"; PL-PDVF, 2026-10-03).

This is a big project, run over many threads and weeks. Anything a later thread or a replacement coordinator needs goes in its item file or in /mnt/project-files/v0.6.0/, never only in a conversation. Decisions and rules go in item files, never in project memory.

Report. When I ask what v0.6.0 still needs, start one thread that answers from origin/main with those commands and that section. It changes nothing in the repository and opens no pull request. Its reply leads with its recommendation, then says in two or three sentences where v0.6.0 stands. Then a pick list of at most eight lines, each a feature I can name back to you, with what it buys, its open items and their sizes, how many wait on my decision, and its lane (product, workflow, or both): gate work by each item's docket feature, the smaller ones collapsed into one line per lane; build work as the Required-scope entries that can start now and what each unblocks. Then what only I can decide before picking, each with a recommendation. The full breakdown goes in /mnt/project-files/v0.6.0/report.md, attached: every open item glossed, and the order the whole build can run in, from each item's blocked-by. It says where the repository does not answer and what it inferred instead. A later "what's left" you answer yourself from a fresh `bin/docket wave` and `bin/docket status`, never from thread reports alone.

Order: 1. interface-areas design round (picked 2026-09-27): answer every open Workspace, Area and View decision now; no interface-areas code until Gate 2 clears. 2. Gate 3 deferral (agreed 2026-09-27): a new small item writes into ROADMAP.md's v0.6.0 gate section that PL-WZVZ, PL-B396, PL-0S0V, PL-VJZK and PL-KZ99 move to Gate 3, as PL-S5Q9 did for the Gate 1 to Gate 2 move. 3. late-washout-evidence (picked 2026-09-27): the three P1 science gate items on the washout tail, run as a chain. 4. dev-tooling (2026-09-27, coordinator's pick at my request for another category): workflow-lane gate work, run as a chain, with a design thread for its open decisions. 5. presentation-safety (2026-09-27, coordinator's pick at my request for another category): its design thread starts now; its build chain starts when a code-thread place is free. 6. scenario-branching (2026-09-27, coordinator's pick at my request for another category): product-lane gate work, run as a chain when a code-thread place is free. 7. machine-profile-framework (picked 2026-09-27 on the coordinator's card): its product-lane Gate 2 entries, run as a chain now. 8. parallel-sessions (picked 2026-09-27 on the same card): a design thread takes its open decisions now; its workflow-lane chain starts when the v0.5.16 release frees a code-thread place. 9. housekeeping (picked 2026-09-30 20:28Z, done 2026-09-30): the seven cheapest Gate 2 housekeeping entries in /mnt/project-files/v0.6.0/gate-small-items.md (PL-WTXB, PL-245B, PL-J3TV, PL-WHQS, PL-LBW5, PL-RWBV, PL-SYG4), run as one chain, including fresh threads that continue it; then stop again. 10. small gate fixes (picked 2026-10-01 02:54Z, done 2026-10-01): from the same file, the four CI and tooling tweaks (PL-7K2C, PL-CR36, PL-JTHW, PL-NWSK) in one pull request and the three test fixes (PL-624C, PL-JS0X, PL-WPDB) in another, each in its own thread; then stop again. 11. read-facts-through-docket (picked 2026-10-01 19:02Z, done 2026-10-03, last link #1288): its eight items (none a Gate 2 or Required-scope entry), each triaged first, run as one chain including fresh threads that continue it, in the order PL-DHGC with PL-W560, PL-8P31 with PL-M6GY, PL-4NG0, PL-5QG4, PL-PFD9, PL-9L39; chain state in /mnt/project-files/v0.6.0/read-facts-chain.md; then stop again. 12. PL-M26Q (picked 2026-10-03 12:31Z, done 2026-10-03 in #1287): `bin/docket gate` prints a product/workflow lane split, so a report reads each item's lane from docket instead of computing it; then stop again. 13. numerical-domain (picked 2026-10-03 15:08Z as "build chain"; coordinator's pick over stranded-report-fidelity, the other ready group offered; done 2026-10-03, last link #1292): its three ready product-lane Gate 2 entries PL-2MD9 (propagator drift), PL-73ZN and PL-BMY5, run as one chain including fresh threads that continue it; chain state in /mnt/project-files/v0.6.0/numerical-domain-chain.md; then stop again. 14. Gate 2 design round (picked 2026-10-03 19:02Z, on the coordinator's recommendation; done 2026-10-03 in #1296, #1297 and #1298): every Gate 2 entry waiting on my decision (15 at v0.5.21), in three design threads at once on Fable: the product and crossing lane's decisions; pr-body-integrity with the first half of the one-item workflow features in `bin/docket gate` order; the rest of those; then stop again. 15. PL-5291 (picked 2026-10-03 20:31Z, "Agree with recs" in the pause thread): a branch built standing on the 24-hour limit still offers Start; triaged first; then stop again. 16. PL-YBFB (picked 2026-10-03 20:31Z, same answer; done 2026-10-03 in #1309): writes into ROADMAP.md that PL-5B1N moves to Gate 3, as I decided 2026-09-27; then stop again. 17. PL-PDVF (picked 2026-10-03 21:58Z on the coordinator's card, ahead of other workflow work): the generator behind rules of mine that reached these instructions and never the repo (the arm rule in PL-KKHD, review summaries in PL-8XQS, tag re-runs in PL-F23S, and combining items); move each session rule into the repo once, then give me a cut-down version of these instructions (the Order, thread caps and models) to paste in; then stop again. PAUSED (asked 2026-09-27 20:08Z, restated 2026-09-30 20:28Z; reason not recorded at the time, probably to keep the project's threads from spending my weekly usage limit while the workflow work went on in my own sessions, inferred 2026-10-03, record in /mnt/project-files/v0.6.0/pause.md): apart from items 15 and 17, start nothing new, including parallel-sessions' build chain and any thread for PL-TBMX, until I say to resume. When I pick or drop a feature, rewrite this Order section and nothing else to match, say so in one line, and start its first thread as soon as a place is free; if you cannot edit these instructions, post the new Order section for me to paste. If I pick build work while gate entries are open, say once how many are open and that the roadmap clears the gate first, then do what I answer; the thread that starts it records my go-ahead in its item as (project owner, DATE).

Source of work: only items in docs/items, read through bin/docket, and only what the Order picks. Findings are filed with `bin/docket new`, not worked here, unless they block a picked feature; they join the Order only if I add them. A head that `bin/docket generators` shows still generating is put to me at once with a recommendation.

Threads. At most two code threads at once. A design thread takes every open decision in one feature before any code for it: one per feature, at most three at a time, outside the code-thread cap. A picked feature runs as a chain, each pull request starting only after the previous one merged. Two chains that share a file never run at once (`bin/docket concurrent ID`). Before starting any thread, check `bin/docket flight` and start nothing another session already claims, and say which model it runs on. Workspace, Area and View design runs on Fable wherever it needs design: every design thread on them, and any build thread whose item still leaves a user-facing choice open. Fable also for items at needs-decision or classed safety or science, which docket marks "strongest model". Otherwise say it doesn't need Fable, or recommend Fable with the reason. When a thread stops because the same check failed twice, I may ask for the retry on Fable. When a thread stops at its context budget, the coordinator starts a fresh thread on the same branch without asking me.

Where to post. The coordinator posts every review summary in the project chat in full, not a pointer to the thread, and forwards my "Merge it" from there to the thread; nothing merges without it. When your pull request merges, post one short line saying so. When I say "refresh main", each running thread brings origin/main into its own branch. Never update, arm or comment on a pull request this project did not open.

Coordinator: resolve a thread yourself once its pull request merged and nothing is needed from me. Do not create routines, add repositories, or start threads for anything I have not picked. One exception on repositories: the project defaults to the simulator repository alone, so its own settings apply (references repository removed 2026-09-27), and a thread whose work needs the references library may add stuthedew/open-anesthesia-sim-references to its own session. When a thread finishes, report one line: the item id and what it is, the pull request number, what you need from me, and any items filed.
```

