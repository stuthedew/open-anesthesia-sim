# docket: triage

Read this when folding untriaged captures into the queue, on a grooming pass,
when recording a generator, or when closing an item needs what shows its work.

Part of the `docket` skill. `.claude/skills/docket/SKILL.md` is its front
page and decides which file a session reads.

## Mode: triage

Triggered by the digest reporting untriaged items, or by a grooming pass.

```bash
bin/docket triage
```

That prints each untriaged item's body, the fields still unset, the brief
sections still missing, and the rules the answers must satisfy — read from
`docket.toml` and the checker, so they are what `docket check` will hold you
to rather than what this file remembers. Do not read the store for this, and
do not re-derive the rules from here.

**An item marked `IN FLIGHT` is one a branch already carries — skip it.** A
second answer here is a second resolution of the same file, and the merge keeps
one of them. The mark names the branch, so another session's work is
distinguishable from this one's. It is bounded by what has been pushed, so an
*unmarked* item means "no ref proved it" rather than "no branch has it" — which
is why the output also names the refs it could not read.

**A second and weaker line fires where that mark cannot reach at all.** A
triage pass writes nothing outside `docs/items/`, which is exactly the diff
shape the in-flight mark refuses to read as work — so two passes on one item
were invisible to each other however carefully each one fetched, and on
2026-09-06 the merge discarded one of two identical answers (`PL-N1JK`). `Its
file is already edited on <branch>` is that case: not work in flight, so
`bin/docket next` still offers the item and nobody has claimed it, but a second
answer here is still a second resolution of the same file. Skip it the same
way, and say in the reply which branch you left it to.

**The mark means the edit is genuinely unmerged, so a skip is worth obeying.**
It is checked against the base's own tip, because a squash merge keeps none of
a branch's commits. Read from those commits alone, the mark went on reporting
edits that had already landed. One pass was told to skip four of its five
items, and all four were byte-identical to `origin/main`'s copies (`PL-8MJ3`).

What it still cannot promise is that the ref it names is the *only* one. In that
same pass one of the four was a real collision, answered an hour later on a
different branch than the one the mark named. So read the mark as "somebody may
be in this file" rather than as the identity of who: skipping is still right, and
the branch named is where to look first rather than the whole answer.

**Claim the ids this pass will answer before spending anything on them**
(`PL-JP35`). The marks above show only what has been pushed, and a pass pushes
nothing until it has answers to commit. So two passes started minutes apart
each find the same items unmarked. On 2026-11-03 a session and a Projects
thread triaged the same 17 items within six minutes. Three of the session's
agents used about 620,000 tokens, most of it on items the thread had already
answered. So once you have read the marks, run `bin/docket claim` with every
id you are taking and the `--trailer` lines your commits end with. Do this
before you work on any of them or send an agent. The claim is pushed at once,
and every other session's `bin/docket triage` then marks those ids
`IN FLIGHT`. Where it exits 4, the
claim is only in this checkout, so run the command its message prints. The
claim is all or nothing. Where another branch holds one of the ids first, it
exits 3, names that id and writes nothing. Leave that id to the other branch,
and claim the rest.

**Then read the marks again before every push, for the ids this pass answered**
(`PL-XJ22`). The marks above are read when the pass starts, and a claim made
while it runs reaches `origin` only afterwards, so both answers head for `main`
and the merge keeps whichever arrives first. Two of about nine triage passes
merged between 2026-09-24 and 2026-10-11 met one: #1124 committed its answer for
`PL-QMN0` seven minutes after another branch claimed it and merged first, and
that branch's finished fix closed unmerged; #1278 restored `main`'s copies of
`PL-DHGC` and `PL-W560` only because its session re-read on its own. So run
`bin/docket flight`, which fetches first, immediately before each push - an
item-only branch arms auto-merge at its first push with no open claim, so
nothing later asks. For any
answered id it lists on a branch other than this one, restore `origin/main`'s
copy (`git checkout origin/main -- <path>`), commit that, and name the branch
in the reply as for a skip. `flight` keeps one row per item, a claim ahead of
any status move and the earliest move ahead of later ones, so a second pass
that answered after this one is not in it, nor is a file edited with no status
move; `bin/docket show <id>` prints every branch on one item.

**Last, yield every id the pass leaves open, before the push that arms the
branch.** Dropping or blocking an item ends this branch's claim on it. Leaving
it at `ready` or `needs-decision` does not, and `bin/docket arm` will not arm a
branch while any claim on it is open. So run `bin/docket yield` with those ids
and the same `--trailer` lines. Ending the claim leaves no gap: once pushed,
the status the pass wrote keeps each item marked in flight until the branch
merges. `claim` opened the pull request as a draft, so the push that arms it
also rewrites its title and body and marks it ready, as
`.claude/skills/pull-request/SKILL.md` says.

Fill in what capture deliberately skipped:
`priority`, `effort`, `classes`, `touches`, and `feature` when it belongs
with related work. Safety-critical work starts at `P0` or `P1`; the checker
enforces that. Process work — work on how the project is built rather than on
the product — does not enter the top band when it would outnumber the product
work already there, except an item on the generator tier, which the checker
pins at `P0` or `P1` too and `bin/docket set` raises on its own (`PL-06JJ`).

**An item whose subject is a second copy of a fact the repository already
holds is classed `defect`, and `safety` as well where the safety-critical
standard applies, even while the copies agree.** `CLAUDE.md`'s bullet "A shared
fact has one source of truth" is the stated rule that each copy breaks, so
`refactor` is left for a change of structure that no stated rule requires
(project owner, 2026-10-24, ratified, over classing a copy `refactor` until
the copies disagree, `PL-ZZ03`).

**An item whose work is to search on purpose and file what it finds - an
inventory, an audit, a survey - gets `sweep:`**, written with `bin/docket set
<id> --sweep "what it looks for"`. `bin/docket inflow` then counts the items its
work files apart from ordinary inflow, so a week spent sweeping does not read
as rising inflow or as fixes failing. Without it, `PL-K88Z`'s inventory read as
9 ordinary filings and 5 failed fixes in the week of 2026-10-19 (`PL-CJGH`).

**Write the answers with `bin/docket set`, not into the file.** `bin/docket set
<id> --priority P2 --effort S --classes defect --touches a.py --status ready
--payoff '...'` writes the named fields in canonical order, keeps the file's
name, and refuses a value the item already records (`--overwrite` replaces
one; `status` needs no flag, since moving it is what triage does) and any
write `docket check` would then fail, in the checker's own words. The brief is
prose and stays a hand edit; write it first, because `--status ready` is
refused until the sections it owes exist (`PL-L4YG`).

An item that should not be done becomes `status: dropped` with a `reason` —
`bin/docket set <id> --status dropped --reason "..." --closed DATE`. Never
delete the file: the reason is what stops the finding being re-raised.

**Dropping an item closes it.** `dropped` is one of `CLOSED_STATUSES` beside
`done` in `subprojects/docket/src/docket/model.py`, so a triage pass pushed
onto an open pull request owes that title the dropped id exactly as a close-out
does. Retitle before pushing, per **Mode: close out an item** step 1 in
`.claude/skills/docket/modes/close-out.md` (`PL-X1S4`).

**An item whose next step is a decision is triaged to `needs-decision`, not
answered.** Triage sets fields; it does not resolve the question an item poses.
Answering one means reading the code around it, weighing the alternatives and
recording a conclusion - a work session's shape, spent on one item out of the
queue this pass exists to describe. `needs-decision` is what the store has for
it, and `bin/docket gate` counts it, so the question reaches the owner through
the queue rather than through the reply.

**Except where the decision is a milestone being scoped, which is `blocked-by:
<version>`.** The two look alike and want opposite statuses. A question this
project can answer is `needs-decision`, and `bin/docket gate` counting it as
debt is right - somebody can go and resolve it. A milestone not yet scoped is
`status: blocked` with `blocked-by: v0.6.0`, and is not debt: only a scoping
round resolves it, and working the item cannot bring one forward. `docket
check` advises that it is ready to promote once that section carries its four
subsections - a session promotes it, with `bin/docket set <id> --status ready`
after reading it against the tree - and errors on a version the roadmap names
nowhere. An item blocker is stricter: once every one has closed, `check`
refuses the item left `blocked` (`PL-2349`). `PL-B9PY` is what the wrong one cost -
parked at `needs-decision`, counted into Gate 1 as resolvable, then two days
hidden from `bin/docket next` after v0.5.0 was scoped. A patch track
(`v0.5.x`) is not a version anything can wait on: it freezes no gate and takes
no section, so nothing resolves it.

**Work that waits on the calendar is `blocked-by: <date>`.** A re-measurement
due two weeks after a change, or a reading that needs a full week of data,
cannot start before its day, and its brief saying so is not enough: `PL-R4Y2`
sat at `ready` with its date in prose, and `next` offered it five days early
(`PL-XNF3`). Write the first day the work may start as `YYYY-MM-DD` in
`blocked-by`, and set `status: blocked`. `docket check` refuses `ready` before
that day, and from the day itself advises that the item is ready to promote.

**And `needs-decision` says the next step is a decision, never whose.** That is
the third case, and it is the one taken by mistake, because the status looks
like an invitation - and `bin/docket next` ranked it until `PL-JW39` named it
apart instead. The owner's are the
*consequential* questions - whether a feature enters `ROADMAP.md`, the order
features come in, which of two defensible products this is, anything a learner
would see or the safety-critical standard reaches. `CLAUDE.md` divides it in
one sentence: "The division of labour is theirs to set direction and yours to
make it real."

**Reopening a ratified decision means choosing what it was chosen over.**
`CLAUDE.md` asks every ratified record to name, in one clause, the alternative
it was chosen over, and putting a decision back to the owner means picking one
of those alternatives. An answer that extends the mechanism the decision chose
picks none of them: the same guard at a further write, a further field, a
further site. That answer is a session's call, even though it touches a
ratified decision. `PL-KFNP` is the worked example. Refusing a stale cardiac
output at the write extends the guard `PL-LBQY` chose, and picks neither frozen
compartments nor the accepted window. It was still put to the owner as a
reopening, and the owner asked why it was theirs (`PL-JZV8`).

**Resting on what the project wants does not by itself make a question
theirs** (project owner, 2026-09-19). How a milestone records a fact about
itself, which of two defensible phrasings a section carries, where a note
lands - each turns on what the project wants and is still a session's, because
its consequence is one document's wording. `PL-C4RS` is the worked example: two
ids sat in v0.5.0's `Required scope` under a gate heading saying another track
had cleared them, and "what does `Required scope` mean for work done elsewhere"
was put to the owner as a decision when it was a session's to take. Rule 14 of
`.claude/rules/instruction-writing.md` carries the test in full and is
resident, so it applies here without being read from this file. Where one
specific point genuinely needs them, ask that point rather than handing over
the decision around it.

**Sort by what the answer rests on, not by how hard the item looks.** An item
answerable by reading the code, running a measurement, or applying a rule this
repository already states is a session's, however long it takes to reach:
`PL-74R0` and `PL-79YX` were both settled by measurement against briefs that
expected argument. An item whose answer rests on what the project is for is the
owner's, however obvious the answer seems from inside the session.

**Most such items are both, and the halves are worked differently.** Do the
half that does not depend on the answer, say that is what you did, then put the
direction half in the reply with a recommendation and leave the item open. A
session that closes it on its own reasoning has taken a decision the owner
would have made differently often enough to matter: `PL-8GV5` was closed as
"do not model anaesthesia's effect on cardiac output, and carry no roadmap
line", the measured half of it correct and the disposition not, and the owner's
answer was "not now, and keep it on the roadmap as an option" - which is a
different project, and a better one, because an option can state its own
uncertainty where a default cannot (`PL-4T90`).

**And record the recommendation in the item, not only in the reply.** The
reply is where the recommendation naturally goes, and it is the one carrier
that does not survive: a reply dies with its session while the item waits.
So the longer an item sits at `needs-decision` - which is what the status is
*for* - the likelier the recommendation is gone by the time the owner answers.
`PL-KQHN` is what that costs. Its brief carried a `**Decision needed.**`
naming both answers and marking neither; by the time the owner said "agree
with the recommendation", the recommending session's branch had been deleted
with its pull request, and the only surviving carrier was a harness-written
summary line naming two options and marking neither. A decision of record
about the release train was settled by reconstructing another model's
compressed prose.

Write it into the brief as you write the question, in your own words, and
**mark it** - `**Recommended.**`, `**Recommendation:**`, or the word under
emphasis somewhere a reader skimming will land on it. Marking is the half
that is easy to skip and the half that failed here: a recommendation in the
ninth paragraph of a long brief is present and unfindable, which buys the
owner nothing. `bin/docket check` advises where a `needs-decision` brief
marks neither a recommendation nor a reason there is none.

**Where none is owed, say that and why, in the brief.** Declining is a real
answer - `PL-PFK1` declines because the deciding number cannot be measured
retroactively, and `PL-JW9J` because the answer follows from a count nobody
has taken yet. Both are better records than a brief that simply says nothing,
because silence cannot be told apart from an omission. Marking the
declination also satisfies the check, which is deliberate: the advisory is
asking the brief to be explicit, not to hold an opinion.

**Record an owner's answer underneath the question, and leave the question
standing** - dated, and with its kind: `(project owner, DATE, ratified)` and
what it was chosen over, or the plain form where the owner specified it
(`CLAUDE.md`). `**Answered 2026-09-19 under PL-4Q9B**` is the shape.
Overwriting the question loses what was weighed, and an undated answer cannot
be told from the question it answers (`PL-RWJD`).

**And move the status in the same commit** - to `ready`, `blocked`, or closed.
Every reader of the queue takes the front matter's word, so an answer left
beneath a `needs-decision` front matter is a question `bin/docket next` and
`gate` go on putting to the owner. `PL-4ZK8`'s design round left the move "to
the thread that builds it", and the owner saw it listed as waiting for three
days after answering; 17 items sat that way on `main` before `bin/docket check`
refused it (`PL-JNWS`). Where the answer leaves work, shaping it for `ready` -
the Done-when rewritten in the decided form - is part of recording it. Where a question is still open beneath a
partial answer, pose it below the answer under a `**Decision needed.**`
heading: the check reads only the last question or answer label in the brief.

**Then mark every passage above it that the answer ended.** A paragraph saying
the item is "Left at `needs-decision`", or that it waits on work since closed,
opens with `[superseded YYYY-MM-DD: what replaced it]`, dated for when it
stopped holding. The marker keeps the history and reaches the reader before the
claim does. `bin/docket set` prints the passages its status or `blocked-by`
write leaves standing, and `bin/docket check` reports any still unmarked, so
the repair rides the commit that moved the state (`PL-8YXJ`, `PL-X4RX`).

### Generators, how they rank, and the pause they set

`CLAUDE.md` keeps the two generator rules that apply before any triage. The two
endings apply in the reply that finds a generator. The pause applies before any
workflow mechanism is built. The rules below are the rest: how a generator is
recorded, why it ranks where it does, and the decisions behind both. They moved
here from `CLAUDE.md` on 2026-10-24 without changing a word of the rule
(`PL-6VJ3`).

**A root cause of more than two items is pulled, not queued** (project owner,
2026-09-17). A mechanism a session identifies as the cause of three or more
items is a *generator*. Record it on the causing item as `root-cause-of:`
naming the items it explains — three or more, or it is an ordinary item — so
the claim is a recorded fact rather than the next session's inference.
**The count decides the record; expected recurrence decides the rank**
(project owner, 2026-09-21, ratified, over keeping the count for both and
accepting that any three-item cluster outranks a `safety`-classed `P1`). A
generator the store is still handing new members ranks **above everything but
`P0`** — including a `safety`-classed `P1`, which was asked and answered
rather than overlooked — because every session it stands through pays it
again, and that is a claim about future inflow rather than about the damage
any one member does. One whose mechanism is spent is recorded all the same,
for the audit, and ranks on its own band. Say which it is and why in
`generator:`, beside the `root-cause-of:` — `live - <why it is still being
handed members>`, or `spent - <why it cannot produce another>`. **At close,
the reason names what stops the next member**: `spent - check: <the check>`,
`type:`, `single writer:`, or `none: <why there is none>`. `bin/docket check`
refuses a head closed `done` without one from 2026-11-23, and `bin/docket
generators` marks every closed head that has none, or whose members are still
open (`PL-D8L0`). Recording
alone does not rank; `bin/docket check` asks any open generator that has not
answered. A *ranking* generator then takes one of exactly two
endings: **fix it in this session, or end the reply with a ready-to-paste
prompt that starts a fresh session on it.** Filing it and carrying on is not
a third — an item alone changes nothing. **Found in a product session, it
takes the second, after the product item**, unless it blocks that item
(project owner, 2026-09-25, ratified, over holding the ending for heads found
in product work and over fixing each one here once the item is done,
`PL-2866`). A spent one is ordinary work under `CLAUDE.md`'s capture rule.
Identifying one is judgment and stays a session's; what follows from it is
not.

**Work on a generator's cause runs at `xhigh`, whatever arm the effort trial
drew** (project owner, 2026-11-02: "Always run proximal upstream generator
issues (big picture stuff, figuring out why or designing/implementing the
cause fix) on extra high despite the current trial. The down stream
consequences of the issue can still be in trial."). A cloud session that
starts such work first runs `python3 tools/effort_trial.py move --to xhigh
--reason "generator cause"`. That caps the session at `xhigh` for the rest of
its life, compactions included, and records the move, so the trial's review
leaves the session out of both arms (`PL-6LVZ`). A Projects thread is in
neither arm already. `docs/maintainer.md` § "Match effort to the standard the
work is held to" says the level it runs at. Work on the generator's downstream
items stays in the trial.

**A defect in the machinery that finds and ranks generators ranks with one**
(project owner, 2026-09-19). Same tier, below `P0` and above every band,
because while identification is broken a generator is never recorded and an
unrecorded generator is ranked by nothing — and nothing in the store would
ever say one went unfound. Record it as `impairs-generators:` on an item
whose `touches` reaches `generator_paths`: prose naming the function that
broke, never `yes`, and `bin/docket check` refuses a claim on code the item
never goes near. **The two endings above bind it too** — fix it in this
session, or end the reply with a prompt starting a fresh one; filing it and
carrying on is not a third. Asked and answered against the recommendation to
confine them to a measured cluster, so reopening it needs a compelling
argument rather than ordinary evidence (`PL-4MPJ`).

**While any open workflow-lane item carries `generator: live`, no new workflow
mechanism is built** (project owner, 2026-09-22, ratified, over adding them
under standing approval and ratified recommendations while six closed generator
heads were still producing, which is how at least nine mechanisms and their
tails arrived on 09-20 and 09-21, `PL-KVDK`; narrowed to the workflow lane - a
head whose `touches` lie in `workflow_paths`, the lane `Item.lane` reads - by
the project owner, 2026-10-17, ratified, over binding on a head of either lane,
after `PL-X7D5`, a run-view defect, froze `PL-ZYHX`, `PL-KBVW`). **It holds
apparatus work unrelated to fixing the generators: new features and
housekeeping** (project owner, 2026-09-23). A new command, check, field or rule
of that kind, or a re-specification of the generator rule, is captured and not
built, nor offered as the answer to a finding. Work on the generators is what
the pause is for, and needs no lift: fixing a live generator, a defect in what
exists, or the machinery that finds and ranks generators, including what a head
records (`PL-5MYR`). The pause ends when no open workflow-lane item carries
`generator: live` — no head in that lane that `bin/docket generators` marks
"still generating". Not `next`'s generator tier, which leaves out whatever is
in flight, blocked or untriaged, and counts `impairs-generators:` items the
rule does not name (`PL-CT07`). A request from the project owner lifts it for
that request, and the session says so (`PL-6Q9L`).

### Ask every item touching the apparatus, and every product defect, where it came from

**Each item touching the apparatus is scrutinized for an unresolved generator
or a cause the code does not recognize** (project owner, 2026-09-22). The
apparatus is largely built, so its inflow should be falling, and an item that
arrives anyway is evidence of why. **Touching the apparatus means a `touches`
path under `workflow_paths`, whatever the item's lane** (project owner,
2026-09-28, ratified, over keying the check on the workflow lane, `PL-4NZ7`):
a capture reaching both halves is `crossing`, and keyed on the lane it was
never asked, so a generator reached through one was queued rather than found.

**Product work is asked too, unless it is classed only as new work.** The
project owner asked on 2026-10-27 for the generator checks to reach product
code. The key below is a session's choice that the owner has not yet ratified,
so ordinary evidence reopens it (`PL-K5CX`). That means a product path on an item whose
`classes` are not all in `new_work_classes`, which are `feature` and
`planning`. An item with no classes is asked. Product features keep arriving,
so a feature is not evidence of a cause. A product defect is, and before this
rule each product generator was found only by a sweep the owner asked for
(`PL-R4Y2`). `Item.generator_question_paths` holds the rule for both halves.
The brief of `PL-K5CX` has the measurement behind the key: keyed on
`debt_classes` instead, 6 of the 75 product members of product heads would
not have been asked.

`bin/docket triage` marks each item that `Owes a Generator check`, and says
where it cannot tell yet: capture often leaves `touches` unset, and such an
item owes the check if any path you declare is under `workflow_paths` in
`docket.toml`, or is a product path on work that is not new work. `bin/docket
set` says so at the write that declares those paths or ends triage, where the
brief carries no answer yet, since that write takes the item off the list the
mark prints on (`PL-6WPD`). Keep asking *why did
this exist?* until the answer is a design
fact rather than the symptom: a representation choice, a missing single source
of truth, an invariant no code enforces, an external behaviour nothing models,
or a rule that forces the work.

**Then name the fact this item's reader misread, and read it against every
head's.** The fact is the thing that, held once as a record every reader
consults, would have made the item impossible. `bin/docket generators
--misread` prints each head's `misread:` line on one screen, sorted by the fact,
followed by the heads whose clusters overlap. Compare at the fact, not at the
reader: a second reader misreading a fact a head already states belongs to that
head, even where it shares no function, file or tool with the head's members.
"Two items in two tools with no shared function, so not a generator" is the
altitude that gave one record a head per reader, four of them for who holds an
item before `PL-MB2W` named it (`PL-5MYR`). Then grep for whether any one
function or check already encodes that fact. Land on one of these:

- **An instance of a head's fact, filed after the head closed.** The head's
  `misread:` states the fact, and `bin/docket generators` gives the head's
  close date. The head's fix did not stop the mechanism, and nothing else in
  the store can record that: a head's `root-cause-of:` names only the members
  filed while it was open (`PL-04KR`).
- **A re-entry**: the same defect, or the same mechanism at a sibling site, as
  an item closed within 30 days whose fix should have covered it.
- **One fact misread by two or more other items, and no head's `misread:`
  states it.** That is a generator. Record it as § "Generators, how they rank,
  and the pause they set" says, above, which also sets its two endings, and
  write its `misread:` beside the `root-cause-of:` and the
  `generator:`. `bin/docket check` refuses a head without one. The band
  follows on its own: a `set` recording `generator: live` on a head below `P1`
  raises it to `P1`, so leave `--priority` off that write, since a band below
  `P1` named there is refused rather than replaced. Three post-close
  instances of one head count the same way, as a generator whose fix did not
  hold.
- **A one-off, bookkeeping, or work the owner asked for.** This is the common
  answer, not a failure to find anything.

Sharing a file or a feature is not sharing a mechanism, so prefer the one-off
over a weak cluster. Sharing a misread fact is sharing one, across any number
of readers. Write the answer into the brief as one `**Generator check.**` line,
naming the fact, and the head or the item where there is one. The reply is gone
before a later session looks for it. **Where the answer is either of the first
two, also record it as a field**: `bin/docket set <id> --reenters PL-XXXX`,
naming the closed head or item whose fix should have covered this one.
`bin/docket inflow` counts that field per period and names any closed item
three filings re-enter - the three post-close instances above - and it reads
nothing from the prose line (`PL-WXKD`). It counts the three per fact: a
filing that names any head of a fact counts against the first head that stated
it, so name whichever head you found (`PL-YSV3`). `bin/docket inflow --lane product`
does the same for product filings (`PL-K5CX`). It leaves out a named item whose
`pr:` is the filing's `filed-pr:`, the pull request that `bin/docket new`
recorded as adding it. That filing was found while the fix was being built,
before it shipped, so it cannot show the fix failed (`PL-C47M`). Where `new`
could not ask the forge, record the number with `bin/docket set <id>
--filed-pr N`.

**On a grooming pass, compare the heads with each other** (`PL-5MYR`). The
check above asks one item about the heads. Nothing else asks the heads about
each other, and that gap gave one record a head per reader: four for who holds
an item, and three for gate dispositions before `PL-WD5Z`. Each was found only
by a sweep the owner asked for. So read `bin/docket generators --misread` once,
whole, and ask whether any two lines state one fact. The sort puts lines with
the same wording side by side, and counts the heads under a fact that has more
than one. Drifted wording puts them apart and splits that count, so read the
whole list rather than neighbours only, and give two heads of one fact the same
words. Treat each overlap pair it prints as a
lead, not a verdict: a member two heads share is a misattribution, a member
with two causes, or a sign the heads share a fact. Four outcomes, all yours to
act on in the pass:

- **Two heads state one fact, and no head names it at family altitude.** The
  fact is a generator. Record it as above.
- **Two heads state one fact that a family head already names.** Rewrite each
  narrower head's `misread:` in the family head's words, so the lines sort
  together.
- **A shared member belongs to one head only.** Remove it from the other
  head's `root-cause-of:`, and say why in that head's brief.
- **Nothing.** Say so in the pass's reply; it is the common answer.

The judgment stays yours. What changed is the cost of reading: `PL-T7Y1` ran
this comparison once by reading every brief, with 262 agents, and the list
makes it one screen.

**On a grooming pass, sweep what fired for obvious fluff** (project owner,
2026-10-01, `PL-562K`). Nothing measures whether a check still earns its place:
`PL-ZBJ0`'s counter was dropped on the build gate, and every retirement so far
was found by a session that happened to be working beside the check
(`PL-G6J5`, `PL-Z909`). So the pass does the cheap half by hand, bounded so it
stays cheap. Read one `make check` run and `bin/docket check`'s advisories -
output the pass already has - and ask of each line that fired without failing
anything the retirement clause's question (`CLAUDE.md` § "Prefer deterministic
tooling over repeated model work"): what decision was it built to change, and
where is that decision taken? Taken somewhere the line does not reach: file an
item to route it there. No such decision: file an item to retire it, with the
count `.claude/rules/expert-review.md` § "Name the number that would change
your mind" asks for. Do not open the check list for what did not fire: a
silent check may be a guard doing its job, and that question is asked when a
session meets the check, not here. "Nothing" is the common answer, and the
reply says so. Each outcome is an item rather than a fix-now edit, because
keeping a check is a defensible choice.

**On a grooming pass, regroup the features** (project owner, 2026-11-22,
ratified, over regrouping only when someone notices, `PL-LRWK`). Run `bin/docket feature --similar` and read its four lists. For
each pair of features that read alike, open both groups' items and merge them
where they are one goal. First replace the folded name's line in
`docs/features.toml` with `old = { use = "new" }`, and widen the kept name's
line to cover what it takes in. Then retag every item with `bin/docket set ID
--feature NEW --overwrite`. The order matters, because `bin/docket set` refuses
a retag that would leave a listed name with no item. Give an open item with no feature the one it
reads like where that feature's description covers it. Name a new feature for
two or more open items that share a goal and a path. Fold an open feature
holding one item into its nearest neighbour, or take the feature off. The
lists are ranked guesses, right about seven times in ten in the top three, so
"none of these" is a common and correct answer. Record each merge taken in
the pass's item.

**On a grooming pass, re-test the dead-ends list** (project owner, 2026-10-19,
ratified, `PL-5J1S`). Read `python3 tools/dead_ends.py emit` and ask two
questions of each entry. First, would a session propose this approach before
opening any file? If it would only propose it while editing one part of the
tree, move the entry into a path-scoped rule whose `paths:` cover that part,
as `.claude/rules/dead-ends-apparatus.md` does for the item store and the
tools. Second, does the entry refuse only the approach it names? Reword one
that would also refuse a sound neighbour. An entry whose question no longer
exists, for example because its code was removed, goes under § "Retired" at the
end of `docs/dead-ends.md` with the reason. Age alone is never a reason to
move one. No check refuses a removal with neither record, so write the move
down whichever you choose. "Nothing" is the common answer, and the reply says
so.

### What shows an item is done, and when it is recorded

An item set to `ready` names no command. Its `**Done when.**` section says in
words what will be true, closely enough that a later session can tell whether
it is. For a code change, name the behaviour a test will show: "a test shows
that the run refuses a step of 0 s".

**Reproduce the fault before the item is set to `ready`.** Run the one command
that shows the defect itself, and write what it showed into the brief with its
date. Measured 2026-09-19 across all 166 open workflow-lane items, five rested
on a premise that was already false when they were filed: `PL-RZPX` asked for
a report that had shipped in docket's first commit the day before, and
`PL-T86P` said an item carried no `**Decision needed.**` section when it had
one from creation. One `grep` would have caught each. The step costs one
command per triaged item for about one catch in thirty-three. The alternative
is the sweep that found them, which read 145,000 tokens of briefs across
twelve agents (`PL-JB3Z`, project owner, 2026-09-19, ratified, over leaving it
to a periodic sweep). Capture is untouched: this is triage's obligation, and
the capture rule stays unconditional.

**An item records what shows its work when it closes, and the record is read
once, on the branch that closes it** (project owner, 2026-11-20, ratified,
over changing the form for code items only, and over keeping a command that
`make check` ran again on every later branch; `PL-LFJZ` has the counts). What
the item records depends on its work:

| The item's work | What it records when it closes |
| --- | --- |
| Code | The tests the branch added or changed, in `tests:` |
| A document, or a deletion | One search for fixed text, in `verify:` |
| A question, a count or a decision whose result is in its own brief | A dated paragraph in the brief |
| A release (`resource: release-train`) | The command it already carries |

1. **Code.** Close the item with the pytest node ids of the tests that show
   the work: `bin/docket set PL-K7QX --status done --closed 2026-11-21 --tests
   tests/unit/test_run.py::test_refuses_a_zero_step`. `--tests` repeats or
   takes a comma-separated list. Each entry names a whole test, as
   `file.py::test_name` or `file.py::TestClass::test_name`. `bin/docket set`
   and `bin/docket check` refuse an entry whose file the tree does not hold,
   whose test the file does not define, or whose test the branch neither
   added nor changed, since that test passed before the work. For simulator
   code, the close-out audit's mutation check then shows that the branch's
   tests detect a change to each line the branch changed (`PL-CZXN`).
2. **A document, or a deletion.** Keep one search: `grep -qF 'a few words the
   work adds' docs/MODEL.md`, or `! grep -qF 'the words the work removes'
   docs/WORKING_NOTES.md src/anesthesia_sim/app/chart.py`. docket reads the
   words and the files itself and runs no shell. It compares them with each
   run of spaces and line breaks treated as one space, so a phrase that wraps
   over two lines is found. A path may glob, so `docs/items/PL-K7QX-*.md`
   names an item file by its id. A search for words that the work adds to a
   Python file is refused, because a test shows that work. In a developer
   document, a sentence that restates a fact of the tree is written as the
   requirement and then the test that checks it (`PL-WKKH`).
   <!-- absent: docs/items/PL-K7QX-*.md -->
3. **A result in the item's own brief.** An item that asks a question, takes
   a count or records a decision needs nothing in its front matter. Its brief
   holds a paragraph that opens with a bold label carrying the date, such as
   `**Answered 2026-11-21.**` or `**Counted 2026-11-21.**`, and states the
   result.
4. **A release.** A release item keeps the command it has.

Where none of these can show the work, say why in `not-delegable:`.

**An open item that still carries a command written before 2026-11-21 replaces
it when it closes.** Where the command names a test, record the test and
remove the command: `--tests tests/unit/test_run.py::test_refuses_a_zero_step
--verify ''`. Where it searches a document for fixed text, it is already in
the form above once it reads `grep -qF`.

**Nothing reads the record after its branch merges.** A test that is renamed
or removed later is not a fault in the item that named it. Of 1,060 closed
items whose command named a test, 109 named one that was later renamed or
removed (`PL-LFJZ`). So a closed item's `tests:` and `verify:` say what showed
the work on a tree that no longer exists, and they are not rewritten.
`docket check` refuses a change to a closed item's command, and a command
added to an item that closed without one. Where an item is not done, reopen
it, and the fields are writable again.

### What the reply says, and what it must not

**Triage is a queue pass, not a work session, and its reply is a summary rather
than a to-do list** (project owner, 2026-09-04). Two things, then it stops:

1. **What was triaged** - each item by id and glossed title, the fields it
   landed on, one line of why. A dropped item says what its `reason` was; one
   left `needs-decision` says what the open question is.
2. **Where the queue stands as a result** - `bin/docket status`, at feature
   altitude, which is the altitude that makes a queue legible. Counts are not a
   summary on their own; say what shape they describe.

**Nothing else.** No ranking of what to work on, no release offer, no "and
while I was in there". `bin/docket next` answers "what next" in the session that
asks it, and this is not that session. Rule 14 of
`.claude/rules/instruction-writing.md` is met here by its own escape clause -
when nothing genuinely needs the owner, say so in one line rather than inventing
items to fill the block. On a normal pass that is the expected ending, not a
failure to find anything.

**Do not work the finding.** Committing and pushing the triage edits is routine,
not something to recommend. What must not happen is the pass becoming the fix: a
branch opened for an item it just triaged, a design question resolved, a pull
request shepherded through review. The pull is strongest where the finding is
most interesting, and interesting is not the test.

**Escalate only a `P0`, a compounding-friction finding or a ranking
generator.** A finding compounds when it meets any of the four tests in the
`CLAUDE.md` bullet "Friction that compounds is recommended the moment it is
found, not filed". A ranking generator is a head recorded `generator: live`,
or an item recorded `impairs-generators:`. `CLAUDE.md` gives it two endings:
fix it in this session, or end the reply with a ready-to-paste prompt for a
fresh one. A triage pass is not the fix, so it takes the prompt (`PL-9KGT`).
Name each escalated finding in a sentence or two
and hand over the means to act on it *elsewhere* - `bin/docket next` where the
queue already holds the work, or the exact line to paste into a fresh session,
per **Mode: recommend what to work on** in
`.claude/skills/docket/modes/picking.md`. Not a diagnosis, not a patch, not
a branch. A pass where nothing pressing surfaced ends without this section;
reaching for something because the reply feels thin is how the summary turns
back into a to-do list.
