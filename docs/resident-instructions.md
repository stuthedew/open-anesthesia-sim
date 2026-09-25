# What loads before a session has read anything, and why

Two files reach every session at launch, before a prompt has been read and
before any tool has run: `CLAUDE.md`, and `.claude/rules/instruction-writing.md`,
which carries no `paths:` frontmatter and so loads unconditionally. Claude Code
documents both facts — "Rules without a `paths` field are loaded unconditionally
and apply to all files", and "target under 200 lines per CLAUDE.md file. Longer
files consume more context and reduce adherence"
([memory](https://code.claude.com/docs/en/memory)).

That is the cost. This file is the ledger of what was done about it: which
resident text was routed to a cheaper carrier, which stayed and on what
argument, and which reductions were considered and refused. It exists so the
question stops being re-opened from scratch — `PL-JQY5` was filed against the
same number and dropped as a duplicate the same day, and the pass it asked for
was never run.

## The standard this applies, which is not readability

The test is **adherence**, not prose quality. Nobody reads these files for
pleasure; the question is whether each rule fires at the moment a session needs
it, at the lowest resident cost. Wordiness is therefore a symptom and never the
defect, and the fix is *routing* — moving a rule to the cheapest carrier that
still delivers it — rather than rewriting. `PL-XXBD` and `PL-3VKZ` hold the
prose-quality standard, deliberately apart from this one.

`CLAUDE.md` § "A behavior change takes effect in the session that asks for it"
holds the four dispositions, cheapest first: a check or script; a skill; a
path-scoped rule; resident. The question each is answered against is *at what
moment does a session need this rule, and what is the cheapest thing that
delivers it then.*

One constraint decides most of the hard cases. A path-scoped rule "triggers
when Claude reads files matching the pattern, not on every tool use"
([memory](https://code.claude.com/docs/en/memory)) — so it cannot carry a rule
that must fire before a first write, or before any file is opened at all. Most
of what is resident here is of exactly that shape: it governs how a session
receives a request, decides an approach, or writes a reply, none of which is
preceded by a read.

## What was routed out

| Rule | Was | Is now | Why it moved |
| --- | --- | --- | --- |
| Never prune remote-tracking refs | 10 resident lines | `.claude/hooks/no-prune-guard.sh`, a `PreToolUse` deny on `Bash` | A prohibition on a command string is decidable by reading the command. The prose fired when a session remembered it; the hook fires always, and its deny message carries the recipe the caller actually wanted. It guards agent sessions and not a human at a terminal, which is the scope the prose had too. |
| How to restart a merged branch | inside that bullet | the `docket` skill's `stranded` section, and the hook's deny message | Needed at branch recovery, which is where the skill already is, and at the refusal, which is where the question is being asked. |
| "A push demand after a merged branch may be false" | inside that bullet | `.claude/hooks/stop_hook_patch.py`'s `UNPATCHED` message | Already routed by `PL-WW08`; the resident sentence was a second copy. The message prints at the one moment a session meets a false demand. |
| The doc-sweep procedure | 11 resident lines | the `docket` skill, Mode: close out | Fires at close-out, which `CLAUDE.md` already requires the skill for. The *trigger* stays resident in one sentence, with its safety reason, because without the reason a session reads the sweep as tidiness and skips it under pressure. |
| A prompt naming a lane is `docket next workflow`, run first | 334 characters, § "Session and tool-use efficiency" | `subprojects/docket/src/docket/cli.py`'s lane line, covered by `subprojects/docket/tests/test_cli.py` | The command now prints the fact the rule existed to supply — which lane its own answer is in, and the other lane's pick with the literal command beside it. It is silent only when the caller already named a lane, or when no `workflow_paths` boundary is declared; this project declares one, so it always fires here. What it costs: the print corrects a session *after* a bare run rather than before it, which is one extra command instead of a wrong item started, and that was the whole of `PL-0D4X`'s harm. The rule and that history stay in the `docket` skill (`PL-4H01`). |
| Prefer finishing a feature to advancing several | 159 characters, § "The queue" | `subprojects/docket/src/docket/plan.py`'s `rank()`, which prints the rule beside every ranked item | The ranking implements it and states it verbatim — "A shipped feature beats progress on several, so the feature nearest done ranks first." The clause it does not carry is "do not override it toward novelty", a prohibition on the session that no ranking can enforce; but the printed rationale puts the counter-argument at the moment of the override, which the resident sentence did not. This was the one bullet in that section this file had never tested (`PL-4H01`). |
| "Restarting a branch that carries nothing of its own is a reset rather than a merge" | a clause of the base-merge bullet, § "The queue" | `bin/docket branch`'s restart line, from `format_branch_state` in `subprojects/docket/src/docket/render.py`, pinned by `test_the_branch_state_line_prints_the_command_for_each_state` in `subprojects/docket/tests/test_vcs.py` | Dropped when `PL-6MW8` rewrote the bullet for strict up-to-date checks. The rewritten rule is about open pull requests, and a branch with nothing of its own has none. `bin/docket branch` prints the restart command at the moment it applies, which was confirmed by running its test before the clause was removed. The fuller restart recipe was routed out earlier, in this table's row on how to restart a merged branch. |
| "Run pytest, Ruff, and the configured type checker before finishing" | 70 characters, § "Architecture and development discipline" | nothing — it stays resident, once | A de-duplication rather than a routing. Twenty-seven lines below, equally resident, § "Session and tool-use efficiency" states the same rule more precisely: it names `mypy` rather than "the configured type checker", and adds when to run it in full and what to use while iterating. Nothing was in the deleted line that is not in the surviving one (`PL-4H01`). |
| Which claim shapes hold a captures-only pull request unarmed, and the five decisions behind them | 1,095 characters of `CLAUDE.md`'s commit-and-push bullet, from "A claim on the branch leaves it unarmed" to "merge half the work" | `bin/docket arm`, from `subprojects/docket/src/docket/arming.py`, whose docstring now carries the decision records, pinned by the `test_arm_` tests in `subprojects/docket/tests/test_cli.py` | A claim is a recorded fact since `PL-3FYK`, so whether one rides a branch is read from the tree instead of recognized by each session from a catalog of shapes - and each shape the catalog missed had been an item (`PL-QP9Z`, `PL-1MCK`, `PL-KWCY`). What stays resident, at 520 characters, is the trigger - ask before arming and before every later push - and what each answer does to the pull request, because a push is preceded by no read. The same pass rewrote three sentences, in the housekeeping and naming bullets and in rule 14, that described every in-flight guard as matching commit subjects, which the claim record ends (`PL-MB2W` § "Deleted"); net across both files, 709 fewer characters (`PL-DDYD`). |

Net: 548 resident lines to 541, and 39613 characters to 38845. Both units are
here because they answer different questions and `PL-QV1F` made characters the
one the tool reports: lines are what the documented 200-line target is written
in, and characters are what actually moved — `CLAUDE.md` −1006 against
`.claude/rules/instruction-writing.md` +238.

The 238 that came back are the two conclusions this pass had to record where
the question gets asked: the pointer to this file in `CLAUDE.md`'s preamble,
and the settled answer at the top of `.claude/rules/instruction-writing.md`.
Both are conclusions rather than arguments. The arguments are here, where
nothing loads them at launch.

## What stays resident, and on what argument

Grouped by the argument, because the arguments repeat and the blocks do not.

**Fires on receiving a request, before anything is read.** `Working with the
project owner` in full — the outcome-is-the-requirement rule, the stop-and-wait
rule, the three cases for a proposed implementation, and the scope limits on
all of it. There is no read, no tool call and no skill between the prompt
arriving and the session deciding how to answer it; nothing but resident text
reaches that moment. The same argument covers `What this project is`, which
sets the horizon every one of those judgments is made against.

The session-length cap in § "Session and tool-use efficiency" was added on
2026-09-16 on the project owner's decision, and is resident for this group's
reason rather than its own: a session decides whether to keep going while it is
working, and no read precedes that. The four dispositions were put to the owner
as real options — a `SessionStart` budget line, a periodic `get_session`
self-check, a low `/autocompact`, or the habit alone — and the habit was chosen,
so what is resident is the rule and there is no mechanism to route it to. It
carries its own measurement (2.5–5.6% of a 263k–519k context) because the
alternative is every later session re-deriving the trim proposal this pass
refuted; a rule that does not carry its refutation gets re-opened, which is the
cost `docs/resident-instructions.md` exists to stop paying (`PL-H253`).

It was reshaped on 2026-09-16, same number and a different moment: the budget
is read *before starting an item* rather than on reaching the cap, and an
overrun externalizes before handing off (`PL-NW76`, owner-approved). That
sharpens this group's argument rather than changing it — the moment is now a
session deciding whether to *begin* the next item, which no read precedes
either, and it is the moment at which the rule can still act without loss. The
stopping form could not: overshoot was bounded by the gap between natural
breaks rather than by the cap, and `PL-H253`'s own author read 176,689 before
looking. Still no mechanism, so there is still nothing to route it to.

The gate-scope bullet in that section was added on 2026-09-16 for the same
reason and against a measured asymmetry. The stop-and-wait rule is stated once,
bolded, at line 66; the cases that release it are stated four times — a note
rather than a gate (line 96), decomposition (line 246), filing an item (line
254), opening the pull request (line 343) — across 250 lines, none of them
emphasised, each buried in a bullet about something else, plus rule 14's three
dispositions in the other resident file. Claude Code's own documentation names
the consequence: "if two rules contradict each other, Claude may pick one
arbitrarily" ([memory](https://code.claude.com/docs/en/memory)). The project
owner reported the predicted failure — decisions offered that `CLAUDE.md`
already settles. The bullet restates no rule; it names where each release
lives, at the one place a session is guaranteed to read them together. It is
resident because the moment it governs is a request arriving, which this
group's argument already covers, and it costs 683 characters against a hazard
that was costing a decision per session (`PL-5D2R`).

That section's closing paragraph — the apparatus is not judged by its share of
the queue — was added on the same argument and for a measured reason
(`PL-9J2W`). `apparatus` appeared in `CLAUDE.md` three times and every one was a
warning: "at permanent risk of becoming the work instead", "a lower and
different bar", "where the two compete for a session, the simulator wins"; and
`.claude/rules/apparatus-standard.md` adds that polishing it "is the most common
way this project wastes a session". The one sentence arguing for investment is
scoped to the simulator by its own words. So a session that reached the ratio
had three warnings and no counterweight, reliably concluded the project was
overinvesting in tooling, and the project owner supplied the missing half by
hand — every time, and never in writing. It is resident rather than routed
because the judgment happens while a reply is being composed, with no read
before it, which is this group's argument exactly. What was written is the
*test* rather than a defence: the specific objection still lands, and only the
general one is foreclosed.

**Fires on writing a reply.** `.claude/rules/instruction-writing.md`, all of
it, and this is the file the item asked hardest about. Rule 14's closing block
alone is 88 of its 140 lines and applies to every reply of any kind; rules 1–9
apply whenever a reply contains a procedure the reader will execute. A reply is
not preceded by a read, so `paths:` frontmatter would defer the file past the
moment it governs. A skill would not help either: a skill is invoked when the
model judges it relevant, which is the same recognition act the rules already
require, with a load failure added. **It is resident by necessity, and the file
now says so at the top.** Do not re-open this without a new mechanism to point
at.

Rule 14 grew 199 characters on 2026-09-19, on the project owner's own
statement of the division of labour: "I'll say what feature order I want or if
we need to change big picture stuff, but granular stuff, unless it's
incredibly consequential, I don't care to comment on". It sits in rule 14
rather than in a skill because the moment it governs is the closing block
itself - a session choosing between deciding a question and handing it over,
which happens as the reply is written and after any skill has done its work.
The `docket` skill's triage section carried the wrong test and was corrected
to point here rather than to restate it, which is the routing rule's answer to
one rule wanted in two places. `PL-HGN6` carries the finding, and `PL-C4RS` is
the instance that produced it.

**Fires when the approach is being decided.** `.claude/rules/expert-review.md`
— the domains this project's review reaches across and the design principles
that follow from them. The constraint above names three moments: receiving a
request, *deciding an approach*, and writing a reply. This section had a group
for the first and the third and none for the second, which is the moment this
file governs, so the routing pass had nowhere to put it and left it
path-scoped. A design round is a reply — the owner describes a feature, the
session proposes an approach — and no read need precede it; scoped to `src/**`,
`docs/**` and `tests/**` it arrived only when a session happened to open an
item file, which `docs/**` matches by accident. The project owner asked for it
directly (2026-09-05): the expert standard applies in a design round, "equally
if not more critical", because that is where the approach is still free to
change. Refused as the cheaper alternative: leaving it scoped and adding a
resident directive to go and read it, which fails the same way a skill does for
`instruction-writing.md` above — it is the same recognition act, with a load
failure added. Its code-and-provenance half stayed path-scoped in
`.claude/rules/sources-and-docstrings.md`, because the Gas Man rule and the
docstring obligations both fire with a file already open. Cost: +4721
characters, the largest single addition this file records (`PL-WWDT`).

*Extended 2026-09-16, +1420 characters (`PL-GDB0`, project owner).* § "Say
what would falsify it, then record the instance rather than the rule": before
writing a rule into `ROADMAP.md` or `docs/MODEL.md`, name what would make the
sentence stop being true, and where the answer is already on the roadmap,
record an instance with its condition rather than a rule. Three instances in
one session bought it, each caught by the owner and none by any gate.

*Extended 2026-09-21, +2348 characters (`PL-0GMC`, the durable-versus-cheap
trade, project owner).* § "Count what undoing it would cost, before taking the
cheaper route": where two routes reach one end state and one of them will have
to be redone, name what would have to change to switch later and count what is
already downstream of the choice, then take the cheap route only when that
count is small. The owner's five-year form of the test — *which option will we
be glad we implemented in five years?* — is carried as the tie-breaker for
where the count genuinely cannot be taken, not as the opening move.

**Nothing was cut to pay for it, and the reason is the carrier rather than the
rule.** This is not a new obligation entering the set. It is one the project
owner has been supplying by hand, in chat, whenever a session reached a fork,
and their own report is that it works every time they do — which is the carrier
failure exactly: it reaches the design rounds they are present for and no
others. Nothing resident was doing that job, so there is nothing superseded to
retire here. Two candidates were looked at and both fail the rewrite test in
§ "When a resident rule is retired": `CLAUDE.md`'s "Challenge assumptions when
warranted" is about inertia rather than cost asymmetry, and its
irreversible-architectural-problems clause is a *ranking* where this is a
*trigger* — the new section is what lets a session recognize one, so cutting it
would remove the thing being triggered.

**Why it is a forcing question and not a statement of the philosophy.** A value
("do it right once") can be agreed with and not applied, which is how a
resident rule rots without anyone noticing. A count cannot: either a number was
produced or it was not, and the reply shows which. It is also symmetric, which
is the property that stops it being quoted as licence to over-build — a
mechanism with nothing downstream fails it — and that keeps it from colliding
with `.claude/rules/apparatus-standard.md`, which argues the other way on the
apparatus paths.

**What should retire it.** The decidable sliver is presence rather than
judgment: 74 of the 345 open items carry an `**Approach**` or `**Decision
needed**` section (measured 2026-09-21, excluding `done` and `dropped`), and a
check could refuse one that enumerates two or more routes and records no count
of what is downstream. Not built, on `CLAUDE.md` § "Prefer deterministic
tooling over repeated model work": it would fire on all 74 at once without
changing a decision, which is the defect that section retires a check for.
Build it once the store holds a run of items written under this rule to
calibrate the shape against, and this block goes when it does.

**Path-scoping was measured against this rather than waved off, and it loses
on one moment.** Two rules already scope `docs/MODEL.md` — `citing-sources.md`
and `sources-and-docstrings.md` — and nothing scopes `ROADMAP.md`, so the
cheap version was a fourth path-scoped file over both. It would have fired: all
three instances opened the file before writing it. What it would not have
caught is that two of the three were *stated in a reply first* — floating
recorded as refused, and the strip recommended — and reached the project owner
before any file was opened. That is the deciding-an-approach moment this whole
file governs, which is why the rule sits beside the count-first discipline it is
the sibling of rather than in a rule of its own. The alternative refused with
it: widening `citing-sources.md` to `ROADMAP.md`, which would drag a
source-routing document into every roadmap edit.

*Corrected 2026-09-07, +450 characters, no routing change (`PL-X19T`).* The
paragraph carrying the Gas Man rule into a reply said a reference
implementation is *never* the authority for a constant, which the shipped
parameter set contradicts: most of what this project stores adopts one, on
decisions recorded in the data files. The absolute could not simply be
deleted — the case it names, a reply answering "where did this constant come
from?" with "Gas Man", is exactly right and is the reason the paragraph is
resident at all — so what replaced it states the true rule and points at the
one document that decides it, which takes more words than a false absolute
did. No block arrived or left, and the routing argument above is untouched.

**Fires before a first write, which no read precedes.** The seven architecture
invariants — simulation code independent of the UI toolkit, no calculation in a
UI callback, simulation time as explicit state, deterministic results, tests
with every core behavior change, validated versioned parameter files, no
executable equations in data — plus the milestone bound and the quality suite.
Three of them are *also* enforced by a check (`tools/import_boundary_check.py`
confines the UI toolkit and the numerics arriving with it out of `core/`, and
both Flet distributions out of `src/` entirely; the wall clock and the process
generator out of `core/`; and Pydantic to one module), and the checks are cited
from `CLAUDE.md` rather than replacing it: the check fails at `make check`,
after the code is written, and the invariant is cheaper to hold before.
`import_boundary_check.py` also cites `CLAUDE.md` as the source of the rule, so
deleting the line would strand the citation.

*Corrected 2026-09-16, +10 characters, no routing change (`PL-Y88W`).* The
first of the seven invariants read "independent of Flet" until `PL-3SQT` took
both Flet distributions out of `pyproject.toml`, the port being complete. The
name had outlived the rule twice over. `import_boundary_check.py` cites
`CLAUDE.md` as this rule's authority for holding `PySide6`, `pyqtgraph` and
`numpy` out of `core/` (`PL-9KDK`) while restating it in three of its own
comments as "independent of the UI toolkit" — so the cited source stood
narrower than the boundary built on it. And the count in this block said *two*
invariants had a check behind them when that boundary had already made it
three, which mattered more than the wording: this file is what § "When a
resident rule is retired" reads to decide whether a rule still has a carrier,
so the undercount was an error in the instrument rather than in the prose.
Both are corrected above. The invariant is now named by what it is rather than
by the toolkit of the day, which is `PL-YVM1`'s rule for version numbers one
category over, and is the wording the enforcing tool had already chosen. No
block arrived or left.

**Fires before the session would have any reason to load the `docket` skill.**
The two working modes, capture, housekeeping-filed-first, capture-intent-by-
readiness, the id in the commit subject, commit-and-push-as-you-go, and the
compounding-friction test. Each of these is acted on *before* a queue workflow
is recognized as one — and the ideation mode's whole content is that capture
must cost nothing, which loading a skill would contradict. The `docket` skill's
own preamble records the same boundary from the other side.

**Fires when a session decides where a new rule goes.** The behavior-change
rule and its four dispositions. This is the routing test itself; it has to be
resident or the routing question is never asked. Path-scoping it to `CLAUDE.md`
would fire only after the session had already chosen this file as the
destination, which is the decision it exists to inform.

**Fires when a session decides to solve something by hand.** `Prefer
deterministic tooling over repeated model work`. Scoping this to `tools/**`
would deliver it only to sessions already writing a tool — precisely the ones
that do not need it. The sessions it is for are the ones that never opened
`tools/`.

**Required unconditionally.** The safety-critical clinical-output standard, and
the two-standards paragraph that keeps `.claude/rules/apparatus-standard.md`
away from `src/`. `PL-6SBB` is what the second one costs when it is scoped
wrongly: a session quoted the apparatus bar as the standard for `src/`,
correctly, from a sentence whose scope was three sentences away.

## Reductions considered and refused

- **A ceiling on `check_resident_instructions`.** Refused in the code itself,
  and the refusal is right: a limit is met by deleting a rule to reach a
  number, which is the one outcome this pass must not produce, and no number
  the tool could hold would know which rules a session must see before it reads
  anything. `MATERIAL_RESIDENT_DELTA` is not that and does not reopen it: it is
  a *floor* below which the advisories stay silent, so a typo fix is not asked
  to justify itself (`PL-QV1F`). A floor withholds a demand; a ceiling would
  create one.
- **Compressing the precedence paragraph in `CLAUDE.md` § "Working with the
  project owner", which restates `.claude/rules/instruction-writing.md`'s own
  PRECEDENCE block.** About 10 lines are recoverable and both files are always
  resident together, so the duplication is real. Kept anyway: the rule is a
  *precedence* rule, whose entire failure mode is a session resolving a
  conflict the wrong way, and stating it only in the subordinate document is
  the weaker arrangement. Reversible in one edit if the project owner would
  rather have the lines.
- **Path-scoping the architecture invariants to `src/**` and `tests/**`.** In
  practice it would fire — almost every session touching the simulator reads a
  matching file first. "Almost" is the objection: these are safety-architecture
  invariants, and a trigger that usually fires is the wrong trade for eight
  lines.
- **A check that fails when a resident block has no row in this file.** It is
  decidable, and it would keep this ledger honest. Refused because it would key
  on bold-lead prose, which gets reworded often enough that the check would
  fire without changing a decision — the defect `CLAUDE.md` § "A check earns its
  place every run" names. The pointer in the growth advisory does the same job
  at the same moment for no upkeep.

## When a resident rule is retired

`CLAUDE.md` § "Prefer deterministic tooling over repeated model work" gives
*checks* a retirement test — "A check earns its place every run, or it is
retired" — on the ground that one firing every run without changing a decision
costs attention forever. Resident *rules* had no equivalent. What they had was
the protection in § "The queue" ("never delete a rule for being wordy") and the
ceiling refused below, so the set could only grow: 35721 characters to 44697 in
the five days to 2026-09-05, against a routing pass that found 563 characters to
move. `PL-NJTZ` is the counterweight, and this is the test it points at.

**A resident rule is retired when its failure mode is now caught
deterministically** — by a check, a hook, or a command that prints the rule at
the moment it fires. Not when it is long, not when it is old, and not to reach a
number. Wordiness is still never a reason; obsolescence is.

Three things this deliberately does not become:

- **Not a ceiling.** The refusal below stands unchanged and is not reopened by
  this section: "a limit is met by deleting a rule to reach a number, which is
  the one outcome this pass must not produce." A qualitative test names the
  carrier that replaced the rule; a numeric one names only the shortfall.
- **Not a licence to rewrite.** A rule whose *evidence* has gone stale while its
  other triggers have no carrier stays put. The `list_sessions` bullet in
  `.claude/rules/instruction-writing.md` is the worked example: `PL-66FP`'s
  release case is now hard-refused in `release.py`, but a tag, a merge and a
  branch deletion still meet no check, and cutting only the dead clause would be
  rewriting rather than routing. It was measured at 1287 characters, the largest
  single candidate anywhere, and left resident (`PL-4H01`).
- **Not silent.** A retirement is recorded in "What was routed out" above with
  what now enforces the rule, exactly as an addition is recorded in "What stays
  resident". The ledger is the audit trail in both directions or it is not an
  audit trail: a later session must be able to find where a rule went instead of
  concluding it was dropped.

The carrier has to be observed firing, not assumed. Each of the three routings
recorded above names a file and a test, and each was run against the tree before
the rule was removed.

## What is not a carrier, and why the list stays at four

`CLAUDE.md`'s dispositions are for a **rule** — text that binds a session
whether or not anyone remembers to supply it. Two things this repository uses
look like carriers and are not, and the list is right to omit them (`PL-JQVB`).

- **A paste-able brief** — `docs/consultant-brief.md`. It reaches a session
  only when the project owner pastes it, so a rule routed there binds the
  sessions they happen to paste it into and no others, which is not a rule. Its
  whole design depends on that: `PL-1H3H` chose a pasted user message over a
  skill precisely so that `.claude/rules/instruction-writing.md`'s precedence
  block and `.claude/rules/apparatus-standard.md`'s scoping would *not* reach
  it — a consultant reviewing the apparatus must not load, by opening the thing
  under review, a rule saying that tree is not worth reviewing. A carrier for a
  *pass* rather than for a rule.
- **An agent definition** — a custom subagent. None exists in this tree, and
  `PL-1H3H` records why the one that was considered was refused: a subagent
  returns a summary to a parent and cannot hold a conversation, and a custom
  agent inherits the whole `CLAUDE.md` hierarchy anyway, so the isolation it
  appears to buy is smaller than it looks. Should one ever land, it is a
  *reader* of the rules rather than a carrier of them, and the disposition it
  routes to is still one of the four.

Nothing is lost by the omission: a rule that would have gone to either belongs
in a skill, on a path, or resident, and the list already names those.

## Re-running the measurement

`make check` prints the total in characters over lines, the per-file breakdown
in both, and the change in characters against the default branch on every run;
`python3 tools/doc_check.py check` alone is the same line.

**A second line prints beside it: the instruction text a session can be made to
load** — `.claude/skills/**`, the path-scoped rules, and `docs/worker.md`. It is
reported separately and never summed with the resident total, because a skill
that is never invoked and a rule scoped to `src/**` cost most sessions nothing,
so one figure would overstate every session and describe none. What it closes is
a blind spot rather than a policy gap: between `v0.4.0` and `v0.4.22` this
project's `CLAUDE.md` grew 3,135 characters and `.claude/skills/docket/SKILL.md`
grew 15,416, so the growth advisory reported 16% of the instruction text that
was actually added and a routing pass into the skill read as a pure reduction
(`PL-JQVB`). Routing a rule into a skill remains the preferred answer to the
growth advisory, so the second line raises no advisory of its own — printing
both halves of the move is the whole of what was missing. Characters are the
unit that decides, because a line count resolves nothing inside an unwrapped
paragraph and the two resident files are not wrapped alike (`PL-QV1F`). Growth raises the routing question at the moment text is added,
which is what `PL-H7XN` built and what this file is the first application of.
`PL-BKQW`'s second advisory catches the shape the total cannot see: text added
and other text trimmed to pay for it, which sums to nothing.

**Two more payloads joined the total on 2026-09-21, and the basis changed with
them (`PL-44DG`).** Both reach every session at launch and are resent on every
turn, and neither was counted by anything:

| Payload | Characters, 2026-09-21 | What it is |
| --- | --- | --- |
| SessionStart digest (`.claude/hooks/docket-digest.sh`) | 4,169 | the hook's *output*, measured by running it |
| `docket` skill description frontmatter | 625 | what the skill listing shows before the skill is invoked |

Against a reported 66,773 that is a 7.2% undercount, and the digest is the half
that **grows on its own**: it carries the dead-ends list and scales with the
store, so it is the one component of resident cost that can rise with no edit
to any instruction file — precisely what a size gauge is for. The skill
description is the other end of `PL-JQVB`: routing a rule into a skill moves
its body out of the resident total and leaves its description in, and until
now neither half of that was visible.

**So a figure printed before that date and one printed after are not
comparable.** The series in `CLAUDE.md` § "A behavior change takes effect in
the session that asks for it" — 8,903 at inception, 49,991 on 2026-09-13,
60,199 on 2026-09-19 — is the instruction files alone. `doc_check` still
reports that quantity, as `ResidentInstructions.comparable_total`, and it is
what the growth advisory compares; the printed total is now that plus the
runtime payload. Read a jump across this date as a change of basis, not as
growth.

The digest is deliberately left out of every comparison. `git show <ref>:<path>`
returns a hook's source and never its output, so there is no baseline for it:
compared, it would read as growth of its whole size once and then forever. It
is counted in the total, which is true, and excluded from the delta, which
keeps the advisory meaning what it says. Where the hook will not run, the
measurement declines and says so rather than reporting a total short by four
thousand characters in silence.

## Rule 14's refresh bullet, added 2026-09-19

**The carrier test.** No check can read a reply, so disposition 1 cannot hold
this; a skill loads at its own trigger and a closing block is written in every
reply, so disposition 2 cannot; and a reply is not preceded by a read, which
rules out a `paths:` scope. Resident is the only disposition left, which is the
same argument the rest of this file's rules stand on.

**Why the existing bullet was not enough.** "Re-verify every carried-over item"
already sat beneath it and had been followed by *recalling* rather than by
refreshing. The project owner's words were that the block "is always out of
date", and the sitting that produced the rule is the evidence: a pull request
merged, its branch was deleted, the base moved twice and a third session pushed
a branch re-adding a file this session had renamed - all inside one turn, none
of it visible without a fetch.

**What it costs and what should retire it.** About 500 characters. It names
three commands because no one command answers the question, and `PL-CM40` is
the item that would collapse it to one - at which point this block shrinks
rather than growing. `PL-QSGX` removes the sharpest edge separately:
`bin/docket flight` does not fetch where its siblings do, so the rule currently
has to say so out loud.

## The attribution sentence, added 2026-09-24

`CLAUDE.md` § "Name the work after the item" now ends with the line every commit
a Claude session makes carries: `Co-authored-by: Claude <noreply@anthropic.com>` and never a
model-named co-author, with a `Claude-Session:` line allowed to stay. It
restates the project owner's 2026-09-16 decision in `PL-B11M`, which until then
was written only in item briefs: `PL-B11M`'s, and the two that quote it,
`PL-LWMS` and `PL-SL16`. No file a session reads before
committing stated it, and 800 of the 970 branch commits of the pull requests
merged from 2026-09-17 to 2026-09-24 carried a model-named co-author
(`PL-SL16`).

**The carrier test.** A commit is written before a session would think to look
anything up, and no read precedes it, so no `paths:` scope reaches it. The
`docket` skill reaches the claim commit, but its claim step asks for "each
attribution line your commits must end with" without naming one, and a line
placed there would bind only once the skill had loaded. Disposition 1 is
`PL-LWMS`, a check on the trailers a pull request's commits carry, and it is
held twice: it is a new check under the generator pause, and it is to be built
only if this sentence does not hold.

**What decides it is the instruction it has to beat.** The harness sends each
session an attribution reminder naming a model-named `Co-Authored-By` line, and the
reminder states that
"the user's own instructions about these lines, such as a CLAUDE.md or memory
rule, take precedence over this reminder". A `CLAUDE.md` sentence is the carrier
that clause names. The sentence also says why it wins, because `PL-SL16` found
the reminder winning where nothing said so: `PL-LWMS`'s session passed the
model-named line to `bin/docket claim --trailer`, and only the claim's refusal
of a blocked item kept it off a commit.

**Why nothing is cut.** Nothing resident stated the decision, so nothing is
superseded: before this edit, neither `co-author` nor `attribution` appeared in
any of the four resident instruction files. Nothing else pays for it either.
`tools/doc_check.py`'s growth advisory refuses trimming other resident text to
offset an addition, and names text the project owner asked for as an answer
already given; this is that text, asked for on 2026-09-24.

**What it costs and what should retire it.** 344 characters. It retires only if
a model-named co-author is refused at the moment a commit is written. `PL-LWMS`
as briefed reads the pull request's commits in `pr-title`, after the push, so
it would stand behind the sentence rather than replace it, as the checks behind
the architecture invariants do above: GitHub keeps a pull request's branch
commits after the squash, so a model-named line caught there costs a rewrite of
the branch. Whether the sentence holds is measured rather than assumed.
`PL-LWMS` re-runs `PL-SL16`'s census over the first 30 pull requests merged
from branches cut after the sentence reached `main` - a session keeps the
`CLAUDE.md` it launched with, so an older branch cannot test it - and that
count decides whether the check is built.
