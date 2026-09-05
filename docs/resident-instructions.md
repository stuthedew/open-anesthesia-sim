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

**Fires before a first write, which no read precedes.** The seven architecture
invariants — simulation code independent of Flet, no calculation in a UI
callback, simulation time as explicit state, deterministic results, tests with
every core behavior change, validated versioned parameter files, no executable
equations in data — plus the milestone bound and the quality suite. Two of them
are *also* enforced by a check (`tools/import_boundary_check.py` confines the
wall clock and the process generator out of `core/`, and holds Pydantic to one
module), and the checks are cited from `CLAUDE.md` rather than replacing it:
the check fails at `make check`, after the code is written, and the invariant
is cheaper to hold before. `import_boundary_check.py` also cites `CLAUDE.md` as
the source of the rule, so deleting the line would strand the citation.

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

## Re-running the measurement

`make check` prints the total in characters over lines, the per-file breakdown
in both, and the change in characters against the default branch on every run;
`python3 tools/doc_check.py check` alone is the same line. Characters are the
unit that decides, because a line count resolves nothing inside an unwrapped
paragraph and the two resident files are not wrapped alike (`PL-QV1F`). Growth raises the routing question at the moment text is added,
which is what `PL-H7XN` built and what this file is the first application of.
`PL-BKQW`'s second advisory catches the shape the total cannot see: text added
and other text trimmed to pay for it, which sums to nothing.
