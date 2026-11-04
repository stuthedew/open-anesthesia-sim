---
id: PL-Q28F
title: owner_ask_guard.py's and arming.py's headers carry decision history (68 and 206 lines) that belongs in the items, so a reader must get past the history to learn what the code does
priority: P3
effort: S
status: done
classes: docs
feature: guard-code-structure
milestone: v0.6.15
touches: subprojects/docket/src/docket/arming.py, .claude/hooks/owner_ask_guard.py
deferred-from: v0.7.0 - captured after the freeze; a workflow-lane code-structure change, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-03
pr: 1996
payoff: a reader of arming.py or owner_ask_guard.py learns what the code does from its header, and finds each decision's history in its item
verify: ! grep -qF 'moved here from `CLAUDE.md` with it' subprojects/docket/src/docket/arming.py && ! grep -qF '**Why the state decides, and the wording only finds the ask.**' .claude/hooks/owner_ask_guard.py
---

**Problem.** owner_ask_guard.py's and arming.py's headers carry decision history (68 and 206 lines) that belongs in the items, so a reader must get past the history to learn what the code does

**Why it matters.** A reader opens `arming.py` to learn what `arm` checks. The
first 207 lines are its docstring, and lines 75 to 201 are a dated list of the
decisions behind each rule: who chose it, what it was chosen over, and the
counts that argued for it. `owner_ask_guard.py` does the same in its paragraphs
on why the state decides, why a hook, and the tool rename. The plain-writing
rule puts decision history in the item, so a reader of the code gets the rule
and a pointer.

**Done when.** `arming.py`'s header keeps the five answers, the precedence
between them, and one line per rule that names the rule and the item holding
its decision. The dated reasoning moves out of the header into this item's
body, under "The decisions arming rests on", word for word, so nothing is
lost. `owner_ask_guard.py`'s header says what the hook checks, which tools it
reads, what it cannot check and how it fails; its history paragraphs move
here the same way. No code changes.

**Generator check.** No generator. Other modules that carry history in their
headers are prose-quality work, one item each.

## The decisions arming rests on

Moved word for word on 2026-11-03 from the header of
`subprojects/docket/src/docket/arming.py`, where they had been since they left
`CLAUDE.md`.

**The decisions the rule rests on**, moved here from `CLAUDE.md` with it:

- a claim holds whichever push carried it (project owner, 2026-09-23,
  ratified, over arming whatever rode the push, `PL-QP9Z`, and over reading
  only a start claim on that push, `PL-1MCK`);
- it holds until the item closes in the branch's own copy and not past it
  (same date, ratified, over holding it past the item's closing, `PL-KWCY`),
  and a block releases it too (2026-09-24, ratified, over holding it until
  closed, `PL-3FYK`) - `claims.RELEASING_STATUSES`;
- a pull request a claim rides is a draft (2026-09-24, ratified, over opening
  none while a claim rides or titling it as the capture, because `#978` was
  merged by hand while its claim was open, `PL-H14W`);
- the tooling arms on green beside the store, and everything else waits on a
  read, this module included (2026-09-25, ratified, over holding every path
  outside the store, `PL-SQTR`, built by `PL-K6B2`): the hold fired on every
  docket change and was clicked through, so it guarded nothing, the simulator
  included. This module stays held so that the gate cannot loosen itself
  (until 2026-10-19, below);
- a body record arms on green beside them (2026-09-25, ratified with the
  record's form, over every pull request holding on the record it writes
  before its merge, `PL-979D`): the record is a copy of the body, never a
  change to read;
- only the owner's read list waits on a read - `src/`, `tests/` outside
  `subprojects/`, `docs/MODEL.md`, `src/anesthesia_sim/data/`, `README.md` and
  this module, until 2026-10-19 - and every other path arms on green, named
  beside the answer, unless the change raises a question for the owner (the
  Projects trial's instructions, 2026-10-03, kind unrecorded, over holding
  every path outside the store, the tooling and the records; built by
  `PL-KKHD`). The rule was written there alone, so on one day `#1298` armed
  under it while `#1308` held under the old one. It reopened `PL-0JGZ`
  (project owner, 2026-09-26, ratified), which kept `ROADMAP.md` and
  `docs/WORKING_NOTES.md` off what arms because the roadmap is where the owner
  sets direction: neither is on the list, so both arm, and the owner settled
  it so (project owner, 2026-10-03, ratified, over holding them as before).
  `.github/workflows/` and `.claude/hooks/` joined the list the same day,
  since they decide merges and tags as this module does (project owner,
  2026-10-03, ratified, over leaving them armed on green; `PL-KKHD` records
  both answers), until the owner's rule of 2026-10-12 below;
- docket's lexer, `docket/shell.py`, joined the list when `PL-JNYL` made it
  the reader every guard hook reads a Bash call through, so that a change to
  what the guards refuse still waited on a read outside `.claude/hooks/`
  (project owner, 2026-10-10, ratified, over arming lexer changes on green;
  `PL-JNYL` records the answer), until the same rule;
- workflow items need no merge confirmation (project owner, 2026-10-12: "don't
  need to ask me for merge confirmation for workflow items"), so
  `.github/workflows/`, `.claude/hooks/` and the lexer left the list and arm
  on green with the rest of the workflow lane, while a product path waits as
  before, in a change crossing both lanes too (`PL-KPM2`). This module stays
  on the list so that the gate still cannot loosen itself: a change to it
  could drop `src/` from the list and merge unread (project owner, 2026-10-12,
  ratified, over arming a change to it on green with the rest of the workflow
  lane; `PL-VKHD` records the answer), until the owner's answer of 2026-10-19
  below;
- a test of the tooling under `tests/` - a file pytest collects that imports
  no `anesthesia_sim` on either side of the change - arms on green, as
  `subprojects/docket/tests/` does, and the rest of `tests/` stays on the list
  (project owner, 2026-10-05, ratified, over keeping every change under
  `tests/` on the read list; built by `PL-552M`). Since 2026-10-03, 16 of the
  51 merges held for a read had been held by such tests alone, every
  `PL-R417` slice among them, so the hold asked for reads with nothing to
  judge, the click-through that retired the hold on the tooling (`PL-SQTR`).
  The import rule is the one `tools/workflow_paths_check.py` holds
  `docket.toml`'s `workflow_paths` to, spelt here and imported there, and it
  is read from the tree rather than from `workflow_paths`, which arms on
  green: widening what arms still takes an edit the gate holds (`PL-0JGZ`);
- a pull request reaches the owner only for a real decision or a high-risk
  change, and housekeeping merges on green (project owner, 2026-10-17: "Model
  comes to me only when there is a real decision as discussed or making a high
  risk change you want a second set of eyes on then you should present the
  case for the change, the risks etc. but house keeping stuff I don't need to
  sign off everything"; built by `PL-DKBG`). The read list had held `#1516`'s
  measured figures and tightened tests exactly as it would a changed equation,
  and its ask invented two points to judge. So the list no longer holds by
  itself: a change to it waits for the session's recorded judgment,
  `Owner-read: needed - <why>` or `not needed - <why>`, which `arm` reads from
  the branch's commits, and only `needed` and this module wait on the owner
  (this module until 2026-10-19, below). Chosen over dropping the list and
  leaving the judgment to prose, which fails open on a session that never
  makes it, and over keeping the list and rewording the ask, which leaves
  housekeeping waiting on the owner.
- a hold for the owner's read carries its ask as an `Owner-ask` record, a
  decision with at least two options and a recommendation or a review,
  and `arm` prints it as the ask's opening line (project owner, 2026-10-18:
  "View chooser thread just told me a generic read pull request without a
  question again" and "it's not supposed to ask for a merge if nothing to
  review"; built by `PL-9JHM`). The ask's shape was prose twice before
  (`PL-9KHK`, `PL-DKBG`), and sessions still sent a bare read. A form for
  "nothing to decide" was weighed and refused, because a pull request with
  nothing to review should not reach the owner at all: the way out of such a
  hold is `Owner-read: not needed`;
- a change to this module holds only when it changes or deletes an existing
  test pinning its answers, and otherwise arms on green with the rest of the
  tooling (project owner, 2026-10-19, ratified, over holding every change to
  it with a review ask and over arming it on green with no such test;
  `PL-9JHM` records the owner's answer). It reopens `PL-VKHD`'s answer of
  2026-10-12, which held every change here so that the gate could not loosen
  itself, because nine of those holds in two weeks were mostly refactors
  with nothing to review. To loosen an existing answer, a change has to edit
  the test that pins it, so that kind of loosening still waits. A loosening
  that no test pins merges unread, and so would one that also rewrote the
  check reading the pins, since this module judges its own change;
- the gate's read covers the existing tests that pin its answers as well as
  this module, and since 2026-10-19 those tests alone (`PL-9JHM`), so a
  loosening through what the answer is read through has to edit one (project
  owner, 2026-10-12, ratified, over holding `vcs.py`, `claims.py`, `cli.py`
  and `test_cli.py` whole, and over leaving it; `PL-WW0Q`). It reopens, for
  that one route, `PL-SQTR`'s line at this module alone;
- a simulator change's new long prose waits for a recorded review: `arm`
  holds while the count that `prose_count_command` gives is above zero, or
  could not be read, and only the prose added since the newest
  `Prose-review` record is counted (2026-10-19, decided in the workflow
  decision round without the owner as the one clearly correct option, over
  relying on a pointer in close-out step 5 and measuring five more branches,
  `PL-W04Z`). Five of six simulator branches had skipped step 8's review, and
  their prose was rated awkward in 58% of verdicts against 22% for the one
  that ran it (`PL-J6CK`). Docket names no repository tool, so the count is a
  configured command, as the forge's are;
- a simulator change waits for its blind generalist review passes: `arm`
  holds while the number `blind_count_command` gives is more than the newest
  `Blind-review` record says ran, or could not be read (2026-10-25, a
  session's call under `PL-HDRN`, over leaving close-out step 9 as prose
  alone). No simulator branch had merged under step 9 yet, so its skip rate
  was not measured. Step 8 was skipped by five branches in six while it was
  prose alone (`PL-W04Z`), and a branch that ran the passes pays one trailer
  line.
  A record is not undone by a later change, because close-out step 9 says a
  fix made for a finding needs no further pass.

## The owner-ask guard's history

Moved word for word on 2026-11-03 from the header of
`.claude/hooks/owner_ask_guard.py`.

refused too. Until `PL-R1HT` the hook accepted any question in the recorded
  form in this state, so a made-up question carried an ask past "send the
  owner nothing". The way past the refusal is to record an `Owner-ask:`
  trailer, or `Owner-read: not needed - <why>` where the change needs no read.

**Why the state decides, and the wording only finds the ask.** From `PL-TLPH`
to `PL-ZCF9` the hook also judged from the wording whether a phrase asked at
all, and let through phrases that were quoted, negated, about a decision card
or put in the future. A review on 2026-11-03 found that 20 of 33 unlisted asks
passed, and that 14 of 18 new phrasings in those four contexts were refused
(`PL-3D2F`). Those context rules are deleted. A message that holds an ask
phrasing in a sentence that asks nothing, such as "no longer needs your read",
is refused, and the refusal says to reword it and record the mistake.

**Why a hook and not more text.** On `#1612` and `#1676` a session read `arm`
through `head`, missed the line saying to send nothing, and sent the owner a
bare "read #N and merge it" (`PL-TLPH`). Text fails whenever it is read short,
so this checks the message itself, at the one moment it goes out.

goes to another session or names a thread. It first listed the tools it read,
`reply`, `update_message` and `ask_decision`. The harness renamed them to
`post_message`, `edit_message` and `request_decision`, so a thread's edits and
decision cards went unchecked and nothing said so. Naming the skipped tools
instead means a renamed or new tool is checked until someone says otherwise.
