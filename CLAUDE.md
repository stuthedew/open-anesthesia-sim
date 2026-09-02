# Repository instructions

These instructions apply to all AI coding agents working on this repository.

Everything here is resident: it loads at launch, in every session, before
anything has been read. It is therefore limited to what a session could get
wrong *before* it would think to look anything up. The rest of the working
agreement is routed to where it fires — `.claude/skills/docket/SKILL.md` for
the queue workflows, `.claude/rules/instruction-writing.md` for the shape of a
reply, `.claude/rules/core-domain.md` and `.claude/rules/expert-review.md` for
the standards that apply to particular parts of the tree, and
`docs/maintainer.md` for what only the project owner can act on. Nothing was
dropped in that routing; adding to it follows the same test, below.

## What this project is

A solo hobby project. There is no deadline, no user waiting, and no
commercial goal; the measure of success is that it is still being worked on
and enjoyed in a year. The simulator is the point. The workflow apparatus
exists to serve it and is at permanent risk of becoming the work instead —
the failure this project is guarding against is a year of effort abandoned
when the codebase becomes unmanageable, not a feature shipping late.

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

**`.claude/rules/instruction-writing.md` decides the shape of a reply, and it
wins.** It loads in every session and applies unasked, so it never needs to be
named in a prompt — including its rule 14, the closing block of what the owner
has to do, which every reply ends with. Where it and another instruction —
this file, a skill, an item's brief — describe the same message differently,
the rules file decides *shape* and the other decides *content*: what the reply
must contain, in what words, with what judgment, is theirs; what comes first is
the rules file's. Being the more specific document does not carry the format
question. A prescribed opening that cannot survive that is edited, not obeyed —
say so and fix it, per the behavior-change rule below. This file states no
reply format of its own, deliberately: two documents specifying one thing is
the hazard that rule exists to remove.

This governs the deliverable, not the session. Ordinary judgment inside an
approach already agreed — naming, structure, where a thing lives, how it is
tested, whether the work continues here or moves to a fresh session — stays
yours. The trigger is a deliverable that would differ materially from the one
described, not every decision taken while building it.

Nor is this license to redefine the goal, widen the scope, or substitute a
more interesting problem. The end state is theirs; only the route to it is
open to argument. The bar for proposing something other than the named
mechanism is that the alternative is clearly superior *for the same goal* —
not that it is the one you would have picked. And the safety-critical
standard below is a floor rather than a preference: where the described
approach would produce a wrong or misleading clinical value, that is not a
mechanism preference to be weighed but a correctness problem, and saying so
is not optional.

## Architecture and development discipline

- Keep scientific/simulation code independent of Flet.
- Put no simulation calculations in UI callbacks.
- Treat simulation time as explicit state, never wall-clock time.
- Preserve deterministic results for identical inputs.
- Add or update tests with every core behavior change.
- Keep agent/model parameters in validated, versioned data files.
- Do not add executable equations to data files.
- Do not implement beyond the current milestone. `ROADMAP.md` is the
  authoritative version and milestone map. An out-of-milestone idea is
  recommended and its value explained, never silently implemented; it is
  built when it fits the current milestone or when the owner approves the
  scope change.
- Run pytest, Ruff, and the configured type checker before finishing.

## Session and tool-use efficiency

Session cost is turns times context, because the whole conversation is resent
every turn. So the practices below work by keeping context small — and none of
them overrides the safety-critical verification requirements below: trimming
applies to routine iteration, never to skipping a check before a commit or
before finishing.

- Keep a session short and scoped to one topic; start a fresh one for an
  unrelated topic rather than continuing or compacting a long one. Pick up cold
  from the session-start digest, `bin/docket next`, and the one item being
  worked — not by reading the queue whole.
- Batch related questions, and related edits, into one turn.
- Prefer targeted reads over whole-file reads of large documents once you know
  roughly where the section is. Read the whole file when editing it.
- Delegate broad codebase search to exploration subagents, whose transcripts
  stay out of the main context. Treat what they return as leads to verify
  against the source, not findings to rely on.
- Edit this file and the core docs in their own session where practical: they
  sit in the cached prefix of every request, so editing one partway through
  invalidates that cache for the rest of the session.
- Batch edits before rerunning the full quality suite (`ruff format`, `ruff
  check`, `mypy`, `pytest`) rather than rerunning all four after each one. Run
  it in full before finishing or committing; use `pytest -q` while iterating,
  and `--cov` only when coverage is the question.

Which model a session runs is the owner's lever rather than a session's, so it
lives in `docs/maintainer.md` along with the settings that support it.

## Prefer deterministic tooling over repeated model work

The section above keeps one session cheap; this one keeps every later session
cheap, and is the higher-leverage of the two. Work moved out of the model is
paid for once and then runs free; work left to the model is re-derived at full
context in every session that needs it. `tools/doc_check.py` and
`subprojects/docket/` are the worked examples. So, when building a mechanism:

- **Find the decidable part and put it in code.** Anything answerable by
  reading the tree, a data file, or a diff belongs in a script wired into `make
  check`, a hook, or CI. Prefer this without being asked — it is standing
  approval, needing no case put for it each time.
- **Do not script the judgment.** `tools/doc_check.py` decides whether a cited
  path exists, never whether the sentence around it is still true. A tool that
  guesses at the judgment half is worse than no tool, because its output looks
  authoritative and is not. Where that line falls is the design work.
- **Use the cheapest sufficient tier:** an existing tool, then a
  standard-library script under `tools/`, then a subagent whose transcript
  stays out of the main context, then the session itself — the last by a wide
  margin the most expensive.
- **Summarizing counts, not only deciding.** Printing the few lines a decision
  needs, instead of loading the documents that hold them, is the same win as
  answering the question outright.
- **The gate is whether it will genuinely run again.** Build where the work
  recurs and the answer is deterministic. Not for a one-off, not around what a
  linter already does, and not where upkeep would cost more than the passes it
  saves. Where the benefit is unclear, the answer is no.

New tools use the standard library only, so a hook or a bare checkout can run
them without the project virtualenv. A script also answers identically every
run and states its rule where a reviewer can read it, which is the
safety-critical standard's determinism and auditability arriving free.

## The queue, and how the project owner works

`docs/items/` is the queue: one file per item, read and written through
`bin/docket <command>`, which runs from a bare checkout with no virtualenv.
`ROADMAP.md` holds releases; `docs/WORKING_NOTES.md` holds narrative behind
open threads. **Invoke the `docket` skill for any queue workflow** — picking
what to work on, triaging, freezing a debt gate, shipping a release, closing an
item out — rather than reconstructing it from here; `subprojects/docket/README.md`
carries the item format. The rules below stay resident only because a session
acts on them before it would have any reason to load the skill.

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

- **Capture, always, and capture cheaply.** Any defect, risk, cleanup,
  optimization, inconsistency, or idea identified in a session and not fixed in
  that same session gets recorded before the session ends — findings the owner
  raises and findings you make on your own alike. `bin/docket new "..."` is the
  whole procedure: no id to allocate, no band to choose, nothing that can
  conflict with another branch, and it takes several titles in one call because
  ideas arrive in clusters. Do not ask whether to record it — filing an item is
  not a decision the owner needs to make. Say in your reply that you did. Where
  a thread is still open when the session ends, update `docs/WORKING_NOTES.md`
  too — but only for a thread spanning more than one item, outliving its item,
  or having none. One item's own reasoning goes in that item, at any length.
- **A behavior change takes effect in the session that asks for it.** When the
  owner asks for a change to how sessions work — these instructions,
  `docs/worker.md`, the `docket` skill — record it like any other finding and
  then *make the edit before the session ends*. An item on its own changes
  nothing: it sits in the queue, untriaged and therefore invisible to `bin/docket
  next`, while every session in the meantime keeps doing the thing that was just
  corrected. The capture is the record; the edit is the change. Do both, and say
  in your reply that you did both. This is the one case where editing this file
  mid-session is right despite the cache cost noted above.

  **Route it; do not append here by default.** Ask *at what moment a session
  needs the rule, and what is the cheapest thing that delivers it then.* Four
  dispositions, cheapest first:

  1. **A check or a script**, wired into `make check`, a hook, or CI. Zero
     resident context, and it never fails to fire. Deleting prose because
     something deterministic now enforces it is the strongest outcome here.
  2. **A skill**, for a multi-step procedure whose trigger is the skill's own
     trigger. It loads only when relevant; the queue workflows are the example.
  3. **A path-scoped rule** — a `.claude/rules/*.md` with `paths:` frontmatter,
     which loads when a session *reads* a matching file. Right for a rule that
     matters only in part of the tree; wrong for one that must fire before a
     first write, which no read precedes.
  4. **Resident here**, only for what a session could violate before it would
     think to look anything up.

  A rule that lands in none of the four has been lost, which is worse than this
  file staying long: never delete a rule for being wordy. `make check` reports
  the resident line total, so growth raises this question instead of passing
  silently; `PL-H7XN` carries the reasoning.
- **Name the work after the item.** On starting one, rename the session to lead
  with its id, and put that id **at the front of every commit subject** and pull
  request title. This is load-bearing rather than cosmetic: `bin/docket flight`
  recovers in-flight state by parsing commit subjects, so a session that commits
  without a leading id makes its own work invisible to every other session's
  `bin/docket next`. **A commit closing more than one item leads with all of
  them**, comma-separated: `docket check` recovers a closed item's pull request
  from the newest subject naming it, so a rider whose id never leads one is
  attributed to its own capture commit instead (`PL-GW37`). Name the branch too
  where the session creates it
  (`claude/pl-k7qx-short-slug`); a branch generated before the session started
  cannot be renamed, which is expected rather than a failure. Say in your reply
  where you put the id.
- **Commit and push as you go; the pull request arrives with the work**
  (project owner, 2026-08-31). The container is ephemeral, so an uncommitted
  thought is one interruption from gone and an unpushed commit dies with it.
  Once the owner has approved a piece of work, the pull request opens as soon as
  that work is finished and its checks are green — do not ask first, because the
  approval *was* the invitation. Two limits: it is **approved work, not any
  commits**, so a branch carrying only captured items is not a pull request; and
  where the **web harness says not to open one unless the owner explicitly
  asks**, this bullet is that ask, standing rather than per pull request, so a
  session reading both proceeds rather than stalls.
- **An `origin/<branch>` ref that resolves locally is not evidence the branch
  exists; check the remote before obeying a demand to push.** The stop hook
  picks its comparison point by whether that ref *resolves locally*, not by
  whether the branch still exists, so a stale one reports everything `main`
  has gained since as unpushed. A merge deletes the head branch and leaves the
  ref behind; the harness seeds one for a session branch nothing ever pushed.
  `git ls-remote --heads origin` says whether the branch exists and `git log
  origin/main..HEAD` whether there is anything to push — empty means the
  demand is false, and obeying it recreates a dead branch identical to `main`,
  with no content and no pull request. Restart a *merged* branch with `git
  branch -dr origin/<branch> && git fetch origin main && git checkout -B
  <branch> origin/main`. **Not `git fetch --prune`**: such a ref can be the
  only surviving copy of an item captured on a branch nobody merged, which is
  why `fetch_remote` declines to prune and what `bin/docket stranded`
  recovers. `PL-1Q3S` carries the diagnosis and the upstream half; `PL-PF8H`
  the never-pushed case.
- **Capture intent, and route it by how ready it is.** A **specific change** is
  a queue item, written now. A **feature wanted but not yet ready to build** is
  one unscoped line of intent in `ROADMAP.md`'s "Planned milestones" — filing it
  as an `L` queue item instead puts work in the queue that cannot be worked,
  where every session reads past it. A **feature being designed right now** gets
  the design round first and items only once the shape has settled, because an
  idea changes most in its first exchange.
- **Prefer finishing a feature to advancing several.** `bin/docket next`
  already ranks this way within a priority band; do not override it toward
  novelty.
- **Friction that compounds is recommended the moment it is found, not filed.**
  Some process findings are paid again by every remaining piece of work: a tool
  that answers the wrong question, a check that cries wolf, a command that ends
  red on success. Their cost is the per-item cost times the items left, so
  deferring one is a decision to pay it N more times. Say so in the reply that
  finds it — with the arithmetic, and a recommendation to do it first. Recording
  it and moving on is not enough: the owner cannot act on what only reached the
  queue. The test is arithmetic, not enthusiasm — name the per-item saving and
  multiply by the items remaining. Work that is merely valuable, cleaner or more
  interesting makes no remaining item cheaper and waits for the roadmap.

**Sweep the docs before calling an item done.** Landing a change is not
finishing it. `make check` runs `tools/doc_check.py`, which decides the
package-map, provenance-table, marked-prose-value, dangling-citation,
math-rendering and release-train questions outright, and `python3 tools/doc_check.py candidates --base <ref>` prints the
documentation lines mentioning anything the diff touched. Spend the judgment on
what neither can decide: whether each statement is still *true*. Stale
documentation is a safety issue here, not tidiness — a reader who trusts a
wrong statement about which agent is running, what a value means, or what the
interface displays can reach a wrong clinical conclusion from a correct number.
Say in your reply which files you checked, not merely that you updated the docs.

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
- Version and record provenance for scientific models, equations, constants, parameter sets, and clinically meaningful transformations. `docs/MODEL.md` is the authoritative specification for the currently implemented model: equations, units, assumptions, parameter provenance, numerical method, and known limitations.
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

Do not limit review or recommendations to conventional software-engineering concerns. Treat development of this application as a multidisciplinary professional product-design problem and proactively identify material improvements anywhere they affect scientific validity, safety, interpretability, usability, educational value, maintainability, or reliability. Recommendations should reflect the standard expected from a top-tier specialist in the relevant field, not merely common or minimally acceptable practice. When the owner's proposed approach is materially weaker than a better established approach, say so clearly and recommend the stronger approach with the reasoning behind it.

**Two standards, deliberately unequal.** The simulator and the documentation a reader of it needs — `src/`, `tests/`, `docs/MODEL.md`, `README.md` — are held to that specialist standard: code an expert contributor would recognize as high quality and could maintain without explanation. The workflow apparatus that exists so agent sessions can be productive — `subprojects/docket/`, `tools/`, `.claude/`, `docs/worker.md`, and this file — is held to *working reliably and staying streamlined*. Reliability and the functionality it actually needs are the outcome; "streamlined" describes how that gets built, never a ceiling on it. What to cut is bloat — duplicated logic, an option nobody sets, prose restating what a command already prints, a mechanism larger than its job because it was written badly — and never function or robustness, which is the trade a size target invites and this one refuses. It is scaffolding, not product; nobody evaluating this project will read it. Polishing it past sufficient is the most common way this project wastes a session. Where the two compete for a session, the simulator wins.

- Prioritize recommendations by consequence. Safety, scientific correctness, misleading output, and irreversible architectural problems outrank visual polish or minor code style, and a required correctness/safety issue is distinguished from a high-value recommendation and from optional polish.
- Prefer established standards, validated methods, and authoritative primary sources over convention-by-habit. Where a recommendation depends on current standards, guidance, libraries, or evidence, consult the source rather than memory — **before** forming the recommendation, not to confirm one already given. This covers how the project is run as much as what it builds: technical-debt policy, delegation and review design, testing strategy and release process are well-studied problems with published evidence, and advice on one of them from memory is worth no more than a solubility coefficient from memory. Recommending first and researching afterwards produces advice that has to be withdrawn, which costs the owner a decision they already made and more than the search would have.
- Challenge assumptions when warranted. Do not preserve a weak design solely because it was proposed earlier.
- The goal is not to maximize the number of suggestions. Surface the few recommendations that would materially improve the quality of the product, and explain them at the level needed to make a sound engineering or design decision.

The fields this review reaches across, and the design principles that follow from them, are in `.claude/rules/expert-review.md`, which loads when a session reads `src/`, `tests/` or `docs/`. The concrete bar for `core/` — that it should read like the domain — is in `.claude/rules/core-domain.md`.
