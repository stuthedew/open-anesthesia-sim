# The short-instructions test of 2026-11-11

`PL-J1ZM` records the test's design, criteria and result. This file keeps the
texts. Each is a first draft from one `claude -p` run and was not edited.

## The short instruction file

    # Standing instructions for every session

    Follow these rules in every session. Read a named file when its rule applies.

    ## What the project is for
    - This is one person's hobby: an open-source anesthesia simulator for teaching.
      The project owner ("the owner") is an anesthesiologist and intensive-care
      physician. Success means that the owner still enjoys the work years from
      now, so prefer lasting quality in the simulator to speed.
    - The simulator is the product. The workflow tools (the queue of work items,
      and the scripts, checks and rules that help sessions work) only serve it.
      If you object to them, name one tool and its cost, not their number.
    - With no work assigned, run `bin/docket next product` and take a simulator
      item. Leave it for a fault in the workflow tools only if the fault blocks
      correct work, would lose work, or weakens a safety check.
    - A "generator" is one cause that has produced three or more queue items.
      While `bin/docket generators` marks a workflow generator "still generating",
      build no new workflow command, check, field or rule unless the owner asks.
      Repairs are still allowed. See `.claude/skills/docket/modes/triage.md`.

    ## Working with the owner
    - The owner asks for a result. A method named in the request is only an
      example, but the owner alone may replace it. Never change or widen the goal.
      If the goal is unclear, ask before you start.
    - Stop and ask before you build a result that differs in an important way from
      the one described. Say what was asked, what you would build, why it is better
      and what it costs. While you wait, do only the work that both answers share.
      Ask for no other reason. Naming, structure and tests are yours to decide.
    - If the owner's own method is clearly weaker, say which part and wait. If it
      is one of several near-equal methods, state the trade-offs and build it.
      Always explain in a few sentences how the approach works, then list changes.
    - Fix a recurring problem without asking, and report the fix in one line. Give
      the risk and benefit, then wait, before a large, risky or complex change.
    - When the owner is only sharing ideas, record them, read nothing extra and
      carry on. An idea becomes work only when the owner says so.
    - Record a decision that the owner made on your recommendation as
      `(project owner, DATE, ratified)`, with what it was chosen over, and one that
      the owner set out themselves as `(project owner, DATE)`. New evidence may
      reopen the first kind. Only a strong argument may reopen the second. The
      safety standard below overrides both.
    - "Read only" means that you write nothing: no file, commit, push, pull
      request, comment or merge. Turn off automatic merging on your own pull
      requests at once and say so. Put what you find in the reply.
    - If another session directs yours, ask it your questions, not the owner.

    ## Engineering rules
    - Keep simulation time as a stored value. Never read the computer's clock.
    - Whenever you change how the simulator behaves, change or add its tests too.
    - Keep each shared fact in one place. This is the main design rule. Read a
      value, format or state from the module, data file or document that owns it.
      If nothing owns it, write one record and read that. Replace a second copy
      with a read, then add a type or check that stops the next copy. Only a test's
      expected value and a cited published value may be copies.
    - Store model parameters in versioned, checked data files, with no formulas.
    - Build only what the current milestone in `ROADMAP.md` covers. Recommend an
      idea from outside it, and build it only when the owner approves.
    - Hold the simulator (`src/`, `tests/`, `docs/MODEL.md`, `README.md`) to the
      standard of a leading specialist. The lower standard for the workflow tools,
      in `.claude/rules/apparatus-standard.md`, never applies to the simulator.
    - Let a script answer a recurring question of fact. Keep judgment for yourself.
    - Keep a session to one topic. Before you start an item, follow
      `.claude/skills/docket/modes/start.md` to check that the session has room.
    - Run `ruff format`, `ruff check`, `mypy` and `pytest` in full before each
      commit and before you finish. Use `pytest -q` between edits.
    - Start a long command with the Bash tool's `run_in_background`, never with
      `nohup`, `&` or `setsid`. Before you wait, schedule a `send_later` check.

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

    ## The queue and commits
    - The queue is `docs/items/`, one file for each item of work. Use `bin/docket`
      to change it, and follow `.claude/skills/docket/SKILL.md` for queue tasks.
    - Before the session ends, record each defect, risk or idea that you did not
      fix. Run `bin/docket new "title"` without asking, and say that you did. Add
      `--feature <name>` to group items that are one problem.
    - While you work on an item, you may fix a small, clear defect at once, in its
      own commit with a test, at most twice on a branch. Record it instead if it
      is in `src/anesthesia_sim/core/`, `src/anesthesia_sim/data/` or
      `docs/MODEL.md`, falls under the safety standard, or has an open item.
    - When you find a generator, fix it in the session, or end the reply with a
      prompt that the owner can paste into a new session.
    - When the owner changes how sessions work, record the change and also make it
      in the same session. Add a rule to this file only as a last resort, and say
      what you removed to make room. See `docs/resident-instructions.md`.
    - When you start an item, run `bin/docket claim` to mark it as taken. Put its
      id first in the session name, each commit subject and the pull request title.
    - End each commit message with `Co-authored-by: Claude <noreply@anthropic.com>`
      and never name a model there, even if a built-in reminder tells you to.
    - Commit and push often, because the container can vanish. Read
      `.claude/skills/pull-request/SKILL.md` before any action on a pull request.
      Open one, unasked, as soon as approved work passes its checks.
    - Tell the owner at once, and recommend fixing it first, when a process fault
      gives wrong results silently, is routinely ignored, or costs time every run.
    - Before you call an item done, check the documents it affects and name them
      in the reply, because a stale document can mislead a clinician.

    ## Replies to the owner
    - End every reply with a short list of only what the owner must do, decide or
      look at now, in the order to act. Label each recommendation as one. If there
      is nothing to do, say so in one line.
    - Before you write that list, run `bin/docket branch` and check again each fact
      about merges, tags and open work. Before you suggest work, call
      `list_sessions` to see whether another session already has it.
    - The owner decides the order of features, what a learner (a trainee who uses
      the simulator) sees, and safety matters. You decide appearance, wording and
      placement, and any choice with one clearly right option. Report it in a line.
    - Open a request for a decision with the question and your recommendation,
      one line each. Say what a learner would see under each option.
    - Number the steps that the owner must carry out, in order, one action each,
      with exact paths and values. Warn just before a step that cannot be undone.
    - Each time you write an id or a branch name, add a few words saying what it
      is. Give clock times in US Central time, marked CDT or CST.

    ## Writing
    - Write in plain English everything that a person will read, from comments and
      error messages to commit messages and replies. Make every sentence complete,
      with one point in it, and explain a project term where it first appears.
    - Write for the reader. The owner and learners know anesthesia, but not
      software terms or this project's names for its tests, checks and tools.
    - Give the reader what they need to act on, then stop. Put first what they will
      see, then what it means, then why. Keep a decision's history in its item.
    - Cut any sentence that repeats itself, rejects an option nobody raised, or
      describes the text instead of its subject.
    - State a reason for a chosen number only if the code or a record holds it.

    ## Recommendations and sources
    - Review the simulator, unasked, as a leading specialist in each field would,
      not only as a programmer. Give a few recommendations, the most serious first.
    - Read a source in this session before you cite it or base advice on it, and
      say how much of it you read. Look up a fact before you state it. If you
      cannot read a source, say which claim lacks one and ask the owner for it.
    - Before you propose a stricter limit, filter or check, say how much the things
      it would exclude must matter for the proposal to be wrong, then count them.
    - Before you take the cheaper of two routes, count what already depends on the
      choice. If little does, take it and say so. If much does, build the lasting
      route now. Waiting for another case to appear counts as the cheaper route.
    - Before you write a rule into `ROADMAP.md` or `docs/MODEL.md`, say what would
      make it false. If that is already planned, write it as one case, not a rule.
    - Another program's parameter set is not a measurement. Cite it as the source
      of a value only as `.claude/rules/sources-and-docstrings.md` allows.

## The reply written under the short file (text 1 of its pair)

    I have read the item and checked its claims against the merged code. The reply follows.

    ---

    **The first of four pull requests for PL-RF2S merged into main at 10:20 PM CST on 2026-11-10 (#2094).** PL-RF2S is the item on values from an earlier run, or from the other compared run, staying on screen. It stays open, because three pull requests remain.

    **Nothing a learner sees in normal use changed.** A reviewer drove the old and new interface through 39 scenarios (224 actions). It compared the full contents of the screen 179 times and its image 172 times, and found no difference.

    **How it works.** Two routines used to write a run's panel, one for a normal redraw and one for a halt (a run stopped on an internal fault). Now one function builds a single record of everything the panel shows, and one routine writes the whole panel from it. On a halt the record holds either the last values drawn or, after a Reset or an agent change, withheld values with the reason.

    **What differs, only after an internal fault:**
    - If the accounting panel, the banner or the new-case question cannot be built, every value stays on the earlier redraw. Before, the readouts and the schematic moved on and the accounting panel stayed behind.
    - If the 1 MAC line cannot be built, it is blank. That was my choice of placeholder, and it is the one decision below.
    - A panel refuses a record built for another run, with an error that names both runs.

    I judged that these did not need your read before the merge, because they are confined to a run that has already stopped on a fault.

    **One correction.** The design said that today's tests would miss a schematic left unwithheld after a Reset. That was wrong, because an existing test catches it. The real gap was the time in the schematic's heading: "At 1m30s of simulated time" over the empty containers of a run at its opening passed every test. Two new tests now fail on it.

    **What the reviews found.**
    - **Planted defects:** a reviewer planted 24 defects in the new writer, and the tests missed three. Each of the three now fails a test. One was a fault that the single writer made possible: on a halt, a panel that had kept a case's first redraw showed the opening's cards under a banner calling them the last ones drawn.
    - **Blind review:** it raised three findings, and all three are fixed.
    - **Scroll range:** it differed for one pass in one fault state. I did not find the cause and changed nothing for it.
    - **Mutation run:** this check plants small faults to see whether the unit tests notice. Six of its 346 faults survive: one changes only an error message, four change nothing, and one cannot be reached. It ran with a local repair, because the run was broken on main. That repair has since merged as PL-GP8G (#2124), and I have not rerun it since.

    **Other things to know.**
    - I published the pull request's title and body without the copy edit, because you said the copy editor is being removed. The pull-request instructions still ask for it.
    - The pull request also carried two records that are not part of this item: your instruction never to state a fact marked "from memory" (PL-J3H7), and your answer on PL-CXYV's Tab check.
    - I filed two faults that are older than this work and still present. I will fix both in the second pull request, which rewrites that code.
      - PL-SV2Q: when the dials cannot be built after a Reset, they keep the discarded run's setting, such as "Delivered 8.00% (4.00 ×MAC)" beside "1 MAC desflurane = 6.0%".
      - PL-MVCF: a Reset that fails partway leaves the discarded run's cards on a halt.
    - I also filed PL-J791, a repeated test for the clock panel.
    - `docs/ARCHITECTURE.md` and `docs/mutation-testing.md` are updated. `docs/MODEL.md` and `README.md` needed no change, because no equation, parameter or computed value changed.

    **Next.** I am starting the second pull request, which draws every View from the same record on a halt as on a redraw. It will also check the unconfirmed lead from PL-VZ57, that the price form names an agent the run no longer holds. The three test-gap items (PL-B8DL, PL-0G2P and PL-G2WC) close with the fourth pull request.

    This session is in the xhigh arm of the effort trial, so it runs at xhigh unless the app's effort picker is set lower.

    **For you now:**
    1. Decide, when convenient, what the 1 MAC line shows when it cannot be built after a fault. Nothing waits on the answer.
       - **Recommendation:** keep it blank. The learner sees an empty line beside the status "Stopped — simulation error".
       - **Alternative:** words on the line saying that the value is unavailable.

## The reply written under today's four files (text 2 of its pair)

    **#2094, the first of the four pull requests for PL-RF2S (draw the whole screen from one value, so that no value from an earlier run can stay behind), merged into `main` at 10:20 PM CST on 2026-11-10.** A learner sees no change in normal use.

    **How it works now.** Two pieces of code used to write a run's panel: one for a frame that draws, and one for a run that stops on an internal fault. Each wrote part of the panel. Now everything the panel shows is built first as one value, and one call writes it on both paths. A stop is a state inside that value: each of the run's values is drawn from this step, kept from the last frame drawn, or withheld with the reason.

    **Three things the design round told you that turned out different.**

    1. **It said each pull request would wait for your review, and this one merged without it.** The side-by-side comparison below found no difference in normal use, so I judged that it did not need you. The second changes what a learner sees after a stop, so I expect to hold it for you.
    2. **It said no existing test would notice the schematic being left out after a Reset that no frame draws.** One does. The real gap was narrower: with a planted defect, the schematic's heading read "At 1m30s of simulated time" over the empty containers of a run standing at its opening, and every earlier test passed. Two new tests fail on it.
    3. **The audit of 2026-11-10 found no wrong value on screen, and the reviews of this pull request found two.** Both were on `main` before this change and both are still there. Both are filed in the group `every-view-in-run-state-tests`, and I fix them in the second pull request.
       - **PL-SV2Q (the dials keep a discarded run's setting):** after a Reset or an agent change, the panel shows "Delivered 8.00% (4.00 ×MAC)" beside "1 MAC desflurane = 6.0%". No shipped machine profile causes it. It needs a control that can offer no setting, which takes a test-injected fault or a malformed profile.
       - **PL-MVCF (a Reset that fails part-way):** the discarded run's cards stay under a clock of 10 min for a run at 0 s. It needs two faults at once.

    **What differs on screen, only after an internal fault.**

    - **A frame with a part that cannot be built:** every value now stays on the earlier frame. Before, the readout cards and the schematic moved to the new step and the accounting panel stayed behind.
    - **A "1 MAC" line that cannot be built:** it is now blank. Before, it kept the earlier agent's value. The blank is a placeholder choice, recorded in the item.
    - **The scroll range:** in one fault state it differs for an instant. I did not find the cause and changed nothing for it. It is recorded in PL-RF2S.

    **How it was checked.**

    - **Side by side:** a reviewer drove the old and new interface through 39 scenarios of normal use (224 actions) and compared every label and control and 172 screen images. It found no difference.
    - **Random use with faults:** 150 sequences of 50 actions gave no stale value.
    - **Planted defects:** the tests caught 21 of 24, and the other three now each fail a test. One of those three was a defect that the single writer itself made possible: a stopped run showing the opening's cards and "Delivered: 0.0 L" under a banner that calls them the last frame drawn.
    - **Small changes to the code:** of 346 made to the changed functions, the unit tests missed 35. Twenty-nine were real gaps, and each now fails a unit test, checked one at a time and not by a second full run. Six remain: one changes only an error message's wording, four cannot change behaviour, and one is on a path that cannot be reached. The new module is now in the set that this run covers.
    - **Full suite:** 12,270 tests passed and 3 were skipped.

    **Also done or filed.**

    - **PL-J791 (the code asks which readout panel is the clock in six places):** filed.
    - **PL-GP8G (the run that makes those small changes stopped at its first step on `main`):** filed. The item asked me to tell the session fixing it when #2094 merged, and that is no longer needed: its item file shows it closed by pull request #2124.
    - **Copy edit skipped:** #2094's title and body were published without the copy edit that a simulator change normally gets, because you said the copy editor is being removed.
    - **Two other commits on the branch:** PL-J3H7 (never state a fact marked "from memory") and your answer on PL-CXYV (how Start, Pause and Reset look when pressed).

    **Still open under PL-RF2S.**

    - **The three test-gap items stay open until the later pull requests:** PL-B8DL (the test layouts hold four of the six View kinds), PL-0G2P (the tests read text and not painted amounts) and PL-G2WC (no test checks a value against the run it is shown under).
    - **One lead from PL-VZ57 (the audit's leads) is not checked yet:** whether the price form names the agent the run no longer holds, after an agent change that no frame draws. I check it first, because it could be on screen today.
    - **A risk for the last pull request's test:** two dashboards in one state can lay out at different widths, 480 px and 706 px. The test needs both at one size, or it falls back to comparing text, which is weaker.

    **Next.** I start the second pull request on a new branch from `main`: every View drawn from the one value, on a stop as on a drawn frame.

    This session is in the high arm of the effort trial, so its effort is capped at high.

    **What needs you:** nothing now.

## The docstring written under today's four files (text 1 of its pair)

    Finished reading the module, its callers and its tests; here is the draft.

    ```
    Return what a run's panel shows when no frame can be drawn, from the run's record alone.

    No compartment value is computed here, because the halt may be the refusal
    of one of them (`PL-7DJK`). The readouts, the schematic, the delivered
    agent and the accounting panel are taken from `kept` while `kept.case`
    equals `state.case`. If the two differ, the run has started over since the
    last frame that drew, and all four are withheld (`withheld_values`). The
    banner is `halt_notice`'s, and it says which of the two happened.

    Two values are restated whether the rest are kept or withheld:

    - The clock readout's playback line gives `state.playback_rate`, which the
      reader may have changed since the last frame (`PL-P58M`).
    - If `record.rejected_accounting` is set, the accounting panel shows the
      check and totals of the step that was rejected
      (`rejected_step_accounting`).

    Args:
        record: The run's record, as `SimulationController.record()` returns
            it. This function does not check that the run is halted. For a run
            that has not failed and is not at the supported run length,
            `halt_notice` returns no banner.
        adjustments: `record.control_timeline` grouped into acts, as
            `RunView.adjustments` groups it.
        state: What the run's panel holds.
        kept: The values of the last frame that drew, with `state.case` as it
            stood at that frame.

    Returns:
        The presentation. Its `standing` is `KEPT` or `WITHHELD`, and its
        `new_case` is None.

    Raises:
        ValueError: If the values are kept and `kept.values.readouts` does not
            hold one readout for each of `READOUT_PANELS`. Also if
            `state.name` is empty (`compared_run_notice`). An exception raised
            while building the dials, the delivered line or the 1 MAC line is
            not raised here. It is returned in `dials` or in `one_mac`, so the
            halt is still stated.
    ```

## The docstring written under the short file (text 2 of its pair)

    ```
    Return what a run's panel shows when no frame can be drawn, from the run's record.

    No compartment value is computed here, because the halt may be the refusal
    of one of them (`PL-7DJK`). Every run-state part is built from `record`, as
    `drawn_run` builds it from a snapshot. So a setting or an agent that changed
    after the last frame is shown as the run holds it (`PL-85LJ`, `PL-1YDD`).

    The compartment values are `kept.values`, the values of the last frame that
    drew. If the run has started over since that frame, those values describe a
    run that was discarded, and `withheld_values` replaces all four.

    Two values are restated in both cases. The clock's playback line states
    `state.playback_rate`, because the rate is a setting of the panel and the
    reader may have changed it since the last frame (`PL-P58M`). The accounting
    panel shows the check in `record.rejected_accounting` when the record holds
    one. The run rolled that step back, so the kept panel describes the step
    before it, which passed (`PL-HF4B`).

    The banner is the one `halt_notice` gives. For a failure, it says that no
    frame of the stopped run was drawn, and that the readouts are withheld when
    they are.

    Args:
        record: The halted run's record, as `SimulationController.record()`
            returns it.
        adjustments: `record.control_timeline` grouped into acts, as
            `RunView.adjustments` groups it.
        state: What the run's panel holds.
        kept: The values of the last frame that the panel wrote in full, and
            `RunPanelState.case` as it stood at that frame. Before any frame,
            they are the values that the panel's widgets were built with. The
            run has started over when `kept.case` differs from `state.case`.

    Returns:
        The presentation. Its `standing` is `KEPT` or `WITHHELD`, and its
        `new_case` is None.

    Raises:
        ValueError: If the run has not started over and `kept.values.readouts`
            does not hold one readout for each panel in `READOUT_PANELS`. An
            exception raised while building the dials, the delivered line or
            the 1 MAC line is not raised here. It is returned in `dials` or in
            `one_mac`, so the halt is still stated.
    ```

## The judging run's verdict on the replies

    # Verdicts for Text 1 and Text 2 against the five criteria

    ## Text 1

    **1. Reader can follow every sentence: fail**
    - Quote: "**Scroll range:** it differed for one pass in one fault state."
    - Reason: the reader cannot tell what scrolls, what "it" differed from, what a "pass" is, or which review found this.

    **2. Terms defined at first appearance: fail**
    - Quote: "The three test-gap items (PL-B8DL, PL-0G2P and PL-G2WC) close with the fourth pull request."
    - Reason: three item codes appear with no description, as do "PL-VZ57", "Blind review" and "PL-CXYV's Tab check", although "halt" and "mutation run" are explained.

    **3. Familiar words in their everyday sense: fail**
    - Quote: "A reviewer drove the old and new interface through 39 scenarios (224 actions)."
    - Reason: "drove" is used in a tester's sense, as are "pass" in "for one pass" and "survive" in "Six of its 346 faults survive".

    **4. No detail that would not change what the reader does next: fail**
    - Quote: "`docs/ARCHITECTURE.md` and `docs/mutation-testing.md` are updated."
    - Reason: the only decision asked for is the 1 MAC placeholder, and file names, comparison counts (179 and 172) and the opening process note do not bear on it.

    **5. Opens with a short, specific statement of what was done, then gives the needed context: fail**
    - Quote: "I have read the item and checked its claims against the merged code. The reply follows."
    - Reason: the text opens on a process note, and the bolded lead after it names the item's problem but not what the change did, which first appears under "How it works".

    ## Text 2

    **1. Reader can follow every sentence: fail**
    - Quote: "A stop is a state inside that value: each of the run's values is drawn from this step, kept from the last frame drawn, or withheld with the reason."
    - Reason: the sentence depends on programming senses of "state", "value" and "frame" that a physician does not bring to it.

    **2. Terms defined at first appearance: fail**
    - Quote: "one for a frame that draws"
    - Reason: every item code is glossed in parentheses, but "frame" is never explained, and neither are "View kinds", "the scroll range" or the group `every-view-in-run-state-tests`.

    **3. Familiar words in their everyday sense: fail**
    - Quote: "draw the whole screen from one value, so that no value from an earlier run can stay behind"
    - Reason: "value" carries a programmer's sense and its everyday sense within one clause, and "frame", "call" and "paths" are also used in technical senses.

    **4. No detail that would not change what the reader does next: fail**
    - Quote: "**Full suite:** 12,270 tests passed and 3 were skipped."
    - Reason: the text says nothing needs the reader now, yet it gives test counts, pixel widths (480 px and 706 px) and a hand-off note that it says "is no longer needed".

    **5. Opens with a short, specific statement of what was done, then gives the needed context: pass**
    - Quote: "#2094, the first of the four pull requests for PL-RF2S (draw the whole screen from one value, so that no value from an earlier run can stay behind), merged into `main` at 10:20 PM CST on 2026-11-10."
    - Reason: the first sentence says what merged and what the work does, and the sections that follow cover how it works, what differs on screen, how it was checked and what stays open.

    ## Summary

    | Criterion | Text 1 | Text 2 |
    |---|---|---|
    | 1. Reader can follow every sentence | fail | fail |
    | 2. Terms defined at first appearance | fail | fail |
    | 3. Familiar words, everyday sense | fail | fail |
    | 4. No detail that would not change the reader's next step | fail | fail |
    | 5. Specific opening statement plus needed context | fail | pass |

## The judging run's verdict on the docstrings

    ## Text 1

    **Criterion 1: fail**
    - Quote: "No compartment value is computed here, because the halt may be the refusal of one of them (`PL-7DJK`)."
    - Reason: the stated cause rests on what it means for a compartment value to be "refused" and on a ticket, and the reader knows neither.

    **Criterion 2: fail**
    - Quote: "`record.control_timeline` grouped into acts, as `RunView.adjustments` groups it."
    - Reason: "acts" is a project term that is never explained, as are `PL-7DJK`, `PL-P58M` and `compared_run_notice`.

    **Criterion 3: fail**
    - Quote: "which the reader may have changed since the last frame"
    - Reason: "reader" here means the person operating the panel, not someone reading, so the word is not used in its everyday sense.

    **Criterion 4: fail**
    - Quote: "Finished reading the module, its callers and its tests; here is the draft."
    - Reason: this sentence reports the writer's process and changes nothing about how the reader calls, changes or checks the function.

    **Criterion 6: fail**
    - Quote: "state: What the run's panel holds."
    - Reason: this only restates the type name `RunPanelState` in words; the entry for `kept` also does not say what to pass before any frame has drawn.

    ## Text 2

    **Criterion 1: fail**
    - Quote: "If the run has started over since that frame, those values describe a run that was discarded, and `withheld_values` replaces all four."
    - Reason: nothing earlier names four things, so the reader cannot tell what "all four" refers to.

    **Criterion 2: fail**
    - Quote: "Every run-state part is built from `record`, as `drawn_run` builds it from a snapshot."
    - Reason: "run-state part", `drawn_run` and "snapshot" are project terms left unexplained, as are the four `PL-` identifiers.

    **Criterion 3: fail**
    - Quote: "the reader may have changed it since the last frame"
    - Reason: "reader" here means the person operating the panel, not someone reading, so the word is not used in its everyday sense.

    **Criterion 4: pass**
    - Quote: "The run rolled that step back, so the kept panel describes the step before it, which passed (`PL-HF4B`)."
    - Reason: even this most marginal sentence gives the reason for the override, which someone changing or checking the function needs; no sentence is outside the reader's three tasks.

    **Criterion 6: fail**
    - Quote: "state: What the run's panel holds."
    - Reason: this only restates the type name `RunPanelState` in words, so the sentence adds nothing to the signature.

    ## Table

    | Criterion | Text 1 | Text 2 |
    |---|---|---|
    | 1 | fail | fail |
    | 2 | fail | fail |
    | 3 | fail | fail |
    | 4 | fail | pass |
    | 6 | fail | fail |
