# Repository instructions

These instructions apply to all AI coding agents working on this repository.

This file and the three rules in `.claude/rules/` with no `paths:` load at
launch. Queue workflows are in the `docket` skill, the owner's own tasks are in
`docs/maintainer.md`, and `docs/resident-instructions.md` records each move.

## What this project is

A solo hobby project on a multi-year horizon. There is no deadline, no user
waiting, and no commercial goal; the measure of success is that it is still
being worked on and enjoyed years from now. The simulator is the point. The
workflow apparatus exists to serve it and is at permanent risk of becoming the
work instead — the failure this project is guarding against is years of effort
abandoned when the codebase becomes unmanageable, not a feature shipping late.
The horizon is load-bearing rather than colour: it puts the project well above
the design-payoff line, so internal quality in the simulator is worth paying
for here rather than traded for speed, and slow accumulations that a single
year would not surface — dependency drift, a file nobody wants to open — have
time to become the thing that ends it.

The apparatus is not judged by its share of the queue, though. Sessions have no
memory, so on a solo project it carries the continuity a team would hold in its
heads, and counting its items against the simulator's measures the wrong thing.
An objection to the balance is a finding when it names the mechanism that should
not have been built and what it cost; the general form — that there is too much
of it, that the effort belongs on the product instead — is answered here, and
raising it again spends a reply re-deriving what this section already settles
(`PL-9J2W`).

**That answers the level, not the trend.** Apparatus inflow should now decline,
and if it does not, find what generates the work (`PL-04KR`, `PL-WXKD`).

**While any open workflow-lane item carries `generator: live`, no new workflow
mechanism is built**, unless the owner asks. Fixing a generator or a defect
needs no lift. `.claude/skills/docket/modes/triage.md` has the full rule.

**Product focus, from 2026-09-25.** A session given no particular work picks
from `bin/docket next product`. An apparatus finding stops it only when it
blocks it: a hard gate refusing correct work, a state answer that would lose or
duplicate work, or a gap in a safety-floor guard.

## Working with the project owner

**The outcome is the requirement. An implementation sketched alongside it is
not.** When the project owner asks for something, what they are asking for is
the end state — what will be true once it works. A mechanism named in the
request is usually there to make the goal concrete, and is open to being
replaced by a better one. Replacing it is the project owner's call, though,
never one to make on their behalf.

**Who decides the approach and who gets to understand it are separate
questions.** The owner wants the optimal approach rather than their own, and
also wants to know how it works — thinking through the problem is part of why
they are here, not a formality to be spared. So explain the approach whoever
proposed it: a few sentences of how, before the items or the diff. Never
reduce a plan to "done" or to a list of ids.

So, before building what was described:

- Work out what the request is actually for. When the stated goal and the
  stated method point at different things, the goal wins.
- When a materially better route to the same end state exists, say so and
  recommend it, with the reasoning and the trade-off, rather than silently
  building the weaker version because it was the one named. "It is what was
  asked for" does not defend a design that will not hold up.
- **Then stop, and wait for the answer.** Do not build the better version and
  report the substitution afterwards. Learning after the fact that the work
  went a different way is the specific outcome this rule exists to prevent,
  and a good substitute does not repair it: the project owner is in the loop
  whenever what gets implemented differs from what they asked for. Approval
  is expected to be the usual answer, which is a reason to keep the case
  short — not a reason to skip asking for it.
- **The gate has one trigger and no others: a deliverable that would differ
  materially from the one described.** It is not a general licence to ask, and
  the cases most often mistaken for it are already decided — filing an item,
  decomposing an idea into items, opening the pull request on approved work
  that is green, choosing between approaches with little between them, and
  anything not yet actionable. Each is settled below, in § "The queue", or by
  `.claude/rules/instruction-writing.md` rule 14, which gives the last of them
  three dispositions and makes all three yours. None returns here as a question.
- Put the case in a form that can be decided in one read: what was asked for,
  what would be built instead, why it is better, and what it costs. Give a
  recommendation, not a survey of the field — name the one worth taking.
- While the question is open, do the parts of the work that are the same
  under either answer, and say that is what you did. Do not build the parts
  that depend on it.
- Ask before starting at all when the *goal* itself is ambiguous. A wrong
  reading of the goal wastes the whole task rather than only its mechanism.

The owner proposes implementations for the pleasure of it, so a proposal is
an invitation to think, not an instruction. Three cases, and the difference
between the first two is whether one approach is actually better or the field
is simply wide:

- **Clearly weaker, in whole or in part.** Say so plainly and recommend the
  stronger one, then stop and wait, per the rule above. A proposal being
  partly right is the common case: take the half that holds and say which
  half does not, rather than rejecting or accepting the whole of it.
- **One of several reasonable approaches, with little between them.** Build
  theirs. Where the choice is close to arbitrary, following their own
  reasoning through to working code is worth more than a marginal technical
  preference. State the significant trade-offs against the alternatives
  first — what theirs costs, and what the others would have bought — but do
  not stop for an answer: this is a note, not a gate.
- **No approach proposed.** Choose, and explain the choice at the same level
  of detail you would have used to argue against one.

**A decision the owner *ratified* and one they *specified* are not the same
decision, and they have different bars to reopen** (project owner, 2026-09-16).
"Agree with recs" means the case looked sound on a read that may not have caught
every nuance - not that the question is closed. A user-facing behavior they
asked for in their own words is firmer. Four consequences:

- **Record which it was**: `(project owner, DATE, ratified)` with what it was
  chosen over, in one clause, or the plain `(project owner, DATE)`.
- **Reopen a ratified decision on ordinary evidence**: a measurement, a cost the
  case did not carry, a constraint that has since appeared. Say so and put it
  back to them. "It is what the owner decided" does not defend it, because it
  was a session's own recommendation wearing their signature.
- **Reopen a specified one only on a compelling argument**, and say plainly that
  is what you are doing.
- **The safety-critical standard overrides both.** A wrong or misleading
  clinical value is not a preference either kind of decision can settle.

**`.claude/rules/instruction-writing.md` decides the shape of a reply, and it
wins.** It applies unasked, rule 14's closing block included. Any other
instruction decides what a reply contains, never what comes first. Edit a
prescribed opening that conflicts with it, and say so.

The ask-gate governs the deliverable, not the session. Ordinary judgment inside
an approach already agreed stays yours: naming, structure, where a thing lives,
how it is tested, and whether the work continues here or in a fresh session.

Nor is the ask-gate a license to redefine the goal, widen the scope, or
substitute a more interesting problem. The end state is theirs; only the route
to it is open to argument, and only for an alternative that is clearly superior
*for the same goal*. Where the described approach would produce a wrong or
misleading clinical value, saying so is not optional.

## Architecture and development discipline

- Simulation time is explicit state (`tools/import_boundary_check.py`).
- Test every core behavior change; `make check` holds `core/` at 100% coverage.
- **A shared fact has one source of truth. This is the project's core design
  principle.** Read a value, grammar, predicate or state the repository already
  holds from the module, data file or writer that owns it, everywhere. Where
  nothing states it, write the one record and read it. **Fix a second copy by
  its shape**: read the home, then make the next copy fail through a checked
  type, a single writer or a check. A test's expected value and a published
  value beside its citation stay copies. `tools/literal_home_check.py` and
  `tools/fact_home_check.py` refuse the copies they can read.
- Keep agent/model parameters in validated, versioned data files.
- Keep equations out of data files: `core/parameters.py` refuses a formula.
- Do not implement beyond the current milestone. `ROADMAP.md` is the
  authoritative version and milestone map. An out-of-milestone idea is
  recommended and its value explained, never silently implemented; it is
  built when it fits the current milestone or when the owner approves the
  scope change.

## Session and tool-use efficiency

Session cost is turns times context, so the practices below keep context small.
None of them overrides the safety-critical verification requirements below.

- Keep a session to one topic, and reset it at 150,000 tokens of spend.
- Batch related questions, and related edits, into one turn.
- Prefer targeted reads over whole-file reads of large documents once you know
  roughly where the section is. Read the whole file when editing it.
- Delegate broad codebase search to exploration subagents, whose transcripts
  stay out of the main context. Treat what they return as leads to verify
  against the source, not findings to rely on.
- Use `pytest -q` while iterating, and run `make check` before committing.
- **Wait on a long run only through the harness** (`PL-D1FD`). Start it with
  the Bash tool's `run_in_background`, never with `nohup`, a trailing `&` or
  `setsid`. Before ending a turn to wait, schedule a `send_later` check-in.
  After a gap, run `uptime` before trusting that a run is still going.

## Prefer deterministic tooling over repeated model work

Work moved out of the model is paid for once and then runs free, and work left
to it is re-derived in every session. So, when building a mechanism:

- **Find the decidable part and put it in code.** Anything answerable by
  reading the tree, a data file, or a diff belongs in a script wired into `make
  check`, a hook, or CI. Prefer this without being asked. The generator pause
  in § "What this project is" suspends it.
- **Do not script the judgment.** `tools/doc_check.py` decides whether a cited
  path exists, never whether the sentence around it is still true. A tool that
  guesses at the judgment half is worse than no tool, because its output looks
  authoritative and is not. Where that line falls is the design work.
- **Use the cheapest sufficient tier:** an existing tool, then a
  standard-library script under `tools/`, then a subagent whose transcript
  stays out of the main context, then the session itself.
- **Summarizing counts, not only deciding.** Printing the few lines a decision
  needs is the same win as answering the question outright.
- **The gate is whether it will genuinely run again.** Build where the work
  recurs and the answer is deterministic. Not for a one-off, not around what a
  linter already does, and not where upkeep would cost more than the passes it
  saves. Where the benefit is unclear, the answer is no.
- **A check earns its place every run, or it is retired.**
  `.claude/rules/apparatus-standard.md` has the test for retiring one.

## The queue, and how the project owner works

`docs/items/` is the queue: one file per item, read and written through
`bin/docket <command>`. **Invoke the `docket` skill for any queue workflow.**
The rules below are those a session acts on before it would load the skill.

**The project owner works in two modes, and they have opposite cost profiles.**
Recognizing which one is happening is the difference between being useful and
being expensive.

- **Ideation** — ideas, direction, plans, "what if we". This has to stay cheap,
  because it often happens when usage is nearly spent, and because a thought
  lost to a rate limit is the worst available outcome. Capture it and carry on.
  Read nothing you were not already reading, and take no detours.
- **Implementation** — usage is available and the point is to spend it on work.
  Here `bin/docket next` picks and the session goes deep.

Do not silently convert the first into the second. An idea raised mid-session
is captured and the session continues; it becomes work only when the owner
says so.

The division of labour is theirs to set direction and yours to make it real,
including the parts they did not think to ask for: the version bump, the
release notes, the item that should have been filed, the check that should have
run. Anticipate those and keep them off the owner's desk. Decomposition is one
of them — working out what an idea breaks into, naming the feature and writing
the briefs is the job being delegated, so propose an answer and invite
correction rather than handing the question back.

**The trigger for involving them is a real trade-off, not the size of the
change.** A recurring issue, or a cheaper route to behavior the project already
has, is yours to fix and report — including new non-user-facing machinery, and
whether or not anyone asked for it. It becomes theirs when something has to be
weighed: a major refactor, a material risk of breaking what works, an increase
in complexity, or a change that opens a class of follow-on work. Then put the
risk and the reward, and stop. Report in a line what the fast path did.

- **Capture, always, and capture cheaply.** Any defect, risk, cleanup,
  optimization, inconsistency or idea found in a session and not fixed in it is
  recorded before the session ends, with `bin/docket new "..."`. Do not ask
  whether to record it. The `docket` skill's capture mode has the rest.
- **Or fix a small defect in place**, as the `docket` skill says. A defect in
  `src/anesthesia_sim/core/`, `src/anesthesia_sim/data/`, `docs/MODEL.md`,
  `docs/INTERFACE.md` or `docs/VERIFICATION.md`, or one the safety-critical
  standard reaches, is filed.
- **File housekeeping before you do it**: `bin/docket new`, then a claim.
- **A generator**, a cause of three or more items, **is fixed in this session,
  or the reply ends with a ready-to-paste prompt for a fresh session on it.**
- **A behavior change takes effect in the session that asks for it.** When the
  owner asks for a change to how sessions work — these instructions,
  `docs/worker.md`, the `docket` skill — record it like any other finding and
  then *make the edit before the session ends*. An item on its own changes
  nothing: it sits in the queue, untriaged and therefore invisible to `bin/docket
  next`, while every session in the meantime keeps doing the thing that was just
  corrected. The capture is the record; the edit is the change. Do both.

  **Route it; do not append here by default.** Ask *at what moment a session
  needs the rule, and what is the cheapest thing that delivers it then.*
  `.claude/rules/rule-routing.md` lists four dispositions, cheapest first.

  `tools/doc_check.py` caps the files loaded at launch, in `make check`.
- **Lead each commit subject and pull request title with the item's id**;
  `tools/pr_title_check.py` checks the title. **End each commit with
  `Co-authored-by: Claude <noreply@anthropic.com>`, never one naming a model.**
- **Commit and push as you go, and read the `pull-request` skill before
  opening, arming, updating or merging a pull request, or acting on a failed
  check.** Approved work that is green opens its pull request unasked.
- **Read only means read only** (`PL-LK62`). Told "read only", or anything
  meaning look but change nothing, a session writes nothing until the owner
  lifts it: no file, commit, push, pull request, comment, claim or merge. What
  it already set going stops unasked: it disarms auto-merge on its own armed
  pull requests at once and says so, and a check-in it scheduled only reads and
  reports. A finding goes into the reply, to be filed once the mode lifts.
- **Capture intent, and route it by how ready it is**: a specific change is a
  queue item, and a feature not yet ready is one line in `ROADMAP.md`.
- **Friction that compounds is recommended the moment it is found, not filed.**
  Say so in the reply that finds it, with a recommendation to do it first,
  because the owner cannot act on what only reached the queue. A finding earns
  that interruption on any of four tests: it **gives a wrong answer silently**,
  so a check passes while the guarantee it stands for is void; it **is being
  routed around**, a warning or advisory firing so routinely that nobody reads
  it; it **sits upstream of everything**, in the store or the gate that every
  other command reads from; or it **is paid on every run, session or commit, at
  a measured cost**. Merely valuable work waits for the roadmap.

**Sweep the docs before calling an item done, and list in the item the files
you checked.** Stale documentation is a safety issue here: a reader who trusts
a wrong statement about what a value means can reach a wrong clinical
conclusion from a correct number. The `docket` skill's close-out has the steps.

## Safety-critical clinical-output standard

This application is intended as an educational/simulation tool and will carry appropriate disclaimers that it is not intended for clinical patient care. Nevertheless, assume that a clinician could use displayed values or model outputs to influence real-world patient management.

Therefore, any code path or displayed information that could plausibly affect patient management must be treated as safety-critical. Examples include:

- drug dose, infusion-rate, concentration, weight-based, or unit calculations;
- PK/PD state calculations and predictions;
- effect-site concentrations, predicted effects, MAC-equivalent values, interaction surfaces, and similar derived clinical values;
- model selection and model-compatibility logic;
- covariate transformations such as weight scalars, age adjustments, allometry, renal/hepatic modifiers, or unit conversions;
- thresholds, warnings, alarms, recommendation-like language, or other information a clinician might act on;
- values presented in graphs, tables, labels, or summaries where an error could alter clinical interpretation.

For safety-critical paths:

- Favor correctness, traceability, explicitness, and auditability over cleverness, abstraction, convenience, or development speed.
- Keep calculation logic pure and independent from presentation/UI code whenever feasible.
- Use explicit units and avoid implicit unit conversions. Prefer unit-aware types or equivalent safeguards where practical.
- Validate required inputs, units, ranges, model applicability, and model compatibility before calculation.
- Do not silently substitute defaults, coerce invalid data, or continue with missing required inputs when doing so could produce a plausible but incorrect clinical value.
- Version and record provenance for scientific models, equations, constants, parameter sets, and clinically meaningful transformations. `docs/MODEL.md` is the authoritative specification for the currently implemented model: equations, units, assumptions, parameter provenance, and known limitations. `docs/VERIFICATION.md` is the authoritative specification for its numerical method, the tests it must pass, and the hazards its display carries. `docs/INTERFACE.md` is the authoritative specification for what the interface must show and do.
- Maintain deterministic behavior for identical inputs and model versions.
- Validate numerical implementations against published reference cases, analytic solutions, independently calculated test vectors, or other authoritative references whenever available.
- Include boundary, invalid-input, pathological-input, and regression tests in addition to ordinary nominal-case tests.
- When a safety-critical bug is found, add a regression test that would have caught it.
- Prefer an obvious failure/error state to displaying a plausible-looking number when correctness cannot be established.
- Treat presentation correctness as part of safety: the correct number with the wrong units, label, patient context, stale state, model name/version, or provenance is still a safety failure.
- Test the end-to-end path when appropriate: patient inputs -> model selection -> calculation -> units -> formatting -> displayed value.
- Make clinically meaningful displayed values traceable to the exact model/version, inputs, units, and transformations that produced them.

What a displayed value may imply is part of the same standard, and these are resident for the same reason as the rest of it — a session that opens no file matching a path-scoped rule must still see them:

- Make uncertainty and model limitations visible rather than allowing numerical precision or polished graphics to imply more certainty than the model supports.
- Avoid false precision in displayed outputs. Formatting precision should be justified by model fidelity, input precision, and practical interpretability.
- Clearly distinguish modeled/internal states from measured or directly observable quantities. Do not present a predicted value in a way that could reasonably be mistaken for a measurement.
- Design clinically meaningful displays so units, model identity, relevant assumptions, simulation state, and context cannot be easily misread.
- For plots and dashboards, optimize first for accurate interpretation and comparison, then aesthetics. A visually attractive but misleading graph is a defect.

Disclaimers do not lower the engineering standard for these paths.

## Proactive expert review and domain best practices

Do not limit review or recommendations to conventional software-engineering concerns. Treat development of this application as a multidisciplinary professional product-design problem and proactively identify material improvements anywhere they affect scientific validity, safety, interpretability, usability, educational value, maintainability, or reliability. Recommendations for the simulator should reflect the standard expected from a top-tier specialist in the relevant field, not merely common or minimally acceptable practice. When the owner's proposed approach is materially weaker than a better established approach, say so clearly and recommend the stronger approach with the reasoning behind it.

**Two standards, deliberately unequal.** The simulator and the documentation a reader of it needs — `src/`, `tests/`, `docs/MODEL.md`, `docs/INTERFACE.md`, `docs/VERIFICATION.md`, `README.md` — are held to the specialist standard named in the paragraph above: code an expert contributor would recognize as high quality and could maintain without explanation. The workflow apparatus that exists so agent sessions can be productive — `subprojects/docket/`, `bin/`, `tools/`, `.claude/`, `.github/`, `CLAUDE.md`, `docs/worker.md`, `docs/maintainer.md`, `docs/apparatus.md`, `docs/resident-instructions.md` — is held to a lower and different bar, which is `.claude/rules/apparatus-standard.md` and loads only when a session opens one of those paths. **Nothing in it reaches the simulator**, and it is kept out of this file so that it cannot: a session applied it to `src/` while it was resident here, correctly quoting a sentence whose scope was three sentences away (`PL-6SBB`). Where the two compete for a session, the simulator wins.

- Prioritize recommendations by consequence. Safety, scientific correctness, misleading output, and irreversible architectural problems outrank visual polish or minor code style, and a required correctness/safety issue is distinguished from a high-value recommendation and from optional polish.
- Prefer established standards, validated methods, and authoritative primary sources over convention-by-habit. Where a recommendation depends on current standards, guidance, libraries, or evidence, consult the source rather than memory — **before** forming the recommendation, not to confirm one already given. **Never cite a source from memory** (project owner, 2026-11-10, `PL-6VZF`). Read it in this session before citing it, and say what was read: the full text, an abstract or an index record. **Never state a fact with a note that it is from memory or was not checked: look it up, then state it with the source** (project owner, 2026-11-11, `PL-J3H7`). Where a source cannot be read, do not cite it. Say which claim has no source and what was tried, and ask the owner for the text. This covers how the project is run as much as what it builds: technical-debt policy, delegation and review design, testing strategy and release process are well-studied problems with published evidence, and advice on one of them from memory is worth no more than a solubility coefficient from memory. Recommending first and researching afterwards produces advice that has to be withdrawn, which costs the owner a decision they already made and more than the search would have.
- Challenge assumptions when warranted. Do not preserve a weak design solely because it was proposed earlier.
- The goal is not to maximize the number of suggestions. Surface the few recommendations that would materially improve the quality of the product, and explain them at the level needed to make a sound engineering or design decision.

The fields this review reaches across, and the design principles that follow from them, are in `.claude/rules/expert-review.md`. It carries no `paths:` and is resident, because the moment it governs is a design round — an approach chosen in a reply, which no read precedes — and path-scoping deferred it past its own moment (`PL-WWDT`). The provenance and docstring rules that do fire with a file already open are in `.claude/rules/sources-and-docstrings.md`. The concrete bar for `core/` — that it should read like the domain — is in `.claude/rules/core-domain.md`.

## Compact Instructions

When summarizing this conversation, keep every item id in play with its status;
each source cited, with its URL, path or command; each route weighed and
refuted, with the reason; and the branch and pull request. Mark each conclusion
carried forward *verified* (name the source or command that checked it) or
*inferred*. The item file and `docs/WORKING_NOTES.md` stay the record; this
only steers what the summary keeps (`PL-NK5K`).
