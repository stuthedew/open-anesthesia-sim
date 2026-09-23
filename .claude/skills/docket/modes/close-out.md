# docket: close-out

Read this when an item's work is done: the closure commit, the docs sweep, the
gate report and the `--self` audit.

Part of the `docket` skill. `.claude/skills/docket/SKILL.md` is its front
page and decides which file a session reads.

## Mode: close out an item

1. Set `status: done` and `closed` - `bin/docket set <id> --status done
   --closed DATE` - and commit that **with the work, in one commit**, whose
   subject leads with **every** id it closes, comma-separated -
   the recovery below reads the newest subject naming an id, so a rider closed
   under another item's id alone is attributed to its own capture commit
   (`PL-GW37`). **Do not write `commit:`** - the field is retired (`PL-T63T`),
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

   **Leave `pr` empty; it is written after the merge, by command.** The number
   cannot be known before the pull request is open, and `docket check` owes a
   `pr` only on a closure that already stands on the default base — so an
   unlanded closure carrying none is the expected shape rather than an error.
   **Do not split the closure out to get the number earlier** — pushing the
   work first and adding the `pr` before the merge reopens the very window
   below, and the merge can arrive between the two pushes. Closing in the same
   commit as the work is what removes that
   window: requiring the number up front forced the closure into a second
   push, and a merge inside it took the work and left the closure on the
   branch — `main` had the fix while the queue still called the item open and
   a debt gate still counted it (`PL-D2GW`, then `PL-P5S0`).

   **`bin/docket record` writes it, and `make fix` runs that.** Bare, with no
   number: it writes every `pr` the base is owed and can supply, which is the
   same reading `docket check` prints the advisory from. **Never edit the field
   by hand** — the command refuses to overwrite a different number, and typing
   the line is how the wrong one gets recorded and how two sessions opened
   `#229` and `#230` for one identical insertion (`PL-QTSB`). Let the write
   ride a commit you are already making; do not compose one for it, and do not
   open a pull request for it alone. Where a number exists that the base cannot
   name — a squash subject that led with no id — `bin/docket record NUMBER
   --merge MERGE_COMMIT` is the explicit form.

   No in-flight guard is owed before running it, unlike every other path that
   edits an item someone else may hold. `PL-QTSB`'s harm was two *pull
   requests* for one insertion (`#229`, `#230`), and there is no pull request
   here: two sessions that both run it write the same tool-dictated line and
   git merges them. Asking each to fetch and check first would be friction
   that changes no outcome.

   The advisory is still an *error* where no commit on the base names a number
   at all **and** the checkout says it is complete, which is provenance
   genuinely lost; a truncated checkout declines instead, because the commit
   may be outside it (`PL-99Y4`).

   **Act on what that command prints about the items you just unblocked.** It
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

   **Two of the four take an exemption the *item* declares, and a session
   cannot declare one for itself mid-work.** Both turn on the base's copy of
   the item rather than on your branch, so adding either beside the work it
   would excuse folds nothing and is reported as your own word for it.

   - `falsifies:` names enough of an assertion to identify the one subject the
     item's work makes untrue - the string it pins is what the item was asked
     to delete, so no arrangement of the tests keeps it. A matching removal
     folds and is printed beside the check (`PL-K82G`). **One item cannot
     declare it in advance, and declares it in the closure instead** - see the
     `needs-decision` exception below (`PL-ZMGR`).
   - A `dropped` item, or one carrying `not-delegable:`, has no command to run,
     and the check says which applies rather than stopping the audit dead
     (`PL-L4KX`).

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
   *merged*, and the window shuts at this branch's first commit. Writing the
   line now folds nothing and is reported as your own word for it, whatever
   the brief says. So the prescription lives where the pass that can act on it
   reads it - `.claude/skills/docket/modes/triage.md` § "`falsifies:`, and why
   triage is the only pass that can write it" - and here the `REJECT` is
   expected, with reporting it the whole of what is owed.

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
