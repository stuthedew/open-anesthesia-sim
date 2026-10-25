# docket: close-out

Read this when an item's work is done: the closure commit, the docs sweep, the
gate report and the `--self` audit.

Part of the `docket` skill. `.claude/skills/docket/SKILL.md` is its front
page and decides which file a session reads.

## Mode: close out an item

1. Set `status: done` and `closed` - `bin/docket set <id> --status done
   --closed DATE` - and commit that **with the work, in one commit**, whose
   subject leads with **every** id it closes, comma-separated -
   `pr-title` holds the pull request's title to the same set, and the squash
   subject is the one line of `main`'s history that says which items the
   change was about (`PL-GW37` was a rider left out of it). **Do not write
   `commit:`** - the field is retired (`PL-T63T`),
   because a squash-merge discards the branch commit while the pull request
   number outlives it.

   **Retitle an open pull request to lead with the same ids, and do it
   before pushing the closure.** `pr-title` runs on `synchronize` as well as
   `edited`, so a closure pushed under the old title is checked against a
   title written before it existed. The check fails correctly, the retitle
   clears it, and what is left on the pull request is a red run beside a
   green one that tells a later reader nothing (`PL-X1S4`). A session knows
   what its commit closes before it pushes, so the ordering costs nothing.
   Nothing is owed where no pull request is open yet: the title leads with
   the ids when it is opened.

   **Write `pr` before you push the closure, with `bin/docket record N`.** `N`
   is this branch's own pull request, so the number exists as soon as the pull
   request is open - which the start mode permits at the claim push, and which
   the `pull-request` skill requires no later than the first push of work. Run
   it after `bin/docket set --status done` and before the closure commit, and
   the number rides the same commit as the work. It writes onto every closure
   this checkout introduces, committed or not, and onto nothing the base
   already holds as done; `make check` then reads the same working tree
   through `tools/pr_record_check.py --discover` (`PL-T8PT`), and CI's
   required `pr-title` job refuses the pull request until every closure
   records its number (`PL-HMZZ`). **Never edit the field by hand** - typing
   the line is how the wrong number gets recorded (`PL-QTSB`). Where the pull
   request opens only after the closure was pushed, run the command then: the
   number rides one more push, and the red check is what holds the merge until
   it lands, so the window below stays shut.

   **Do not split the closure out to get the number earlier.** Closing in the
   same commit as the work is what removes the window in which a merge takes
   the work and leaves the closure on the branch: requiring the number up
   front forced the closure into a second push, and a merge inside it left
   `main` with the fix while the queue still called the item open and a debt
   gate still counted it (`PL-D2GW`, then `PL-P5S0`). The number may trail
   the closure; the closure never trails the work.

   `bin/docket record N --merge SHA` is the explicit form, for a closure that
   reached the default base without its number - closed before this rule, or
   merged past the check. It writes onto what that merge closed and restates
   the released bullets that shipped without the number. `docket check` names
   it in the one error it still raises about `pr`: a landed closure recording
   none.

   **Move every item `bin/docket set --status done` says you just unblocked,
   in this pull request.** It names the items whose last recorded blocker this
   closure clears - the reverse of `blocked-by`, derived rather than stored -
   and `bin/docket check` refuses each one left at `blocked`, so the pull
   request cannot go green until all of them have left it (`PL-2349`). You are
   holding the context the judgment needs, which a later grooming pass would
   not be. Read each against the tree and either `bin/docket set <id> --status
   ready` with its `--verify` and `--payoff` written for the end state, or
   write what is really holding it into `blocked-by` - an item for the
   condition, per `PL-0H5D` - in this branch's commit. Of 13 items reached
   this way across the two passes that preceded the print, 6 were genuinely
   startable and the rest were already done inside another item, held by a
   condition nobody had declared, or carrying a user-facing question written
   in since triage - so which way each moves is a judgment nothing makes for
   you, and only leaving it `blocked` is refused (`PL-PQC7`, `PL-6T44`).

   **Two of them are worth more than the rest, and neither is visible from the
   id.** An item classed `safety` or `science` that also carries `anticipated`
   is exempt from the debt gate only while `status: blocked` holds with it, so
   promoting one is the event that returns a finding to the gate built to catch
   it - say in the reply which way you called it and why (`PL-ZF2G`, `PL-JFQ3`).
   And where the closure releases several, say so as one group rather than as a
   list of ids: `PL-1FT6` holds eight.
2. **Sweep the docs.** `make doc-check` decides the package-map,
   provenance-table, marked-prose-value, dangling-citation, math-rendering and
   release-train questions outright, and
   `python3 tools/doc_check.py candidates --base <ref>` prints the
   documentation lines naming anything the diff touched *as code* - a term
   that is also an ordinary word is reported only where a line marks it as
   code, and the output names which terms those were.

   Landing a change is not finishing it. Spend the judgment on what neither
   can decide: whether each statement is still *true*. Stale documentation is
   a safety issue here rather than tidiness — a reader who trusts a wrong
   statement about which agent is running, what a value means, or what the
   interface displays can reach a wrong clinical conclusion from a correct
   number. Say in the reply which files were checked, not merely that the docs
   were updated.
3. Capture anything found but not fixed as its own item.
4. **Report gate progress if the item is one the gate contains.** Membership is
   decidable rather than a judgment: `bin/docket wave` prints the gate's open
   entries by id and `bin/docket gate` recomputes the split. When the item is
   one of them, close out with where the gate now stands — how many of its
   frozen entries are done, how many remain, and what the remaining ones are,
   glossed and grouped so the shape is visible (what is blocked on the
   strongest model, what is cheap). Say the same for entries the milestone
   clears itself. When the gate does not contain the item — anything captured
   after the freeze, or any other work the frozen list does not name — end
   without a gate report. Listing the remaining entries then is work arriving
   in a discussion that was not about it.
5. **Audit the branch: `bin/docket verify --self <id>`**, naming every id the
   closing commit leads with, since the diff is selected per id from the
   commits that name it. **On a branch that changes the simulator, run step
   8's prose review first.** Its rewrites change files that this audit reads.
   Of five simulator branches that skipped step 8, two reported running this
   audit, so the step's place at the end of the list was passed over
   (`PL-W04Z`). It runs the item's own `verify:` command and `make
   check`, so it *is* the close-out's proof rather than a step beside one -
   re-run it until it says `ACCEPT`. A `REJECT` that stopped early ran
   neither.

   **`--self` is not optional, and the bare command asks the wrong question.**
   Without it, `verify` asks whether a *delegated* worker exceeded its
   commission, and four of its guards then fire by construction on the path
   this procedure prescribes: the capture and leading-id rules put other items'
   files in the diff; an item whose declared work is a `.claude` file trips
   `gate_paths`; an item non-delegable *because* it touches `protected_paths`
   is one a session works itself; and step 1 edits the front matter the guard
   watches. So a correct close-out gets `REJECT`, which trains a reader to skim
   the block where a real protected-path failure is printed (`PL-69JZ`,
   `PL-7XTS`).

   It relaxes those four and nothing else. They still run and still name every
   path, printed as `NOTE` with the reason they are not refusing - read them,
   because a path you did not expect is the finding. The four integrity checks
   stay absolute: no suppression added, the item's own command passes, the
   unit tests catch a mutation of each changed line, and `make check` passes.
   A session may re-scope its own commission; it may not weaken what measures
   it, and it may not skip the test.

   **The command check takes an exemption the *item* declares, and which copy
   of the item each field is read from - the base's or your branch's - follows
   one rule, stated on `Commission` in `subprojects/docket/src/docket/verify.py`
   (`PL-B8HZ`).** An *outcome* (`status`, `closed`, `reason`, `pr`) is your
   branch's and excuses nothing. A *prediction* (`verify:`, `touches:`) is
   measured against the base's copy, and your branch's copy is a correction of
   it: honoured, and printed beside the base's with the base's own result. A
   *waiver* (`not-delegable:`) removes a refusal and is the base's alone, so
   adding one beside the work it would excuse waives nothing and is reported
   as your own word for it.

   - `verify:` is a prediction, and rewriting it is a correction the audit
     honours and prints: where the base's copy commissions a different
     command, both run, yours decides the check, and the report carries
     ``commissioned: `A` - fails on this tree (exit 1); this branch runs `B`
     instead`` under it. A rewritten command is never silent, so say in the
     reply why the commissioned one was wrong - that line is what a reviewer
     will ask about (`PL-PZ6T`). `touches:` is read the same way: the diff is
     measured against the base's, and a path only your own widening declares
     is named as that in the NOTE.
   - A `dropped` item, or one carrying `not-delegable:`, has no command to run,
     and the check says which applies rather than stopping the audit dead
     (`PL-L4KX`). A dropped item that still carries a `verify:` has it printed
     and not run, so there is no need to delete one when dropping (`PL-BX1C`).
     The drop is an outcome and is read off your branch, since the close-out
     is what writes it - but a `not-delegable:` reason is a waiver and excuses
     only a command the base never commissioned. Deleting the base's `verify:` and writing a
     reason beside it is refused (`PL-KSV2`), and the paragraph below applies:
     restore the command, or give the one that proves the work.

   **So a `REJECT` here is still a `REJECT`.** Meeting one on work you believe
   correct means the commission did not anticipate it: say so to the project
   owner with the check's own words, and do not add a declaration to the item
   on this branch to clear it. The whole worth of a waiver is that a reviewer
   wrote it first.

   **The mutation check refuses a branch whose unit tests miss a mutant of a
   line it changed** (`PL-CZXN`; project owner, 2026-10-19, ratified, over
   making the old assertion check an advisory and over keeping it). It runs
   `tools/diff_mutation.py --verdict` once for the branch. That takes seconds
   where the branch changes no function mutmut mutates, five to eight minutes
   on a typical branch that does, and 36 minutes for the largest batch measured
   on 2026-10-24, 340 mutants. Iterate with `make mutate`, which prints the
   same survivors, rather than by re-running the audit.

   The same check refuses a branch that weakens a changed simulator unit test,
   where a mutant of the display modules that the test's base version catches
   survives the branch's version (`PL-7FPD`). That costs about two more
   minutes for each version of the changed tests. Clear it by restoring what
   the test checked. `docs/mutation-testing.md` § "What the check of a changed
   test leaves unmeasured" says what it does not reach.

   Clear a refusal of a mutant of a changed line honestly, in one of two ways:

   - **Write the unit test that catches the mutant.** The check prints each
     mutant's line and its diff, and `uv run --group mutation mutmut show NAME`
     prints it again. A mutant only an integration test catches still refuses,
     because only the unit tests run against it.
   - **Mark an equivalent mutant `# pragma: no mutate`**, on the line, where no
     input can tell the mutant from the original. The check prints every such
     line on a changed line, so say in the pull request body why each one is
     equivalent.

   A survivor on a line the branch did not change is listed and not counted.
   Where the check says it has no answer - the run failed, timed out, or could
   not place a mutant on a line - fix that cause and re-run. Never read a
   missing answer as a pass.

   Run the bare `bin/docket verify <id>` only when reviewing a branch somebody
   else was commissioned to write.

6. **Review the diff adversarially before the pull request opens, where the
   change earns it** (project owner, 2026-09-20, ratified, over leaving it to
   a session's judgment case by case). The trigger is size and location, so
   that it is decidable rather than a mood: the diff touches
   `src/anesthesia_sim/` and changes roughly **200 lines or more**. Below
   that, `make check` and your own adversarial re-read of the diff are the
   whole of the bar and this step does not apply.

   **`make check` passing is not this step.** The suite proves that what has a
   test still holds, which is exactly what a defect nobody wrote a test for
   survives. `#784` was opened green and merged on that; a review run
   afterwards found three real defects in it, one `safety`-classed - a Reset
   that deleted another run, `add_run` admitting a run the case never
   sanctioned, and a vanished fork instant silently re-pointed at induction
   (`PL-LQ19`, `PL-K5NY`, `PL-J12Z`). Found an hour earlier they were one
   commit. Found after the merge they were three items, a second pull request,
   and a permanent record of `PL-VKJW` and `PL-QRD1` closing against work that
   was incomplete.

   **What counts.** Independent passes over the change, each looking for a
   different class of defect rather than all re-reading it the same way -
   lifecycle and state, the domain invariants, what a displayed value could
   mislead a reader into, whether the new tests would fail if the behaviour
   were inverted, the rules this repository states, dead code. Then attack
   what they return: a finding nobody tried to refute is a suspicion, not a
   finding. The `Workflow` tool is one way to run this and not the only one;
   what matters is that the finding and the scepticism come from different
   passes.

   **Make one of the sceptics run the claim rather than reason about it.**
   Both refutations that mattered on `#784` were empirical. A fourth candidate -
   that per-run holder widgets cost the plots 18 px of layout spacing - read as
   obviously true and measured **0 px** at two window sizes, and would have
   been filed on argument alone. Conversely the three that were real were
   each reproduced with a scratch script under the offscreen platform before
   being written down.

   **Then distrust a high uphold rate.** On `#784`'s first pass, refutation
   killed 1 of 4. On its second, 3 of 18 verdicts - and that is the number to
   be suspicious of, not the first. Sceptics pointed at a named method tend to
   agree with it; when almost nothing is being killed, the refutation has
   become a second opinion and the tail of `should-fix` and `nit` findings is
   yours to check by hand before any of it reaches the queue.

   **A confirmed finding does not stop the close-out; it joins it.** Fix it on
   this branch if it is in scope and the item's `touches` already reach it.
   Otherwise file it - grouped under one `feature:` where the findings are one
   problem - and say in the reply what you found and what you left.

7. **Sort the survivors that step 5's audit printed, where the diff changes a
   function that mutmut mutates.** Those are the modules that the
   `only_mutate` globs in `pyproject.toml`'s `[tool.mutmut]` table name:
   `core/` and seven presentation modules. The audit's mutation check runs
   `make mutate`'s tool on the functions that the branch changed, so there is
   no second run to make. A survivor on a changed line has already refused the
   audit, and one on a line the branch did not change is named in its notes.
   Sort each survivor as `docs/mutation-testing.md` § "Read a survivor" says,
   and list each one with its kind in the pull request body.
   `uv run --group mutation mutmut show NAME` prints a survivor's diff while
   `mutants/` is left from the run. Write the test that kills a real gap in
   this change, and file an item for a gap that is not this change's. A
   survivor on a line the branch did not change never holds the pull request
   (project owner, 2026-10-17, ratified, over a whole-tree mutation score as a
   target, `PL-Y1PS`).

8. **Have a fresh reviewer read the branch's new long prose in the simulator,
   before step 5's audit**, because the rewrites change files that the audit
   and `make check` read. Run `uv run python tools/new_prose.py`. It prints each
   docstring and comment of 30 words or more that the branch added or changed
   in `src/` or in a file under `tests/` that imports the simulator, with its
   rows and the code around it. Where it prints none, this step is done.
   Otherwise start one subagent, `general-purpose` at the session's own
   effort level (`docs/maintainer.md`, 2026-10-19), with the
   prompt below followed by the tool's whole output. The prompt tells it to
   open nothing, so it costs one turn (project owner, 2026-10-18, ratified,
   over a review on every branch and over no review, `PL-PRCS`).

   ```text
   Review the prose below for a careful newcomer: someone who knows
   anesthesia or Python but has not read this repository. Hold each unit to
   .claude/rules/plain-writing.md, which you already have. Do not open a file
   or run a tool. Everything you need is below, and you have one reply.

   For each numbered unit, write one of two things. Write "[N] keep" when a
   newcomer would understand every sentence on the first reading. Otherwise
   write "[N] rewrite" and then, in a fenced block, the new text for the rows
   marked ">", exactly as they would stand in the file: the same indentation,
   the same comment markers or quotes, and lines no longer than 100
   characters. Rewrite only the sentences that need it.

   Keep every fact. Keep each number, unit, value, condition, exception,
   identifier in backticks, item id and citation exactly as written. Change
   no code. Where you cannot tell what a sentence means, say so in one line
   rather than guessing.
   ```

   Apply each rewrite yourself. Reject any rewrite that drops or changes a
   number, a unit, a condition, an identifier or a citation, and keep the
   original sentence there, because the safety-critical standard applies to
   what a docstring states. Say in the pull request body how many units the
   reviewer read, how many it rewrote and how many rewrites you rejected.
   Record the same three counts as a trailer in the last paragraph of the
   commit that applies the rewrites, or of the next commit where there were
   none: `Prose-review: read N, rewrote M, rejected K`. `bin/docket arm` holds
   a simulator branch whose long prose was added after the newest such
   trailer, as `uv run python tools/new_prose.py --count` counts it (`PL-W04Z`).
   `PL-PRCS` records what the step costs. `PL-J6CK` measured what it buys on
   2026-10-19: long prose from the branch that ran it was awkward in 22% of
   blind verdicts, against 58% from branches that skipped it, so it is kept.

9. **Run the blind generalist review passes on a simulator branch, before step
   6's review, step 8's prose review and step 5's audit**, because a fix for a
   finding changes the files those steps read. Every simulator pull request
   gets one pass before it merges. One that changes the model's code, its
   parameter files or `docs/MODEL.md` gets a second (project owner, 2026-10-24,
   ratified, over two passes everywhere and over one pass everywhere,
   `PL-TDV9`). `docket.arming.SECOND_PASS_PATHS` holds that list of paths.
   `PL-TBQS`'s replay of 20 merged simulator pull requests found that one
   blind generalist named about half of the defects filed later, as many as a
   three-specialist panel.

   Commit the work, then run `python3 tools/blind_review.py`. It prints how
   many passes the branch owes. Where it owes none, this step is done.
   Otherwise it builds one directory per pass outside the repository, holding
   only the committed tree and the branch's diff, and prints one brief per
   pass. Start one `general-purpose` subagent per brief, all in one message,
   at the session's own model and effort. Give each its brief exactly as
   printed and nothing else, so no pass sees this session's reasoning or
   another pass's findings.

   Treat each finding as a review comment on your own pull request. Check it
   against the code first, because a reviewer can be wrong. Fix a real
   `blocking` or `should-fix` finding on this branch, with the regression test
   the standards ask for. File a real finding that is not this change's with
   `bin/docket new`. Fix an `optional` one only where it is plainly correct
   and small. List every finding in the pull request body with what happened
   to it: fixed in a named commit, filed as an item, or rejected with the
   reason. A fix made for a finding needs no further pass.
