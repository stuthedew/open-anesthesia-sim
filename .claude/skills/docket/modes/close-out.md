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
   the commit-and-push rule requires no later than the first push of work. Run
   it after `bin/docket set --status done` and before the closure commit, and
   the number rides the same commit as the work. It writes onto every closure
   this checkout introduces, committed or not, and onto nothing the base
   already holds as done; `make check` then reads the committed tree through
   `tools/pr_record_check.py --discover`, and CI's required `pr-title` job
   refuses the pull request until every closure records its number
   (`PL-HMZZ`). **Never edit the field by hand** - typing the line is how the
   wrong number gets recorded (`PL-QTSB`). Where the pull request opens only
   after the closure was pushed, run the command then: the number rides one
   more push, and the red check is what holds the merge until it lands, so
   the window below stays shut.

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

   **Record the body too, with `python3 tools/pr_body_check.py --record`,
   once the pull request is open**, committing the file it writes with the
   `bin/docket record N` write where there is one, and again after any later
   edit to the body: `pr-title` holds the merge until the head's
   `docs/pr-bodies/<N>.md` holds the body GitHub has (`PL-979D`).

   **Act on what `bin/docket set --status done` prints about the items you
   just unblocked.** It
   names the items whose last recorded blocker this closure clears - the
   reverse of `blocked-by`, derived rather than stored. Do not defer them to a
   grooming pass: you are holding the context the judgment needs, and the pass
   is what this replaced. Read each against the tree and either `bin/docket set
   <id> --status ready` or write what is really holding it into `blocked-by`,
   in this branch's commit. Of 13 items reached this way across the two passes
   that preceded the print, 6 were genuinely startable and the rest were
   already done inside another item, held by a condition nobody had declared,
   or carrying a user-facing question written in since triage - so the reading
   is a candidate list and never a verdict, which is why nothing promotes them
   for you (`PL-PQC7`, `PL-6T44`).

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
   clears itself. When the gate does not contain the item — a tooling fix, a
   docs pass, anything captured after the freeze — end without a gate report:
   the remaining entries are all simulator work, and listing them at the end of
   a process session is product work arriving in a discussion that was not
   about it.
5. **Audit the branch: `bin/docket verify --self <id>`**, naming every id the
   closing commit leads with, since the diff is selected per id from the
   commits that name it. It runs the item's own `verify:` command and `make
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
   stay absolute: no suppression added, no assertion removed, the item's own
   command passes, `make check` passes. A session may re-scope its own
   commission; it may not weaken what measures it, and it may not skip the
   test.

   **Two of the four take an exemption the *item* declares, and which copy
   of the item each field is read from - the base's or your branch's - follows
   one rule, stated on `Commission` in `subprojects/docket/src/docket/verify.py`
   (`PL-B8HZ`).** An *outcome* (`status`, `closed`, `reason`, `pr`) is your
   branch's and excuses nothing. A *prediction* (`verify:`, `touches:`) is
   measured against the base's copy, and your branch's copy is a correction of
   it: honoured, and printed beside the base's with the base's own result. A
   *waiver* (`falsifies:`, `not-delegable:`) removes a refusal and is the
   base's alone, so adding one beside the work it would excuse waives nothing
   and is reported as your own word for it.

   - `verify:` is a prediction, and rewriting it is a correction the audit
     honours and prints: where the base's copy commissions a different
     command, both run, yours decides the check, and the report carries
     ``commissioned: `A` - fails on this tree (exit 1); this branch runs `B`
     instead`` under it. A rewritten command is never silent, so say in the
     reply why the commissioned one was wrong - that line is what a reviewer
     will ask about (`PL-PZ6T`). `touches:` is read the same way: the diff is
     measured against the base's, and a path only your own widening declares
     is named as that in the NOTE.
   - `falsifies:` names enough of an assertion to identify the one subject the
     item's work makes untrue - the string it pins is what the item was asked
     to delete, so no arrangement of the tests keeps it. A matching removal
     folds and is printed beside the check (`PL-K82G`). **One item cannot
     declare it in advance, and declares it in the closure instead** - see the
     `needs-decision` exception below (`PL-ZMGR`).
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
   owner with the check's own words, and do not add the declaration to the item
   on this branch to clear it. The whole worth of the field is that a reviewer
   wrote it first.

   **One exception, and it is the only one: a `needs-decision` item whose
   answer turned out to be "delete this".** A reviewer could not have written
   `falsifies:` first, because which assertions the answer makes untrue depends
   on the answer and the answer was yours to make. So where the *base's* copy
   reads `status: needs-decision` and this branch is the one closing the item,
   the closure's own declaration is honoured: `bin/docket set <id> --falsifies
   '<enough of the assertion to identify it>'` in the same commit that sets
   `status: done`. The check prints that the declaration is the closure's own
   and that the base is what let it be, so nothing folds quietly, and the gate
   is not yours to set - on a `ready` item the identical line folds nothing and
   is reported as your own word for it, exactly as above. `PL-G6J5` is the
   instance: an advisory retired on a count, whose close-out printed `FAIL no
   existing assertion removed - 29 line(s)` with `make check` green and every
   other guard passing (`PL-ZMGR`).

   **One class of item reaches that `REJECT` every time, and the case is
   settled - do not re-derive it** (`PL-K4R5`). Where the deliverable *is* a
   changed output string, the test pinning the old one must change, and the
   old string is then simply gone: nothing in the diff separates the
   commissioned rewrite from an expectation quietly dropped. The check prints
   the removed assertion under its test function, beside every assertion that
   arrived there, and pairs none of them. Report the `REJECT` with those lines
   and say which arrival is the rewrite - that is the reading the tool refuses
   to guess at, and it is one line rather than a reconstruction. Since
   `PL-4W2L` the same holds for any existing assertion changed in place, a call
   site gaining an argument included: the check reads statements, refuses the
   change and prints both sides, where it used to fold an insertion unasked.

   Three ways out were measured over 502 single-id close-outs, in which 57
   would `REJECT` this check and 20 are this shape, and all three failed:
   folding on the pairing reaches a wrong answer, since 15 of the 20 have more
   than one candidate and `PL-FCM3` has six; keying the fold to the
   commission's own `verify:` string explains 1 of 20; and having triage copy
   the old string out of the brief reaches 3 of 20, because the string is
   usually not in the item. `falsifies:` itself stands at **0 of 1,503**
   items on 2026-09-22 - written once into the tool in `v0.4.27` and never onto
   an item.

   **Nothing in that is this session's to repair, and the one case that works
   is not reachable from here** (`PL-YZJD`). The case is real - the item's own
   brief already quotes the old string, as `PL-FCM3`'s title did, and then
   `bin/docket set <id> --falsifies '<the quoted string>'` makes the close-out
   fold. But "at triage" is a precondition rather than a turn of phrase: the
   check reads the base's copy, so the declaration counts only once it has
   *merged*. Writing the line on this branch folds nothing and is reported as
   your own word for it, whatever the brief says. So the prescription lives
   where the pass that can act on it cheaply reads it -
   `.claude/skills/docket/modes/triage.md` § "`falsifies:`, and why triage is
   the only pass that can write it" - and here the `REJECT` is expected, with
   reporting it the whole of what is owed unless the round trip below is worth
   its cost.

   **A waiver is amended where the commission lives, so a mid-work discovery
   has a route, and so does an item captured and closed on one branch**
   (`PL-TKFD`; project owner, 2026-09-25, ratified, over accepting a
   declaration committed to the branch before the removing commit, and over
   leaving the `REJECT` to carry the conversation). Neither needs a mechanism:

   - **A `ready` item whose work turns out mid-way to falsify an assertion.**
     Declare it on the base: from `origin/main`, an item-only branch carrying
     `bin/docket set <id> --falsifies '<enough of the assertion to identify
     it>'`, which `CLAUDE.md`'s capture rule opens a pull request for at its
     first push - `bin/docket arm` answers `arm`, since the change lies under
     the store and no claim is bound to that branch. Once it merges, bring
     `main` into the work branch and re-audit: `verify --self` reads the
     declaration from the base. On a solo project this buys visibility and
     order rather than a second author - the declaration is a commit of its
     own on `main`, ahead of the work - and that is all that is claimed for it.
   - **An item captured and closed on one branch.** The same route in its
     natural order: capture on its own branch with the declaration, let it
     merge, and work from the merged base. A declaration written on the
     capturing branch is still refused (`PL-ZMGR`), because the assertion it
     would waive is in the base tree whether or not the base holds the item.

   Both are the ordering the field always asked for - declare before the
   commit that removes the assertion - made concrete on the base instead of on
   the branch. Sized by `PL-YZJD`'s count, about 2 folds in 502 close-outs, the
   round trip is paid rarely; honouring the branch's waiver instead was refused
   because a wrong waiver switches an integrity check off.

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
   Both refutations that mattered on `#784` were empirical. A fourth candidate
   - that per-run holder widgets cost the plots 18 px of layout spacing -
   read as obviously true and measured **0 px** at two window sizes, and would
   have been filed on argument alone. Conversely the three that were real were
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
