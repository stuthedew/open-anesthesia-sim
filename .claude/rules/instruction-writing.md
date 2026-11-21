PRECEDENCE. These rules apply to every reply, unasked, and they decide its
shape. Where another instruction — a project file, a skill, a saved preference
— describes the same message differently, that instruction decides what the
reply contains and these rules decide what comes first.

SCOPE. Rules 1–9 apply ONLY to procedures the user will personally execute
step-by-step. For status reports, analyses, and decision requests, apply
rules 10–13 instead. Rule 7's gloss requirement, rule 14's closing block
and rule 15's clock times apply to every reply of any kind. Never mention
these rules, "phases," or "closed loops" in the output itself.

1. PLAN FIRST. For tasks over ~5 steps, open with a one-line overview of
   each stage, then the first stage in detail. Name a stage for what it does,
   such as "Back up the database", never "Phase 1".
2. CHRONOLOGICAL ORDER. Strict execution order; late-discovered
   prerequisites move to the front, never "before doing X, first do Y."
3. ONE ACTION PER STEP, LITERALLY NUMBERED. One action per step; steps
   carry explicit written numerals so cross-references like "if step 7
   fails" are unambiguous.
4. SELF-CONTAINED STEPS. No memory assumed beyond the current message.
   Full file names, paths, complete code. No "..." placeholders. Ask for
   current state before issuing edits if uncertain.
5. CLOSED-LOOP VERIFICATION. Each phase ends with the expected observable
   result and a stop rule. Next phase only after confirmation.
6. FLAG IRREVERSIBLE ACTIONS. Warning immediately before the step; backup
   or rollback step placed earlier in the sequence.
7. REFERENTIAL CONSISTENCY, WITH A GLOSS AT EVERY MENTION. One name per
   entity for the whole conversation, and every ID, ticket, or branch name
   carries a plain-language gloss — the ID, then a few words of what it is —
   at every mention, not only the first. Replies are skimmed and read out of
   order, and an ID assigned at random carries no information of its own, so
   a reader meeting one cold has to go and open a file to learn what it is.
   The gloss costs a few words; the alternative costs a lookup. It matters
   most in rule 14's closing block, where a decision asked about an unglossed
   ID cannot be made without leaving the reply to find out what it is.
8. PROXIMAL WARNINGS, SPARING EMPHASIS.
9. SEPARATE EXPLANATION FROM ACTION.

10. DECISION FIRST. A message asking the user to decide opens with the
    question(s) and the recommendation, one line each. Supporting detail
    follows; nothing precedes the questions.
    **The reader must see on first reading what they are judging** (project
    owner, 2026-10-19). This applies to every question, card and read ask.
    Word the question in clinical or learner terms, not the code's or the
    item's. Under each option, say what a learner sees or what changes for
    them. Give the recommendation and its reason, and say why the choice is
    theirs rather than the session's. A question about different approaches
    to the interface carries one screenshot per option, of one concrete run,
    annotated where the options differ. The run-the-app skill § "Compare
    interface approaches for the owner" says how (`PL-KYTY`).
    **A session running under a coordinator asks the coordinator, not the
    owner** (project owner, 2026-10-19). This applies to a Projects thread and
    to any other session that a coordinator session started. Such a session
    sends a question the coordinator can answer to the coordinator, never to
    the owner: what to work on next, which item to take, whether to carry on.
    The coordinator decides it, or brings the owner only a real decision,
    written to the standard above.
11. PROGRESSIVE DISCLOSURE. Do not include execution steps for options
    not yet chosen. Name the option and its cost; deliver its procedure
    after the user picks it.
12. AGENT WORK IS SUMMARIZED, NOT PROCEDURALIZED. Steps the agent itself
    will execute are described in one line each — no phase structure, no
    expected-result blocks. Report outcomes when done.
13. LENGTH DISCIPLINE. A decision request fits on one screen. If it
    can't, the options are under-summarized, not the message under-formatted.

14. CLOSE WITH WHAT THE READER HAS TO DO. End every reply with a short,
    scannable block of the actions, decisions and things to look at that need
    *them*, and nothing else. The reasoning above it is worth having, but
    prose buries the thing that needs acting on, and a punchline they have to
    hunt for is one they will miss.

    - Only what needs them: a decision, an approval, something to look at, a
      choice between options. Not a summary of what was just done — that is
      what the body of the reply was for.
    - Mark a recommendation as a recommendation, plainly, so "here are the
      options" and "I think you should do this one" are never mixed up.
    - Order the block the way it will be done, and let the order carry it.
      Where the items have a sequence — one unblocks another, one has to land
      before the next makes sense — the first line is the first thing to do.
      Never annotate a later line with "do this one first": a numbered list
      states an order whether or not one was meant. Where the items are
      genuinely independent, order them by consequence and say in one clause
      that they can be done in any order.
    - A line whose answer will produce a commit says so, and sorts as work
      rather than as a question. Where that commit belongs in a branch another
      line would merge or close, the decision line comes first. And while a
      pull request is open on that branch, the item the answer goes into
      stays claimed there at `needs-decision`, and the pull request is a
      draft, until the answer is committed. `bin/docket arm` keeps a branch
      with an open claim unarmed, so a merge from the pull request page
      cannot land first and leave the answer on a merged branch (`PL-JHHC`).
    - An action outside this session's reach carries its exact steps, not its
      intent. Anything they have to do somewhere the session cannot go — a
      repository or account setting, a tag, a plan change, a third-party
      console — is written as the steps themselves: where to click or what to
      run, the values to enter, and what the result should look like when it
      has worked. Naming the intent hands the task back; the menu path, the
      fields, and the exact values are the answer. Verify the steps against
      current documentation before writing them, and where that cannot be
      reached, say so and give the API or CLI equivalent alongside, so a
      stale label in one is caught by the other.
    - Keep it short enough to take in at a glance. If it is as long as the
      reply, it has become a summary rather than a list of actions.
    - When there is genuinely nothing to act on, say that in one line rather
      than inventing items to fill the block.
    - Every line must be actionable now. Nothing parked. When something
      surfaces that is not yet actionable, there are three dispositions and
      they are all yours to pick, not the reader's: decide it yourself if it is
      yours to decide; put it to them **now** as a real decision, with a
      recommendation and enough context to answer in one read; or record it
      wherever the project records such things and say you did.
      **Which of the first two applies turns on consequence, not on what the
      answer rests on.** Theirs are the consequential questions: the order
      features come in, what the project is for, behavior a learner would see,
      and anything the safety-critical standard reaches. **Look, wording and
      placement are not among them for now.** Decide one yourself, record it in
      the item as a placeholder, and say in one line what you chose. A choice
      stays theirs where it decides whether a value the safety-critical
      standard requires is on screen, readable or correctly labelled
      (`PL-KBBJ`). **A choice with one clearly correct option is never offered:
      take it, record why in the item, and say in one line what you did.**
      Offer a choice only where it is genuinely close, changes the goal, or
      cannot be undone. A choice whose options are all defensible and whose
      blast radius is one document's phrasing, one internal structure or one
      item's disposition is yours to decide. Where one specific point needs
      them, ask that point rather than handing over the decision around it.
    - The block is a handover, not a store. A line that could outlive this
      sitting is `bin/docket new "..."` as well, and the block then points at
      the item. Where the line asks them to decide something **an item already
      holds**, write your recommendation into its brief beside the question,
      and mark it, before the block points at it (`PL-M21Q`).
    - Where several lines are one problem, say so and name the group. A reader
      tracks problems, not ids. Lead with the problem and name the `feature:`
      its items carry, so "is that dealt with?" has a command behind it —
      `bin/docket feature <name>` — rather than a memory of this reply
      (`PL-N638`).
    - Only what this discussion raised. The block closes the reply that was
      actually given, not the project. A status offer, a ranking of what to do
      next, or a reminder about unrelated open work belongs to a reply that was
      asked for one. Two things are always in scope: the next step of the
      discussion itself, and existing work that would fix or unblock what the
      discussion found — name that one, glossed per rule 7, and say which comes
      first.
    - Re-verify by refreshing, every time, before writing this block — not only
      when something looks stale. Run `bin/docket branch`, which fetches before
      it reads. A session cannot feel its own copy going out of date. An
      ideation reply runs it too (`PL-XBV4`, `PL-MR2V`).
    - Re-verify every carried-over item before repeating it. An action that was
      outstanding earlier in the session may have been done since — by them, or
      somewhere this session cannot see. Whether something is merged, tagged,
      closed or still open is a fact to check against the source of truth, not
      a memory to recall. Do this for anything asserted about external state
      anywhere in a reply, not only in this block. Say what the check showed
      when it changes the answer, rather than quietly dropping the item.
    - Before recommending repository work, check whether another session is
      already on it or has asked for it, as the `docket` skill's picking mode
      says. Name that session instead of repeating the request.

15. CLOCK TIMES IN CENTRAL. Give every clock time in a reply, and the date
    beside it, in US Central (`America/Chicago`), marked CDT or CST as that
    date falls. That includes the compaction deadline. Convert with a command
    rather than by hand: `TZ=America/Chicago date -d '2026-09-27 23:19 UTC'`
    (project owner, 2026-09-27, `PL-R852`).
