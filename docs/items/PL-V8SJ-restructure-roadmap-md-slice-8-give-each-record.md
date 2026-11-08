---
id: PL-V8SJ
title: Restructure ROADMAP.md, slice 8: give each record of the milestones v0.1.0 to v0.5.0 one home in its own section, apart from v0.5.0's gate dispositions
priority: P2
effort: L
status: ready
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
blocked-by: PL-M3MV
added: 2026-11-07
payoff: a reader checking why v0.1.0 to v0.5.0 took the shape they did finds each record once, in that milestone's own section, and the copies that disagree with an outcome are gone
verify: ! grep -qF 'recorded so it is not re-litigated' ROADMAP.md
---

**Problem.** Restructure ROADMAP.md, slice 8: give each record of the milestones v0.1.0 to v0.5.0 one home in its own section, apart from v0.5.0's gate dispositions

**Source.** The copy editor's structure read of `ROADMAP.md`, run on the project owner's Mac on 2026-11-06: one read per chapter, then one read of all the chapters' outlines together. Row numbers are `ROADMAP.md` at `aff76df1`, the last commit to change it before slice 1 (`PL-W0TS`), so a later slice finds each passage by the words the finding quotes. The project owner chose to file the findings as items and apply them one slice per pull request (project owner, 2026-11-07, ratified, over one pull request for the whole restructure), because the release tools read the roadmap's gate sections and a small move is easier to check against them. The raw reads are in the project's shared folder, `/mnt/project-files/v0.7.0/repo-copy-edit/mac-structure-reads/ROADMAP-md/structure/`.

**Why it matters.** The records of the Qt port, the port's move ahead of v0.5.0, `PL-011`, `PL-NGF7` and the Flet format callables are each given in two to five places, and the `PL-NGF7` copies disagree with its outcome. A reader checking why a milestone took the shape it did should find one record, in that milestone's section.

**The findings, as the outline read gave them** (numbered by their order in the read: 27, 28, 30, 43, 44).

- The Qt port and the interface pass: "app/theme.py changed by 10 insertions and 29 deletions ... No palette entry, type size, padding or radius has moved since 2026-09-10" (446), "changed app/theme.py by 10 insertions and 29 deletions ... No palette entry, type size, padding or radius changed" (1773-1781) and "it changed no palette entry, type size, padding or radius" (9007-9025). The placement history appears at 452, 1766-1800, 1911-1917 and 8969-9005. The measurement belongs in § "Completed: v0.4.26" (1773-1781). Item 33 keeps its placement and one sentence, and the timeline rows keep their dates.
- The port moved ahead of v0.5.0: "Of v0.5.0's eight open ids, one was wholly inside the port (PL-8PSW), two partly, and five not at all" (446) and "v0.5.0 has 8 open Required-scope ids: 1 wholly ..., 2 with a slice ..., 5 never touch it" (1632-1649). The grounds appear at 446, 1651-1670, 2137-2143 and 3301-3312. Row 446 also gives "a patch number for a 5 133-line rewrite ... It keeps a section", which 1678-1702 gives too. All of this belongs in § "Completed: v0.4.26". The timeline row keeps the date, and § "Completed: v0.5.0" (2124-2143) keeps one sentence and a pointer.
- PL-011 and the score architecture: "Dropped 2026-09-05, superseded by PL-T691 and PL-2FM6" (444) repeats 1501-1529, and 443, 447, 5235-5245 and 5280-5282 also give it. "Score architecture placed here (project owner, 2026-09-05)" (447) is also given at 444, 5224-5233 and 8587-8599. PL-011 belongs in v0.4.0's Required scope (1501-1529), and the score architecture belongs in v0.5.0's (5224-5233). The timeline rows keep contents and size, and item 29's paragraph (8587-8599) can go.
- PL-NGF7: "The port dissolves PL-NGF7" (1918-1937, also 2045-2049) and "dissolved by the port; clears before v0.5.0 as dropped" (3318, also 3413-3414) disagree with the outcome. The outcome is "The item closed done in v0.4.26 (#621)" (3275-3280), and 9027-9040 adds "the Qt port did not dissolve it as the deferral predicted". The outcome belongs at 3275-3280. The other places say "closed done in v0.4.26" or point there.
- PL-16ZC, PL-YVHK, PL-GS3R and PL-2K1R: "about 1 870 per-point strings on Flet against one format callable" (1866-1876) and "roughly 1 870 per-point strings ... one format callable" (3396-3411). The other dispositions are argued at 2000-2024 and again at 2811-2842 and 3316-3440. They belong in § "Completed: v0.4.26", where they were decided. § "Sequenced past v0.5.0" keeps its table, which 3374-3380 calls the index, and the gate entries keep one line each.

**Queries filed separately.** `PL-392N` (a control timeline's size, 140 KiB against 70 KiB) and `PL-T5R7` (`PL-Y5WR`'s 30-day cap against the 24-hour cap). v0.5.0's gate dispositions, rows 3221-5219, are slice 9 (`PL-4BCF`).

**The findings inside each chapter, as the chapter reads gave them.** Each chapter read also ended with an outline of one line per paragraph, which is left out here and kept in the shared folder. Each read is quoted whole, as a block, so that its quotations of the roadmap are not taken for this item's own claims.

**Chapter read 6: § "Completed: v0.1.0 - first patient sevo model", rows 513-589.**

```text
- One fact appears in three places. Row 517 says "Extend the existing circuit model", row 531 says "Keep the v0.0.2 circuit model and its analytic regression tests", and row 560 says "the v0.0.2 circuit reference behavior remains unchanged". Rows 531 and 560 state the same requirement. It belongs in Definition of done (560) as a pass condition. Required scope keeps nothing, because the Goal already says the model extends the existing circuit model. If the reader needs "analytic regression tests", the section edit can fold it into 560.
- Row 546 says "so that mass balance can be checked within a documented numerical tolerance", and row 566 says "total sevoflurane mass closes within the stated tolerance". The tolerance belongs in Definition of done (566). The scope entry (544-546) keeps the tracking of agent delivered, exhausted and stored, and ends at "so that mass balance can be checked".
- Row 527 says "while preserving deterministic behavior and explicit units", and row 547 says "Preserve explicit simulation time, deterministic results". Determinism belongs in Required scope (547), which can take "explicit units" as well. The Goal paragraph (525-527) then ends at "washout". Row 567 is the pass condition for determinism and stays.
- Order: put "### Explicitly out of scope for v0.1.0" (576-589) straight after "### Required scope" (529-552), before "### Definition of done" (554-574). There are two reasons:
  - This reader decides what a release holds and what it leaves out, and those two lists answer that together.
  - The last criterion of Definition of done (570) mentions "deferred feature" before the reader has seen what was deferred. After the move it points back to a list they have already read.
  
  The section edit should then use one name, "out of scope" or "deferred", for both. If the other milestone chapters use the same order, change them all so they stay parallel. The outline read can confirm this.
- Two passages are written for a developer, which the section edit can fix in place:
  - Rows 558-559 list Ruff, strict mypy, pytest and GitHub Actions. The owner's row does not say they know these tools. The roadmap needs only what passing guarantees: formatting, lint, type and test checks all pass on the locked Python 3.14 setup. The tool list belongs in the item.
  - Row 548 names "Flet" without saying it is the interface library.
- Query: row 546 says "a documented numerical tolerance" and row 566 says "the stated tolerance". The chapter gives no tolerance value and names no place that gives one. Rows 564 ("documented reference scenarios") and 565 ("supported step sizes") have the same gap. The reader needs at least a pointer to where each is stated, and the chapter does not give one.
- The headings say what their sections hold. At 475 words with four subheadings, the chapter is easy to find one's way in.
```

**Chapter read 7: § "Completed: v0.2.0 - isoflurane and desflurane", rows 591-676.**

```text
- **Said twice: governing equations.** "No governing equation changes in this milestone" (599-600) also appears as the out-of-scope entry "Any change to the v0.1.0 governing equations themselves. This milestone proves that the equations are agent-generic. It does not change them from one agent to another." (664-666), and again as "even though they do not change the governing equations" (622-623). The fact belongs in the out-of-scope list, which is where this reader looks for what the release left out. That entry keeps only its first sentence, because "proves that the equations are agent-generic" repeats the Goal (595-597). The Goal keeps "It adds only new per-agent data and the loading capability to select among agents" (600-601). The clause in 622-623 goes.
- **Said twice: the Goal's aim.** "This milestone only needs the model to be able to run as isoflurane or desflurane. It does not need to offer that choice in the interface yet." (646-648) repeats the Goal (597-601). The entry keeps the exclusion and its pointer to item 1. The repeated aim goes.
- **Said twice: Required scope and Definition of done.** The two lists give four facts twice:
  - schema validation: "schema-validated like `data/agents/sevoflurane.json`" (605-607) and "pass the same schema and range validation as `sevoflurane.json`" (631-632);
  - independent reference tests: 616-619 and 633-635, with the Goal's "each with independent reference cases" (599) as a third copy;
  - keeping the old reference tests unchanged: "Preserve the v0.0.2 circuit and v0.1.0 sevoflurane reference tests unchanged" (624-625) and 636-637;
  - parameter sources in `docs/MODEL.md`: 620 and 638.

  Each criterion belongs once, in Definition of done. Each Required scope entry keeps only what it adds:
  - the two new files with cited blood:gas and tissue:gas partition coefficients (605-607);
  - choosing an agent by id (608-609);
  - wash-in, uptake, washout and equilibrium (616-618);
  - the agent-specific numerical points (621-623).

  The entry at 624-625 goes, and so does the first sentence at 620.
- **Wrong place and wrong heading: the outcome paragraph.** The paragraph saying what was done (668-676) sits under "### Explicitly out of scope for v0.2.0", a heading that does not say what the paragraph holds. The reader of a completed milestone looks first for whether it was delivered and what it delivered. The paragraph belongs under its own subheading, such as "### Outcome", directly after § "Goal". Its first sentence, "All the criteria above were met when the milestone was tagged", can stand as the lead of Definition of done in place of "v0.2.0 is complete only when all of the following are true:" (629). That lead is written as a plan, for a milestone that is now complete.
- **Another reader's: code detail.** These rows are written for a developer or a later session, not for a reader deciding what a release holds:
  - 609-615: `core/parameters.py`, `load_sevoflurane_parameters()`, `RespiratorySystem.default()`, the `_require_*` helpers, and the Pydantic suggestion with its reasons;
  - 619: `tests/reference/test_sevo_patient.py`;
  - 669-673: `load_agent_parameters(agent_id)`, "thin wrapper", and `tests/reference/test_multi_agent.py`.

  This reader doesn't know these internal names. The detail belongs in the item for this milestone, or in its commit messages. This section keeps three points: an agent can be chosen by id (608-609), existing sevoflurane runs behave as before (671-672), and reference tests check directional solubility and mass-balance closure for both new agents (672-673).
- **Wrong place: work done after the milestone.** "A basic picker was in fact added afterwards, in commit `00791b1`. The picker restarts the run rather than switching agents mid-run. So the interlock and residual-washout work that this milestone excluded is still outstanding." (649-652) is the current state of planned work. The reader deciding what to build next looks for it in § "Planned milestones" item 1, the anesthesia-machine milestone. It belongs there. The outline read should check whether item 1 already says it. This entry keeps the exclusion and its pointer (644-646). The commit hash goes to the item. "(This was recorded as the milestone's scope when it was tagged." (648-649) describes the text itself and goes.
- **Wrong place: advice on sourcing other agents.** "Halothane is clinically obsolete, but it has reasonable modern published data. Enflurane, ether, and xenon are harder to source ... None of the three should be assumed available just because the Gas Man reference simulator shows it." (657-661) is advice for whoever plans to add those agents. It belongs with that stretch goal. This entry keeps the exclusion (656-657).
- **Order.** Goal, Required scope, Definition of done, Out of scope, then the outcome means the reader reads the whole plan before learning what was delivered. Use: Goal, Outcome, Required scope, Definition of done, Explicitly out of scope. That is the move in the outcome-paragraph finding above.
- **Length.** The section has subheadings for each part and needs no more beyond "### Outcome".
- Query: the Required scope entry suggests moving the loading code's JSON validation to Pydantic (611-615). No place says whether this was done, dropped or is still open. If it is still open, it belongs in an item or a planned milestone.
- Query: Required scope asks for equilibrium tests (617-618) and a note on agent-specific numerical points such as desflurane's low blood:gas solubility (621-623). Neither Definition of done nor the outcome paragraph says whether these were delivered.
- Query: the entry excluding vaporizer physics (653-655) does not say where, if anywhere, that work is planned. The agent-switching entry (645-646) and the nitrous oxide entry (663) both say where theirs is.
- Query: the entry for halothane, enflurane, ether and xenon calls them "a stretch goal further in the future" (656-657) but names no milestone or item that records that goal.
- Query: "`load_sevoflurane_parameters()` is currently the only path that `RespiratorySystem.default()` uses, and it is hardcoded" (610-611) describes the code before the milestone. The outcome paragraph (669-672) says agents now load through a new path. The reader cannot tell whether the default still loads only sevoflurane.
- Query: the section names no item for this milestone. Its decision history and code detail need one to move to.
- Query: "within the documented tolerance" (634-635) does not say where that tolerance is documented.
```

**Chapter read 8: § "Completed: v0.2.8 - the workflow works", rows 678-1074.**

```text
- **Repeat: the list of machinery.** 684-686 lists "the merge path, the release script, the queue's ranking, the session-start digest, the type-check and lint gates, and the instructions that a session reads before it does anything else". 955-958 gives the same list again, and 842 says "one of the six pieces of machinery the goal names". Keep the list in § "Goal". At 955-958, keep only "the machinery the goal names".
- **Repeat: the simulator is untouched.** Five places say it: 686-687 "None of this work touches the simulator"; 700-701 "adds nothing to the simulator. It changes no equation, parameter, numerical method, unit or displayed value"; 981-982 "which this release does not touch"; 1035-1036 "No equation, parameter, numerical method, unit or displayed value has changed"; and 1065-1068 "Any simulator change at all". Keep one sentence in § "Goal" (686-687). Keep only "crosses no capability boundary" at 700-701. Keep the testable condition in § "Definition of done" (1035-1042) and the paths in § "Explicitly out of scope for v0.2.8" (1065-1068). At 981-982, keep only where those findings go.
- **Repeat: what "new scope" means.** 937-938 says "new behavior, new capability, or another workflow idea raised while this release runs". 963-965 says "a new workflow capability, a better tool that nobody is blocked by, or an idea someone had". 1069-1070 says "new tools, better tools, or an idea this release made someone think of". Merge 937-938 into 963-965 as the one definition. The out-of-scope bullet keeps a pointer and the fact that the queue holds more process items, which wait for the next release (1070-1072). Cut 1072-1073 ("The scope test admits a defect in machinery that the goal already names"), which repeats 966-967 and 973-975.
- **Repeat: the four entries added under the completion rule.** 985-988 lists PL-J295, PL-KWC1, PL-XCYB and PL-WFJ9. Each of those entries already says "Added after the freeze because it completes …" (757, 765, 876, 883). Cut 985-988. The entries keep the fact.
- **Repeat: why PL-XCYB was added.** The entry at 875-879 ("completes PL-ZQ9C … the check as specified reports sound provenance as broken") and the paragraph at 990-997 ("fails loudly against correct data … Shipping PL-ZQ9C without PL-XCYB would close an entry that was known to be half-fixed") make the same point. The entry keeps the problem. How it was found goes to item PL-XCYB. The paragraph keeps nothing.
- **Repeat: why PL-WFJ9 was added.** The entry at 880-885 ("the widened gate passes over the digest and `status` outputs … completes PL-020") and the paragraph at 999-1007 make the same point. The entry keeps it, and the paragraph keeps nothing.
- **Repeat: why entries are `not-delegable`.** 926-934 gives every reason. 1030-1034 repeats one ("No command in this repository can verify either of them, which is why both are marked `not-delegable`"), and so does 844-846 ("marked `not-delegable` only because confirming it means ending a session"). The reasons belong in 926-934. § "Definition of done" keeps "confirmed in effect on a real pull request". The PL-1Q3S entry keeps nothing.
- **Repeat: the closed and open count.** 727-730 ("`bin/docket wave` checks these entries against `docs/items/` and reports how many are closed") and 1026-1027 ("`bin/docket wave` reports the split against `docs/items/`") say the same thing. Keep it in § "Definition of done". Cut 727-731, which also points to "the reason given in the v0.4.0 section" and then gives that reason anyway.
- **Repeat: where Gate 0 is recorded.** 724 says "Gate 0 is still recorded under v0.4.0 below" and 1062 says "which is recorded under v0.4.0 below". Keep 724. 1062 keeps only "Anything on Gate 0's frozen list".
- **Repeat: the four flaws in one function.** 798-804 retells the closes of PL-CPSY and PL-MGNC, which their own entries give at 793-795 and 821-825. 811-815 retells PL-S1P1, PL-MGNC and PL-KWC1. "Six readers" appears at both 807 and 836. Each entry keeps its own problem and close. The story across entries goes to the items.
- **Overlap: a needed change to a modelled value goes to Gate 0.** 981-982 and 1040-1042 both route such a change to Gate 0. Keep the rule at 981-982. 1040-1042 keeps only that such a change is not this release's work.
- **Another reader's: why the list sits under "Debt gate".** 719-723 explains it: `bin/docket wave` reads that subsection, and the passage on the "beat" follows from it. That explains how a tool works and belongs in item PL-NSN9 or a comment in the tool. This reader keeps the rest of 715-725: the list is not a gate, the first group is debt, the second is new capability, and Gate 0 still binds v0.4.0.
- **Another reader's: the documentation check enforces the counts.** At 734-735, "`tools/doc_check.py` enforces that those three statements match the entries" is a rule for writers and belongs in item PL-H8MQ. This reader keeps only that the group headings give the list's size.
- **Another reader's, and in the wrong section: which counts the check verifies.** The note at 1044-1058 explains which counts the check verifies and why a check built on `touches:` would fail. It is reasoning about a tool, it serves a writer, and it says nothing about when the release is done. Move all of it to `PL-GLBF` and leave nothing here.
- **Decision history.** 948-949 ("When the section was first written, this paragraph said the opposite, and it was wrong") and 967-971 ("This paragraph used to offer only two cases … On 2026-08-31, nine findings were triaged") record how the rules came about. That history belongs in an item, but neither decision tag, at 936 or 951, names one. See the queries.
- **Decision history: PL-68XK.** 1009-1022 belongs in items PL-68XK and PL-T63T. Keep one sentence: PL-68XK predates the freeze, was left off the approved list on purpose, and was dropped when PL-T63T retired the `commit:` field. The PL-HDY6 entry relies on this paragraph (851-852), so that sentence must stay.
- **List entries grown into essays (pattern 5).** Many entries carry admission reasoning, details of how the fix was built (`in_flight_ids`, `FlightReport`, the commit walk) and links to other entries: 755-761, 762-768, 769-777, 778-784, 796-807, 808-815, 816-825, 826-831, 832-837, 838-846, 847-855, 899-904, 905-910 and 911-917. For this reader, cut each entry to one line on the problem, plus how and when it was admitted and how it closed. The reasoning goes to each named item. The entries are also written for a developer: they use code and tool names this reader does not know, such as `render.py`, `[tool.mypy] files`, `warn_unused_ignores`, RUF100 and `docket flight`. The sentence edit should fix those.
- **Rules that may belong in another section.** The membership rules at 936-983 read as rules for any frozen list. 945-947 calls them "the correct reading of" a general section. A reader deciding what a future release holds would look for them in "The gate is a snapshot, not a moving target" or "What counts". If they apply beyond v0.2.8, move them there and leave a pointer (see the queries).
- **Order: the rules come after the list that uses them.** From 757 on, entries cite "the scope test" and "the rule beneath this list", but those rules come only after 38 entries (936-983). 985-988 sits apart from the completion rule (936-949) and says "The scope test is described below this rule", although the scope test (951-979) now sits above it. Use this order:
  1. 707-713, the freeze;
  2. 919-924, approved items that are not entries;
  3. 936-943 merged with 951-979, the membership rules, then 981-983;
  4. 715-725, what the two groups are;
  5. the two groups;
  6. 926-934, the `not-delegable` entries;
  7. the one PL-68XK sentence.
- **Planning tense in a completed release.** Several rows still speak to someone planning the work:
  - 926-927, "worth knowing before the work is planned";
  - 855, "the item carries both candidate rules and what each costs";
  - 903-904, "the first to drop if this list needs shortening";
  - 996-997, "worked together and closed together";
  - 1007, "worked with PL-020 rather than behind it";
  - 727-731, "goes stale the next time an item closes".

  Rewrite them as outcomes (see the query on outcomes).
- **Section too long.** § "Debt gate: the frozen list" (705-1022, about 3,000 words) needs subheadings:
  - "What the list admits" before the rules;
  - "Entries" before the two groups, which already have labels;
  - "Entries that need the project owner" before 926-934;
  - "Items left off the list" for 919-924 and the PL-68XK sentence.
- **Heading that does not fit.** "Debt gate: the frozen list" (705) does not say what the section holds: 715-719 says the list is not a gate and half its entries are not debt. A tool reads this heading (720), so renaming it means changing the tool too. Query the owner. If renamed, "The frozen list of entries" would fit.
- **Section references.** 716 ("the section "What counts"") and 946 ("The gate is a snapshot, not a moving target") do not use the § "Heading" form, so the documentation check may not find them.
- **For the outline read.** 693 gives Gate 0's size ("twenty entries of inherited product debt"), and 1062-1064 says v0.3.0 clears Gate 0. The v0.4.0 chapter probably gives both facts too.
- Query: The reader needs each entry's outcome, done or dropped with its reason, and the text does not give it. 712-713 says "Each entry records its own outcome when it closes", 1026 allows "`dropped` with its reason recorded", and 1056 says "every id on it is closed". Yet only PL-1CYR, PL-CPSY, PL-S1P1 and PL-MGNC record a close. Also missing: which rule PL-HDY6 chose (855), PL-CMCB's verdict (933-934) and PL-ZQ9C's migration choice (929-930).
- Query: The reader needs the date v0.2.8 shipped, and the chapter does not give it.
- Query: 986-987 says "The rest were added under the scope test", but PL-1CYR was added "at the project owner's direction rather than under the completion rule" as new scope (771-772, and 710). Only the author knows which is right.
- Query: 988 says "The scope test is described below this rule", but the scope test (951-979) sits above 985.
- Query: 849 says "after the four above" and 917 says "the four of 2026-09-01". The list shows six entries admitted on 2026-09-01: PL-3576, PL-1Q3S, PL-HDY6, PL-QDH7, PL-RWZV and PL-H8MQ. Which four are meant?
- Query: At 902, "The weakest of the seven": seven of what? Perhaps the seven defects among the nine findings at 969-970, but the PL-CMCB entry does not say it came from that triage.
- Query: 1055-1056 gives "This list is frozen" as the reason no count can drift, but 707-708 says entries kept being admitted after the freeze. The real reason seems to be that every entry is closed.
- Query: The decision tags "(project owner, 2026-08-30)" (936) and "(project owner, 2026-08-31)" (951) name no item. Name the item that should hold their history (945-949, 967-971).
- Query: Do the rules at 936-983 apply only to v0.2.8, or to every frozen list?
- Query: If subheadings are added, does `bin/docket wave` still read entries under them (715-720)?
- Query: This chapter does not explain these terms: "beat" (722, 786), "cadence" (713, 715), "parse floor" (896), "grandfathered items" (749), "Gate 0's minor-version exception" (702), "captures" (830, 909) and "groom" (834). It also uses tool names the reader does not know: `docket next`, `docket flight`, `docket check` and `bin/docket wave`. Say what each means, or point to the section that does.
```

**Chapter read 9: § "Completed: v0.3.0 - the foundation", rows 1076-1123.**

```text
- **Rows 1086-1087, 1099-1100 and 1112-1113 state what the release covers three times.**
  - The three statements are "Its contents are exactly Gate 0's items that fall outside the teachable case's own scope", "Every item on Gate 0's frozen list that is outside the v0.4.0 milestone's Required scope is `done`, or `dropped` with its reason recorded" and "Anything in the v0.4.0 milestone's Required scope".
  - This belongs in the Goal (1086-1088).
  - The definition of done keeps only "every item in this release is `done`, or `dropped` with its reason recorded".
  - The out-of-scope bullet keeps only the fact the other two lack: v0.4.0 clears six Gate 0 items itself.
  - The three places use two names for one scope, "the teachable case's own scope" and "the v0.4.0 milestone's Required scope", and spell "Gate 0" as "gate-0" at 1112. The line edit should give each one name.
- **Rows 1086 and 1089 say the same thing twice:** "Its contents are exactly Gate 0's items…" and "The frozen list *is* the specification". The first stays and the second goes. "The release has no scope of its own to specify, which is why this section is short" (1088-1089) talks about the text itself, and it goes too.
- **Rows 1083-1084 and 1105-1106 describe the two safety items twice.**
  - The two descriptions are "Its verification gate is widened to cover the inputs that the interface can actually reach. Its failure path can no longer leave partial state behind" and "The two safety items on the list tighten a verification bound and make the step transactional".
  - The Goal keeps them, because its wording says what changes for the simulator.
  - The definition of done keeps only that neither item may change a modelled value, and what happens if one would.
  - One change is called "widened" in one place and "tighten" in the other. Row 1083 also uses "gate" for a test bound, while every other row uses it for Gate 0's list. The line edit should give each one name.
- **Rows 1081 and 1122 both rule out new capability:** "This release adds no capability" and "New capability of any kind". This belongs in the out-of-scope list, with its reason (1122-1123), because a reader looks there for what the release leaves out. The Goal keeps nothing, because 1082, "the simulator does what it did before, but correctly", already says it.
- **Rows 1114-1118 restate the rule for re-admitting items found after the freeze.** The bullet's own history (1119-1120) says that § "The gate is a snapshot, not a moving target" and step 4 of § "The cadence" already give this rule.
  - The rule belongs in § "The gate is a snapshot, not a moving target".
  - This bullet keeps the exclusion and a pointer to that section. The pointer should use the full heading in the § "Heading" form: 1116 leaves out the §, and 1119 shortens the heading to "The gate is a snapshot".
- **Rows 1118-1121 are decision history:** "This bullet used to name only the `P0`/`safety`/`science` half … (queue item PL-9PMV)". They belong in item PL-9PMV, and nothing stays here.
- **Rows 1101-1102 list the tools that `make check` runs, which is a developer's information:** `ruff format`, `ruff check`, `mypy`, `pytest`, `docket check` and `tools/doc_check.py`. This reader does not know `docket check` or `tools/doc_check.py`. Keep here that the full automated check passes, and leave the tool list where `make check` is defined.
- **Rows 1086-1088 send the reader ahead to the v0.4.0 section to learn what this release contained.** The frozen list sits under § "Debt gate: the frozen list" there, and "Gate 0" is first used here but explained only there. Since the release is complete, either list here the items it closed (or their number), or move the frozen list to its own section above both release sections.
- **Query (1090-1091 against 1115-1118):** rows 1090-1091 say nothing may be added to the frozen list. Rows 1115-1118 say that a finding present at the freeze re-enters, and so does anything at `P0` or classed `safety`/`science`. If "re-enters" means joining the list, the rows contradict each other, and only the author knows which is right.
- **Query (1076 against 1080-1108):** the heading says the release is completed, but the rows read as a plan, for example "Clear the inherited backlog" and "If either turns out to require one". No row gives the facts this reader needs about a finished release:
  - when v0.3.0 was released;
  - whether each done criterion was met;
  - which items were dropped, and why;
  - whether either safety item needed a change to a modelled value.
```

**Chapter read 10: § "Completed: v0.4.0 - the teachable case", rows 1125-1620.**

```text
- Written for another reader, rows 1131-1135: "They are not amended as the milestone closes them. A Goal records the problem… Rewriting it into the past… neither the problem nor the product" is a rule for whoever writes ROADMAP.md, not for the owner. It belongs with the roadmap's instructions to writers. Leave "stated below as they stood on 2026-08-25" and "the Required scope… is where this milestone's outcomes are recorded".
- Fact given twice, rows 1156 and 1593-1594: "This milestone changes no equation, parameter, or numerical method" and "No equation, parameter or numerical method has changed." Keep it in the Goal, where it explains why this is a minor release. The Definition of done keeps the reference-test criterion and drops the restated sentence.
- Fact given three times, rows 1161-1162, 1449 and 1609-1610: "the recording half of item 8", "This is the recording half of planned-milestone item 8, not the replay half" and "This includes the replay half of item 8's timeline. Only recording is in scope." Keep the promotion in the Goal and the replay exclusion in "Explicitly out of scope". Row 1449 keeps nothing.
- Fact given twice, rows 1162-1163 and 1608: items 26 and 12 are not promoted. Keep it in "Explicitly out of scope", where the reader looks for what the release leaves out. The Goal keeps "designed so that neither is blocked" and its pointer to § "Designed for forking".
- Contradiction, row 1472, as a query: "item 12 (forking, promoted below to "Designed for forking")" conflicts with rows 1162-1163 ("It does not promote… item 12") and row 1538 ("It is not built here"). Only the author knows which is right.
- Fact given twice, rows 1180-1181 and 1363: "The PL-Z4GF/PL-SWFM entry below holds two ids for one problem" and "One entry holding two ids". Keep it at the entry (1363). Row 1180 keeps only "count entries, not ids: the gate is 21 entries".
- Fact given three times, rows 1243-1246, 1251 and 1366-1369. Row 1243 states the presence rule ("whatever id the finding is filed under, and however long after the freeze someone noticed it"). Rows 1251 and 1366-1369 apply the same rule again ("regardless of which id or session it surfaced under"). Keep the rule once, at the head of the notes on later additions, and keep the "(project owner, 2026-08-25)" tag whole beside it. Rows 1251 and 1366-1369 each keep a pointer.
- Fact given twice, rows 1187-1188 and 1323-1324: "`bin/docket wave` reads the entries below against `docs/items/` and reports the split" and "`bin/docket wave` computes the gate's split by reading the entries recorded here against `docs/items/`". Keep the first. Row 1323 keeps nothing.
- Written for another reader, rows 1184-1189, 1282 and 1322-1328: the prose names internal tools (`bin/docket wave`, `docket check`), which this reader does not know. Say what each one guarantees. Item titles quoted in the list can stay as written.
- Fact given four times, rows 1274-1277, 1305-1306, 1315 and 1382-1383: safety- and science-classed findings re-enter the gate whenever they were captured. Keep it once, at the head of the debt-gate section with the P0 exception from row 1382. The notes keep a pointer.
- Fact given twice, rows 1238-1240 and 1253-1254: PL-K79K's command that did not exist. The entry keeps it. The note keeps only the date (`6f1b5b1`, 2026-08-24) and why that put it inside the gate.
- Fact given twice, rows 1301 and 1311: "missed rather than deferred" and "Leaving it out was an oversight, not a judgement". Keep the bold opening. Rows 1311-1315 are narration about the text, so cut them.
- Decision history, and a lesson for whoever triages items, rows 1279-1287 (PL-NV9W's priority and "something to check at triage"): move it to PL-NV9W's item file. The note keeps the date it was added and the ground it qualified on.
- Decision history, rows 1322-1328: the tool's blind spot and "a gate nobody wrote down…" belong in PL-Y4Q4, which the text says "records the diagnosis". Keep "the gate reported one entry fewer than its real size for three days" only if the owner needs it.
- Fact given three times, rows 1352-1357, 1406-1418 and 1616-1620: PL-WB0X stages 1 and 2 are in v0.4.0, and stage 3 (PL-B9PY) waits at Gate 1 for v0.5.0's comparison. Keep the stages in Required scope and stage 3 in "Explicitly out of scope" with its "(project owner, 2026-09-02)" tag. The note's three conflicting placements and PL-4C41 (rows 1347-1352) are decision history, so they go to PL-WB0X/PL-4C41. Rows 1356 and 1618-1619 also give the same comparison two names: "two-runs-at-once comparison" and "side-by-side comparison of two branches".
- Fact given twice, rows 1378-1380 and 1504-1505: PL-011 was dropped on 2026-09-05. Keep it in Required scope. The "Cleared by v0.4.0 itself" list keeps a pointer.
- Written for another reader, rows 1506-1507 ("recorded here rather than removed, because nobody can audit…") and 1528-1529 ("recorded here so that it is visible"): these are rules for writers, so cut them or move them with the rule at rows 1131-1135. Rows 1509-1519 (the design round, the score architecture, keyframes) are decision history for PL-011 and PL-T691. Keep "dropped because PL-2FM6 deletes the store it would bound", plus the growth figures and their cost.
- Written for developers, rows 1450-1455, 1457-1468 and 1480-1490: the struct-versus-tuple argument and the implementation notes (`ControlChange`, `RecordedSeries`, `RunHistory`, the 7-tuple) belong in the `docs/MODEL.md` sections they already cite, or in PL-DR1Z and PL-W3DD. Each landed note keeps one sentence on what shipped and how it differs from the scoped text.
- Fact given three times, rows 1471-1476, 1554-1556 and 1582-1584: the substance-keyed record keeps item 12's reproducibility proof from being reworked when a second substance arrives. Keep the reason in "Designed for forking". Required scope keeps the change, and the Definition of done keeps the criterion without the reason.
- Fact given twice, rows 1391-1392 and 1549-1551: the step count does not depend on machine speed. Keep the reason in "Designed for forking". Required scope keeps the requirement "never catches up to the wall clock".
- Fact given twice, rows 1477-1478 and 1604-1605: the MAC readout is the only piece that changes shape when a second substance lands. Keep it in "Explicitly out of scope". Row 1477 keeps nothing.
- Section away from where its reader looks, rows 1176-1372: row 1178 says the 21-entry list "is exactly what v0.3.0, the foundation release, ships". A reader deciding what v0.3.0 held looks in v0.3.0's section, which rows 1308 and 1340 suggest exists. Move the list and its notes there. v0.4.0 keeps one sentence saying v0.3.0 cleared that list, plus rows 1374-1383.
- Order, rows 1166-1383 before 1385: the debt gate comes before Required scope, yet rows 1353, 1374 and 1379 call Required scope "above". Either move the debt gate to v0.3.0 as the finding before this one says, or put it after "Explicitly out of scope". Then the reader meets what the release holds and leaves out first. The order Goal, Required scope, Designed for forking, Definition of done, Explicitly out of scope stays.
- Order inside the list, rows 1242-1357: about 115 rows of notes break off the list between the "Live process machinery" group (1222-1240) and the "Documentation, performance" group (1359-1372). Row 1177 says the notes are "beneath this list". Move 1359-1372 up to follow 1240, and put the notes after the whole list.
- Section too long to find one's way in, rows 1166-1383: add subheadings. Suggested: "Cleared before v0.4.0 began" (the list), "Entries added after the freeze", with one subheading for each of the four notes at 1242, 1261, 1301 and 1334, "Cleared by v0.4.0 itself" (1374-1380) and "Findings made while clearing" (1382-1383). Each note then needs only its ids, its date, the ground it qualified on, and its effect on the work left.
- Heading, row 1166: "Debt gate: the frozen list" uses a term ("frozen") that is explained only inside the section, and it does not say the section holds two lists. Suggested: "Debt cleared before and by v0.4.0". Other files that cite the heading must be updated with it.
- Fact the reader needs, rows 1388 and 1414: "Today `SimulationState.elapsed_s` accumulates…" and "Today that derivation ends in a private static method" are wording from scoping that reads as current, and the landed notes contradict it. Date them as the Goal does ("as scoped on 2026-08-25") or put them in the past tense.
- Query: row 1176 gives "(14 and 15 at the freeze)", which is 15 ids at the freeze. Rows 1364-1366 say PL-SWFM "surfaced later under the separate id", and rows 1168-1173 count 14 open items cleared before implementation. Which count of ids at the freeze is right?
- Query: the section is "Completed", and row 1178 says v0.3.0 ships these entries. Yet only four entries are marked done (PL-N2N1, PL-K79K, PL-Z4GF/PL-SWFM, PL-Y2GG), and row 1184 says closed counts are "not recorded here". The reader needs to know whether the other 17 entries closed, and whether the "done" marks should stay.
- Query: row 1276 says "This milestone's out-of-scope list names these classes as ones that re-enter the gate". The v0.4.0 out-of-scope list (1598-1620) names no classes, and row 1308 points to "v0.3.0's out-of-scope list". Which list is meant?
- Query: row 1526 says "A simulated day takes 8 minutes" at 300x. Row 1525 gives twelve hours in 2.4 minutes at the same rate, which makes a day 4.8 minutes. The reader also needs to know whether these figures and the 140 KiB and 3.16 GB at rows 1514-1515 came from runs or from arithmetic, and on what date. Row 1515 does not say what case length the 3.16 GB is for.
- Query: the note at rows 1242-1259 never names its two entries. The reader can only infer PL-N2N1 and PL-K79K from the "Added after the freeze" marks at 1235-1240.
- Query: these terms are not explained in this chapter, and the reader did not see the sessions that coined them: "Gate 1" (only "ships inside v0.5.0", row 1349), "the presumption" (1336), "the refilling-queue problem" and "Phase 0" (1342-1343), "the cut" (1505, 1510), "score architecture" and "keyframe" (1512-1514), and "bucket cache" (1428). I cannot tell what "an outside review of the repository, which recorded nothing of its own" (1261-1262) means.
- Query: row 1172 cites "Debt inside the milestone's own scope" without the § form, and no such heading appears in this chapter. Row 1443 writes "s" where § belongs, so the documentation check will not find that reference.
```

**Chapter read 11: § "Completed: v0.4.26 - the interface moves to Qt", rows 1622-2120.**

```text
- **Order (rows 1624-1828 against 1830-2120).** About 200 rows of decision history and release-tool detail come before "### Goal". The reader wants to know what v0.4.26 held and what it left out, and that starts at 1830. The opening rows also point ahead to Required scope items 2, 3, 6 and 8 (1655, 1762, 1786-1787, 1796), so the reader has to read on and come back. Use this order: Goal, Required scope, Fixes this port carries, Items this port moots or transforms, Definition of done, Explicitly out of scope. Then add one short closing subsection on why the port shipped before v0.5.0 and as a patch, built from 1628-1630, 1651-1676, 1678-1685 and 1700-1702. The rest of 1624-1828 goes where the lines below say.
- **Too long (rows 1624-1828).** If those rows stay, they need subheadings: "### Why it moved ahead of v0.5.0" before 1628, "### Why a patch number, and a section of its own" before 1678, "### Keeping this version number free" before 1704, "### The visual pass and the styling layer" before 1766, and "### Effect on the debt gates" before 1812. After the moves below, one closing subsection is enough.
- **Wrong place (rows 1624-1626).** The scoping history belongs in `PL-QXSB` and `PL-X9T3`. Keep only the scoping date in the closing subsection.
- **Wrong place (rows 1632-1647).** The counting method, the eight-id count and the import-check history (`PL-9KDK` to `PL-25KS`, "unused-allowance error") are developer and decision detail. Move them to `PL-RKWB` and `PL-25KS`. The closing subsection keeps one sentence: little of v0.5.0's work lay in the rewritten interface, so the move rests on three other grounds.
- **Wrong place (rows 1687-1698).** The mechanical reason for a section of its own (how `blocked-by` resolves, `bin/docket next`) belongs in `PL-L09X`. Here keep only 1700-1702.
- **Wrong place (rows 1704-1750).** These rows cover the numbering hazard, the eight-site rename count and the reserved-version decision. Move the general decision ("a number this file gives to a milestone section ahead of the current one is not free", with the tag "(project owner, 2026-09-16, ratified, on `PL-KQHN`)" whole) to § "Versioning decision" or the `v0.4.x` row, where a reader choosing a release number looks. The site count and the `PL-Y1L0` finding go to `PL-KQHN`, and the 2026-09-14 renumber goes to `PL-G7RD`. This chapter keeps nothing, because v0.4.26 has shipped.
- **Wrong place (rows 1752-1764).** The "open question" about this number is stale for a completed section. The bracketed 2026-09-27 note says the question "would not arise today". Move the reading to `PL-RKWB` and `PL-LPH9`. See the completed-status query below.
- **Wrong place (rows 1766-1800).** The absorption and un-absorption of item 33 belong in `PL-L9RD`, and the item 33/34 correction belongs in `PL-BNYF`. Required scope item 3 keeps the outcome: the visual pass is not in this release, and `app/theme.py` was re-expressed with no colour, size, padding or radius changed. That is the dated measurement at 1773-1781.
- **Wrong place (rows 1802-1810).** Where the Qt styling lives (`PL-Y4YX`) is something the release leaves out. It belongs as a bullet under "Explicitly out of scope for v0.4.26", where the reader looks for that. The reason it is not named in Required scope (1806-1809) is a rule for writers and goes to `PL-Y4YX`.
- **Wrong place (rows 1812-1822).** The Gate 2 reasoning belongs in § "The debt gate" -> "The cadence". Row 1820-1822 says that section already records both instances. Keep one sentence here: this port's findings go to Gate 2, which freezes when v0.5.0 ships.
- **Wrong place (rows 1853-1856).** The parenthetical on wording history belongs in `PL-YVM1`. Nothing stays here.
- **Wrong place (rows 1918-1937).** Required scope item 4 has grown into an essay about check internals (`contrast_check`, `agent_identity_check`, "keyed on one method name"). That detail goes to `PL-BXB2`, `PL-V53R`, `PL-0PJG` and `PL-JRS3`, and the membership history (1919-1922) goes to `PL-HWW1`. Keep one sentence: the two checks that read the interface's colours now read every interface module and treat an empty measurement as an error.
- **Wrong place (rows 1953-1961).** The account of `MilestoneStates.ships_with` and the two meanings of `blocked-by` is a rule for writers. It goes to `PL-HWW1` or a code comment. Item 8 keeps the six ids and a pointer to § "Fixes this port carries".
- **Wrong place (rows 2099-2101).** "The id and the reasoning are in ... `docket next` reads this heading" is a rule for writers and goes in a code comment or the item. See the `PL-8PSW` query.
- **Wrong place (rows 2062-2064).** The Gate 1 bookkeeping for `PL-7J96` belongs in Gate 1's section.
- **Merge (rows 2070-2073).** Merge into the `PL-NGF7` bullet (2045-2049), which should hold the deferral and its tag.
- **Pointer (row 2093).** "the carried-fix rule below" points down, but the rule is above, at 1970.
- **Said twice: the interface-pass row's history.** Row 1682-1683 "(That row was written `v0.5.x` until 2026-09-16, and has followed item 34 since.)" and row 1784-1785 "(That row was written `v0.5.x` then, and has followed item 34 since 2026-09-16.)". This belongs in `PL-PHKP`. Both places keep nothing.
- **Said three times: item 33 un-absorbed.** Row 1766 "It absorbed planned-milestone item 33, and no longer does", row 1913-1915 "Item 33 was un-absorbed on 2026-09-16 and is the interface-pass row again", and row 1895-1897. This belongs in Required scope item 3. The others keep nothing.
- **Said four times: the item 34 reservation.** Row 1788-1789 "built once here with their splitter handles inert, and **item 34** is what turns them live", row 1885-1887 "**The splitter handles stay inert.** Item 34 is what makes them live", row 1909-1910 "Making the handles live is item 34's first step and costs one line" and row 2117-2118 "Making those handles live is that milestone's first step". This belongs in Required scope item 2. The area-system bullet keeps "Required scope item 2 reserves space for it". Rows 1786-1790 keep nothing.
- **Said twice: what item 34 holds.** Row 1797-1799 "split, join, swap, break out, and save as a workspace" and row 1886-1888 "the split/join affordance, the workspace tabs and the savable presets". Say it once, where item 34 first appears in the new order (item 2), as one list.
- **Said twice: the `PL-BNYF` correction.** Rows 1793-1800 and the parenthetical at 1897-1901. Both go to `PL-BNYF`.
- **Said three times: "built decomposed from the start".** Rows 1891-1892, 1931-1932 and 2040-2041. This belongs in the `PL-B9PY` bullet. The others keep nothing.
- **Said five times: rendering inside the container.** Rows 1651-1659, 1848-1850 ("The spike writes a PNG ... where Flet's renderer cannot load"), 1943-1947, 2056-2057 and 2083-2084. This belongs in Required scope item 6. Ground 1 keeps only that the overlay could then be built where a session can see it. The Goal bullet keeps a pointer to item 6.
- **Said twice: `PL-7J96` dropped.** Row 1657-1659 "`PL-7J96`, the Flet equivalent, is `dropped` as superseded" and rows 2054-2060. This belongs in the `PL-7J96` bullet. Ground 1 keeps nothing.
- **Said twice: `PL-GS3R`'s 0.26 MAC, under two names.** Row 1663 "0.26 MAC of drawn departure at the 12 h base" and row 1845 "0.26 MAC of chord error". Also row 1862-1864 "The port is what makes that rule affordable" and row 1844 "this choice decides it". This belongs in Required scope item 1, with the value and the cost on each toolkit. Ground 2 keeps the item name, and the Goal bullet keeps a pointer. Use one name, "drawn departure", which the Definition of done also uses (2085).
- **Said four times: no new capability, so a patch.** Row 1680-1681 "After this port, a learner can do nothing that they could not do before", row 1967-1968 "narrow enough to keep this release a patch", row 1977-1978 "That is what keeps the patch argument ... true" and row 2092-2093 "This release adds none, which is what makes it a patch". This belongs in the first out-of-scope bullet. The closing subsection keeps the v0.2.8 precedent. 1967-1968 and 1977-1978 keep nothing.
- **Said twice: "whatever its size".** Rows 1905-1906 and 1977. Row 1977 keeps it, and item 2 keeps a pointer.
- **Said three times: parity means "identical except for this list".** Row 1667-1668 "parity against a **closed** enumeration", row 1907-1909 "Parity below means 'identical except for this list'" and row 1985-1986. This belongs in "The enumeration is the point". The others keep a pointer.
- **Said three times: `PL-NGF7`.** Rows 1935-1937, 2045-2049 and 2070-2073. This belongs in the `PL-NGF7` bullet. Item 4 keeps nothing.
- **Said twice, with two sources: what taught the guard.** Row 1732-1734 "`PL-VFD8` and `PL-188T` taught the reserved-version guard ..." and row 1749-1750 "`#606` taught the guard to see exactly that". Both leave the chapter. See the 1704-1750 line.
- **Said twice: compare mode.** Row 1668-1670 "compare mode, the largest new visual surface in the project" and row 2104-2105 "the largest new visual surface in the project was built once". This belongs in the closing subsection's grounds. The branched-run bullet keeps a pointer.
- **Said three times: the boundary of untouched code.** Rows 1640-1645, 2108-2111 and 1978-1979. This belongs in the out-of-scope `core/` bullet. Rows 1640-1647 go to the items. Rows 1978-1981 keep the rule that defects there wait.
- **Said twice: the schematic.** Row 1851-1853 "Headroom is needed for the schematic" and row 2114-2115 "This port makes it affordable and does not begin it". The Goal keeps the ground, and the out-of-scope bullet keeps "does not begin it".
- **Heading (row 1963).** "### Fixes this port carries, and why that is not scope creep" answers an objection. A heading that says what the section holds: "### Fixes and decisions this port carries". Row 1905 already cites it as § "Fixes this port carries", which does not match the current heading. Search other files before renaming.
- **Bullet lead (row 2108).** "**Anything under `core/`.**" also covers six `app/` modules. Use "**`core/` and the `app/` modules that never imported Flet.**"
- **Query: inconsistent section citations.** § "Sequenced past v0.5.0" (1633, 1828) does not match § "Sequenced past v0.5.0, so not clearable before it begins" (2021). "The gate is a snapshot" (2072) does not match § "The gate is a snapshot, not a moving target" (2063). "The debt gate" (1813) and "The timeline" (1783) lack the § form. The text does not say which heading text is current.
- **Query (Goal against the body).** Rows 1832-1833 say the goal includes "do the interface pass once on the way", but rows 1766-1790 and 1913-1914 say "The visual pass is not here." The text contradicts itself.
- **Query (rows 1835-1843).** "none of it is about speed" is followed by a first ground that is input latency. The text contradicts itself.
- **Query (`PL-LPLD`).** Rows 1675-1676 say "`PL-LPLD`'s bookmark list" moved into this port, but rows 2102-2103 say "v0.5.0's bookmarks and forking belong to that milestone, and this one does not touch them". The text contradicts itself.
- **Query (`PL-8PSW`).** The reader needs to know whether `PL-8PSW` (the two-run overlay) shipped in v0.4.26 and under which Required scope item. Rows 1675-1676 say it moved in, and rows 2094-2098 say the overlay is built. Required scope (1858-1961) does not list it, and rows 2099-2100 send the reader to § "Versioning decision" for the id.
- **Query (Flet's automated check).** Rows 1658-1659 say "no automated rendering check at all", but rows 2059-2060 say "no automated wrapping check before the port". These are two different claims.
- **Query (completed status).** The section is headed "Completed", but several rows are still written as open or future. Examples: rows 1752-1764 ("the one question ... left open"), 1809-1810 ("The port ships with"), 1891 ("`PL-B9PY` decomposes `SimulationView` in v0.5.0", against 2036 "landed ... 2026-09-14"), 2023 ("It waits for `PL-G59B` to land") and 1851-1856. The reader needs what is still open after v0.4.26, such as `PL-Y4YX`, `PL-16ZC`, item 33 and item 34, and the interface-pass row's current version. The text does not give it.
- **Query (Definition of done).** The reader needs whether each bullet at 2077-2088 was met. That includes `PL-GS3R`'s re-measured departure at each rung and where it sits in `docs/MODEL.md`. The text does not give it.
- **Query (rows 2000-2009).** The reader needs the outcome of each decision: `PL-YTX9`, `PL-CZFY`/`PL-Q4M4`, `PL-LL9Y` and `PL-2K1R`. The text does not give it.
- **Query (row 2068).** The reader needs `PL-027`'s disposition: moot, dropped or carried. The text does not give it.
- **Query (rows 1906-1907).** "a fourth entry beside `PL-16ZC`": the chapter names no second or third entry.
- **Query (rows 1714-1715).** The reader needs the source of "a rename each time, not a re-scope", and the text does not give it.
- **Query (row 2042-2043).** "than it would have a week ago" needs a date.
- **Query (undated values).** "A rewrite of 5 133 lines" (1700), "Today 27 `setStyleSheet` sites" (1803-1804), "has moved since 2026-09-10" as of when (1778-1780), the 49.4 ms and about 78 ms costs (1845-1846), and the 0.85-2.46 ms and 20-30 ms latencies (1840) all need the date they were measured.
- **Query (row 1645).** "The milestone's landed work" does not say which milestone, v0.5.0 or this one.
- **Query (row 1876).** "That item has the measurement": cannot tell whether this means `PL-YVHK` or `PL-YLKR`.
- **Query (row 1942).** "That note is argued again rather than cited either way": cannot tell what this means.
- **Query (unexplained terms).** No place in the chapter explains "declaration slot" (1919, 1953), "`wave`'s unreleased set" and "the beat" (1741-1742), "presentation-safety" (1659, 1850, 1944), "six channels are already spent", "two-compartment cap" and "owes an attribution to its run" (1660-1661), "the 12 h base" (1663), "rung of `TIME_BASE_LADDER`" (2086), or "the hedges that `PL-NV9W` requires" (2079).
```

**Chapter read 12: § "Completed: v0.5.0 - the case you can branch", rows 2122-2143.**

```text
- **The decision is given in two places.** Rows 2124-2126 give the decision itself: "**Its display half now builds on Qt (project owner, 2026-09-14, on `PL-RKWB`).** The Qt port moved ahead of this milestone." Rows 2125-2126 then say that § "Completed: v0.4.26 - the interface moves to Qt" "carries the decision, the count behind it and the three grounds." The decision belongs in that section and in `PL-RKWB`, and its tag moves with it whole. This section keeps only what the decision changed for v0.5.0: the two-branch overlay (`PL-8PSW`) and the bookmark list (`PL-LPLD`) were built once, on pyqtgraph. It also keeps the pointer to § "Completed: v0.4.26 - the interface moves to Qt".
- **The cost-and-benefit paragraph belongs with the decision (rows 2137-2141).** It opens "**What this costs and what it buys, recorded so it is not re-litigated.**" It holds the history of the Qt port decision and the reasons for it, which another section carries. Move it beside "the three grounds" in § "Completed: v0.4.26 - the interface moves to Qt", or into `PL-RKWB`. This section keeps nothing of it. The outline read should check whether the three grounds already say "a toolkit that a session can actually look at (`PL-2QMK`)" and "unblocks two `P1` `safety`-classed items" (`PL-GS3R`, `PL-YVHK`). If they do, cut both here.
- **The Gate 1 fact is given in two places (rows 2141-2143).** Row 2141 says the port "makes it possible for Gate 1 to reach zero before the milestone it gates begins." Rows 2142-2143 say that § "Sequenced past v0.5.0" "records that as the structural debt `PL-D143` named and could not pay." The fact belongs in § "Sequenced past v0.5.0", where the sequencing is. This section keeps nothing of it.
- **The section opens with the wrong subject (rows 2124-2135).** It opens with the Qt port, which is another milestone's subject. It says what v0.5.0 is only in its last sentence: "It is the release that crosses the branching capability boundary, and the port crosses none" (rows 2133-2135). Use this order:
  1. What the milestone is.
  2. Its port-neutral spine items (rows 2130-2133).
  3. What the port changed (rows 2126-2128), with the pointer to § "Completed: v0.4.26 - the interface moves to Qt".
- **The first paragraph makes three points (rows 2124-2135).** They are the port's effect on two items (rows 2124-2128), that nothing else changed and which items form the spine (rows 2128-2133), and what the milestone means (rows 2133-2135). A second bold phrase, "**Nothing else about this milestone moves.**", starts partway through it at row 2128. Split the paragraph at row 2128. Give what the milestone means its own paragraph, first in the section.
- **Query: the heading and the body disagree on whether the milestone has shipped.** The heading says "Completed", but the body reads as a plan. It says the spine "ships on the schedule it had" (row 2131). It says "It costs the MVP its place in the queue for the length of the port" (rows 2137-2138). It speaks of "before the milestone it gates begins" (row 2142). Has v0.5.0 shipped? If it has, the section needs what shipped. If it has not, the heading is wrong. I left both as they stand.
- **Query: the milestone's own scope is missing.** Rows 2129-2130 say that "Its goal, required scope, definition of done and out-of-scope list are unchanged." The section gives none of them, says nothing of what the milestone delivered, and points to no place that does. A reader deciding what a release holds needs them. The spine (rows 2131-2133) is seven item ids with no words saying what each one delivers.
- **Query: terms the chapter never explains.**
  - "Gate 1", and what "reach zero" counts (row 2141)
  - "port-neutral spine" (row 2130)
  - "durable halves" (row 2132)
  - "branching capability boundary" (row 2134)
  - "display half" (row 2124)
  - "the MVP" (row 2138): which milestone it names
  - "`P1`" and "`safety`-classed" (row 2140)

  The outline read should check whether another chapter defines them. If none does, this reader needs each one explained.
```

**Chapter read 13: § "Goal", rows 2145-2204.**

```text
- **Same point in two places.** Rows 2177-2179 say "The history before the branch point is identical in the two branches, because it is the same history and not a reproduction of it." Rows 2194-2196 say "This is what makes a branch's history before the branch point *the same object* as its parent's history, rather than a reproduction." The reason belongs in 2188-2198, which explains how that is achieved. The end-state paragraph should keep only "The history before the branch point is identical in the two branches."
- **Same point in two places.** Rows 2181-2183 say "run a case, branch it at a decision point, and compare the two managements side by side". The end state just above, in 2174-2176, already lists those steps: "A learner runs a case, marks the decision point, forks the case there, manages the two branches differently, and reads both on one time axis". Those rows also repeat the definition in § "What MVP means here". The steps belong in the end-state paragraph. Rows 2181-2183 should keep only the pointer: "This milestone completes the MVP as § "What MVP means here" defines it."
- **The reader has to read ahead.** Row 2170 uses "the score architecture" before 2190-2193 says what it is ("turns a run from a sequence of applied steps into a closed-form function of its control-input timeline"). Row 2196 says "Item 12 requires that property" before 2201 says that item 12 is forking.
- **The list of what the release holds comes last.** Rows 2200-2204 list the items the release holds and leave out item 9. That is this reader's main job, but the paragraph is last in the section.
- **Order to use:**
  1. the opening paragraph (2147-2151)
  2. the three gaps (2153-2166)
  3. the end state (2174-2179)
  4. MVP and minor release (2181-2186)
  5. the items promoted and left out (2200-2204)
  6. the change to `core/` (2188-2198)
  7. the sample-store debt (2168-2172)

  With this order, item 12 is named as forking before 2196 refers to it. The debt also comes after the paragraph that explains the score architecture. Its opener, "Beneath those three gaps sits a fourth problem", will need new wording in the sentence edit.
- **A sentence for another reader.** Rows 2197-2198 say "It is also the property where it is easiest to write a test that passes for the wrong reason." This warning is for whoever writes forking's tests, so it belongs in planned-milestone item 12's entry or brief. Move it there rather than cut it, because it is a warning. The Goal section then keeps nothing of it.
- **Query:** Rows 2168-2172 say this milestone keeps the promise to remove the sample store, and 2190 says the score architecture does this. But rows 2200-2204 promote no item that builds the score architecture or removes the store, unless that work is the replay half of item 8 (the resimulation driver). To decide what the release holds, the reader needs to know which item delivers that work, and the text does not say.
- **Query:** The reader needs to know which promoted item closes which of the three gaps (2153-2166), so they can see which gap stays open if they drop an item. The text does not say.
- **Query:** Rows 2202-2204 say item 10 "stays behind item 9's save/load, which is out of scope here". That implies item 10 is out of scope too, but does not say so. Since the reader is deciding what the release leaves out, the text should say whether item 10 is out of scope.
```

**Chapter read 14: § "Debt gate: the frozen list", rows 2206-2621.**

```text
- **The freeze-day triage is told twice.** 2242-2244 says "The 2026-09-06 triage pass classed the eleven captures that were not this session's own, and eight of them are debt. Those eight are the sixth group below." 2472-2473 says "The 2026-09-06 triage pass classified the eleven captures that were still untriaged when this list was frozen earlier that day. Eight of them are debt." The reason they rejoin is also told twice: 2235-2238 ("Each of these items was captured *before* this freeze … re-enters this gate rather than waiting for Gate 2") and 2474-2476 ("Each of the eight describes a problem that already existed at the freeze … rather than waiting for Gate 2").
  - Where it belongs: the group introduction at 2472-2479, next to the eight entries. Move the sentence on the three P1 findings (2244-2248) there too.
  - What 2231-2252 keeps: one sentence saying that an item still untriaged at the freeze joins the list, with its date and reason, if triage classes it as debt.
  - The reader can do without the four captures that are not debt (2248-2252). They belong in the record of the 2026-09-06 triage, and the text names no such record.
- **"Clears before implementation begins" is said five times.** "None of them is inside this milestone's Required scope, so all eight clear before implementation begins" (2476-2477) appears again at 2500-2502, 2512-2514, 2565-2566 and 2620-2621. Say it once in 2220-2229: every entry added after the freeze clears before implementation begins, unless Required scope names it, as it names the four at 2520-2524. The five group introductions then keep nothing.
- **The move of `PL-2FM6` and `PL-8LXM` is told twice.** 2272-2279 says they "are under § … They have also left `Required scope` … 'Required scope below drops to sixteen items'". 2301-2304 says "Required scope below drops to sixteen items … `PL-2FM6` and `PL-8LXM` moved between groups rather than joining the gate." The fact belongs in the note under the first group (2289-2304). 2272-2279 keeps nothing, and its history goes to `PL-C4RS`.
- **"0.32 MAC" appears twice:** at 2294 ("0.65 pp, **0.32 MAC**") and at 2312-2313 ("`PL-4RBD`'s 0.32 MAC only fell to 0.26 MAC").
  - The measurements belong in the items `PL-4RBD` and `PL-GS3R`.
  - The note at 2289 keeps one sentence: `PL-2FM6` came forward because `PL-4RBD`, now P1 `safety`, cannot close until the chart is drawn from the closed-form sampler.
  - The `PL-GS3R` entry keeps its one-line title.
- **The gate total appears twice:** "the gate total stays at 132" (2351-2352) and "the gate stands at 132 entries, 44 cleared" (2377-2378). The headings and the timeline row already give the size (2213-2214), and 2215-2217 says this section records no closed count. Cut both. A query below covers the contradiction.
- **One rule has five names.** Safety and science items rejoin under a rule called:
  - "the rule that admits a `safety` finding regardless of presence" (2315-2316);
  - "the second of the two unconditional exceptions in 'The gate is a snapshot'" (2494-2495, 2511-2512, 2619-2620);
  - "the unconditional safety/science exception" (headings at 2507 and 2614);
  - "the `safety` test" (2496).
  
  State the rule once, where the reader first meets it, and use one name after that. Cut 2511-2512, "Two passages state this same rule: … step 4 of 'The cadence'", because it describes the document rather than the gate.
- **Decision history is written for the history reader.** Each paragraph names the item that should hold its history:
  - 2265-2285 goes to `PL-C4RS`. Keep nothing here, because the three entries already sit under the right headings.
  - 2289-2304: the `PL-4RBD` measurement and the earlier cases of `PL-T691` and `PL-P1Z3` go to `PL-4RBD`. Keep the move and its one-line reason.
  - 2339-2352 goes to `PL-YXXG`. Keep that `PL-YDKJ` waits for `PL-2FM6`, because `PL-2FM6` changes the inputs `PL-YDKJ` depends on.
  - 2526-2536 goes to `PL-KTKP`. Keep that a check now flags any open safety or science item this list does not place.
  - 2552-2594 goes to `PL-36R4` and `PL-QXSB`. Keep:
    - the thirteen items admitted, split by lane;
    - the twenty-nine workflow-only items that were declined;
    - why `PL-QXSB` was admitted: v0.5.0's second chart doubles the interface cost it names;
    - its three follow-up items.
  - The tag at 2263, "(project owner, 2026-09-06)", stays whole beside "frozen whole rather than narrowed".
- **Three list entries have grown into essays:** `PL-GS3R` (2311-2319), `PL-ZX12` (2320-2326) and `PL-C4PH` (2371-2378). Cut each to one line: title, the date it was added or dropped, its class, `needs-decision` where it applies, and for `PL-ZX12` its place in the order (after `PL-8LXM`, before `PL-49R8`). The reasons go to each item.
- **Tool and file workings the reader cannot use.** These rows belong in `docs/maintainer.md` or the items:
  - 2214-2218: `tools/doc_check.py` and `bin/docket wave`;
  - 2255 and 2563-2565: `docket.toml` and `workflow_paths`;
  - 2283-2285: `PL-HWW1`'s change to parsing;
  - 2350-2351: "so no check has to work out that dependency";
  - 2517-2518: `PL-VRMK`'s tiering in `bin/docket concurrent`;
  - 2529-2535: `bin/docket wave`, `docket check` and `tools/doc_check.py`.
  
  The reader keeps what each one guarantees, such as "a check confirms that each heading's count matches its list". The comparison with Gate 0 (21 items) and v0.2.8 (38 items) at 2211-2213 is history the reader can do without.
- **Entries name internal tools.** The workflow-lane entries (2405-2453) and several others name internal tools and functions (`docket next`, `doc_check`, `_number_closing`, `cmd_next`), so the reader cannot judge them from here. These entries copy the item titles, so the fix belongs in those titles.
- **The list comes before its rules.** The list applies rules from § "The debt gate", which comes "below" (2209). The chapter uses "presence rule", "presence test", "the two unconditional exceptions", "What counts" and "The cadence" before stating any of them. Either place this section after § "The debt gate", or give each rule in one sentence where the reader first meets it (2231-2240).
- **Two paragraphs separate a group from its list.** 2520-2536 stands between the 2026-09-07 group's introduction (2509-2518) and its list (2538-2548). Move 2520-2524 after the list, or to the Required scope section as a pointer. Move 2526-2536 to `PL-KTKP`.
- **Late additions are filed two ways.** `PL-GS3R` and `PL-ZX12`, both added 2026-09-08, sit in the `v0.4.x` group, while every other late addition has a dated heading. Pick one scheme: either group entries by when they clear and tag each late entry with its date, or put every late entry under a dated heading.
- **Seven paragraphs come before the first entry.** Four of them (2231-2285) are history. After the moves above, open with what the list holds, its three groups, and when each group clears.
- **The section needs real subheadings.** It runs to 5931 words. Its groups are bold lines, not headings, yet 2273 and 2281 cite them with § as though they were sections. Make each a #### heading and keep its text:
  - "Cleared by the `v0.4.x` track, ahead of this gate";
  - "Cleared by v0.5.0 itself";
  - the three "Cleared before v0.5.0 begins" lane groups.
  
  Put the five dated additions (2470-2621) under one heading, such as "Added after the freeze".
- **"Group" means two things.** 2220 ("Three groups") counts by when items clear. 2244 ("the sixth group below") and 2528 ("the two groups above") count bold lines. Refer to each group by its heading.
- **Headings that do not say what they hold:**
  - "Debt gate: the frozen list" (2206) names neither the gate nor the milestone. It also calls the list frozen, though entries were added on 2026-09-06, -07, -08 and -10. The chapter implies this is Gate 1 (2237 "waiting for Gate 2", 2407, 2604) for v0.5.0 (2578, and the headings from 2328 on). Suggest "Gate 1: the v0.5.0 debt list, frozen 2026-09-06", and update the files that cite the old heading.
  - "Cleared before v0.5.0 begins, reaching both halves" (2455) uses "reaching" in a private sense. Suggest "Cleared before v0.5.0 begins, both lanes".
  - "Added … under the presence rule" (2470, 2550) names a rule the reader has not been given. It can stay once the rule is stated earlier.
- **Query:** the chapter uses the presence rule, the two unconditional exceptions and the exception for a late finding (2570-2571) throughout, but never says what they are. The reader needs them.
- **Query:** the chapter never says what the product lane and the workflow lane cover. It says only "the two lanes that `docket.toml` declares" (2255).
- **Query:** Required scope "drops to sixteen items" (2275, 2302) but "stays at eighteen items" (2351), and both are dated 2026-09-08. Which is current?
- **Query:** the bold opening at 2289 says "and one added", but 2302-2303 says the total "rises by two, for `PL-ZX12` and `PL-GS3R`", and both entries are marked "added 2026-09-08".
- **Query:** the counts disagree.
  - The gate total is given as 132 (2352, 2377), although 2302 says it rose by two that same day.
  - The headings in rows 2287-2612 add up to 151 entries (7+8+39+49+9+8+2+11+17), and the heading at 2614 announces one more.
  - "44 cleared" (2378) breaks the rule at 2215-2217 against recording closed counts.
- **Query:** 2344 says "`PL-2FM6` is in this group" (Cleared by v0.5.0 itself), but `PL-2FM6` is listed under the `v0.4.x` group (2309).
- **Query:** 2340-2341 says "It was in the product lane above", but the product-lane heading is below, at 2354.
- **Query:** `PL-T691` is described as a restructure still to come that the product half must be ordered against (2258-2260), and it is listed under "Cleared by v0.5.0 itself" (2330). But 2300 says `PL-T691` and `PL-P1Z3` "had already shipped in v0.4.8".
- **Query:** 2245-2247 pairs `PL-NBWP`, `PL-NBCJ` and `PL-B1WW`, in that order, with "the step size, the control resolution of the playback burst, and the oracle". Their entries say `PL-NBWP` concerns the burst (2481) and `PL-NBCJ` the step size (2482).
- **Query:** 2531-2532 says the list "contained none" of the project's open P1 items on 2026-09-07. But 2244-2245 and 2493 put five safety or science items on it on 2026-09-06 (`PL-NBWP`, `PL-NBCJ`, `PL-B1WW`, `PL-X35V`, `PL-ZVS7`). The claim holds only if all five had closed by then, and the text does not say they had.
```

**Chapter read 15: § "Debt gate: the frozen list", rows 2623-3165.**

```text
- **One admission paragraph is repeated in every group.** Row 2649 says "All seven are `safety`- or `science`-classed. So they re-enter this gate whatever the presence test says about them, under the second of the two unconditional exceptions in "The gate is a snapshot". None is inside this milestone's Required scope, so all seven clear before implementation begins". Row 3033 says "Each is classed `safety` or `science`, so each re-enters this gate whatever the result of its presence test. The rule that allows this is the second of the two unconditional exceptions … so all three must be cleared before implementation begins". The same thing is said again at 2732-2735, 2765, 2773-2774, 2802-2803, 2811-2813, 2876-2877, 2880-2881, 2884-2885, 2914-2917, 2969-2974, 3008-3014, 3090-3094, 3134-3135 and 3150-3151. Say it once, in a paragraph just before row 2645. Each group then keeps its capture and triage dates, its triage pass, and any exception to that paragraph:
  - PL-YVHK is sequenced behind the port (2814-2816).
  - PL-9KDK enters under the presence rule as a `defect` (2887-2890).
  - PL-LHBY is debt the milestone clears itself (2906-2909).
  - The four `PL-JRS3` entries land before the port's first commit (2868-2870).
- **Sizes are given twice.** "Each is `S`." (2918), "Its size is `S`." (3014), "All three are `S`." (3037) and "Both are `S`." (3094) repeat the "(S)" that each list line already shows. Cut these sentences and keep the size in the list line.
- **Dates are given twice.** From row 2873 on, each list entry opens "added 2026-09-…" (2873, 2878, 2882, 2886, 2894, 2920, 2931, 2938, 2978, 2993, 3016, 3046, 3060, 3071, 3101, 3126, 3142), and the group heading above it gives the same date. Keep the date in one place only: in the entry if the groups are regrouped by subject, as proposed below, or in the heading if they stay grouped by date.
- **The rule that `safety` and `science` entries cannot be deferred, and its one exception, appear in four places:**
  - 2749-2754: "`checks.py` exempts the class from the band only at `status: blocked`, and nothing blocks this item".
  - 2903-2904: "because the rule below makes `safety` not deferrable".
  - 2945-2951: "There is one carve-out: an `anticipated` finding whose hazard a later milestone creates. That carve-out also needs `status: blocked`".
  - 2971-2972: "Neither is `anticipated`, so the one carve-out to that exception does not apply to them".

  State the rule and its exception once, in the opening paragraph proposed above. PL-V6M0 keeps only why it does not qualify: nothing blocks it, and v0.5.0 makes its route real (2752-2759). Rows 2971-2972 and 2903-2904 keep nothing. The sentence naming `tools/doc_check.py` and the "disposition error" and "re-entry advisory" in a `### Declined to Gate ...` entry (2947-2949) are instructions for whoever maintains the gate. Move them to § "The gate is a snapshot". PL-KZ99's placement (2951-2953) belongs in the declined subsection, with a pointer left here.
- **The class of problem the exception covers is named twice.** Rows 2655-2656 ("which is the class of problem this exception exists for") and 2772-2773 ("This is the class of finding that this exception exists for") say the same thing. So do 2656-2657, 2782-2783, 2962-2963, 2973 and 3022-3023, which each say again that a reader turns to `docs/MODEL.md` to judge a displayed value. Say both once, in the opening paragraph, and cut the rest.
- **The argument that the item can be closed is made twice.** Rows 2627-2629 say "The project owner turned around two interlibrary loans in three days … `PL-7HDS` on 2026-09-08 and `PL-8SDL` on 2026-09-10". Rows 2671-2675 say "on the same evidence as `PL-LT51` above … the project owner has turned around three interlibrary loans". Keep the argument with PL-LT51. PL-RFLN keeps only the pointer "on the same evidence as PL-LT51". PL-RFLN closed on 2026-09-13 (2679), so its admission argument is history and belongs in its item. The reader keeps the result: only the published value is left.
- **The point that a value must be marked as modelled is made in five places:** 2686-2693, 2710-2713, 2827-2830, 2834-2836 and 2854-2855. The point that the paused tooltip is where a reader studies a number is made in 2688-2690, 2827-2828 and the list line at 2727. Explain both once, at PL-YLKR or at PL-YVHK, the half that is still open. PL-2K1R and PL-27H0 then keep one clause each that points back.
- **The design's independence from the toolkit is stated twice.** Rows 2693-2694 ("The design does not depend on the toolkit and survives the port. Only its implementation moves") and 2822-2827 (design landed on v0.4.x, building it against pyqtgraph remains) make one point. Keep it at PL-YVHK and cut it from 2693-2694.
- **PL-DZFJ's paragraphs (2696-2719) are a correction history, written about the text itself.** Examples: "The seventh is the paragraph immediately above", "Until that date, the paragraph argued…", "That is why this is a rewrite and not a removal" and "The brief was corrected along with this paragraph". Move the history to PL-DZFJ's item. The reader keeps one sentence: PL-DZFJ corrected the gate text and PL-YLKR's brief on 2026-09-13. Rows 2709-2713 restate 2686-2693, so cut them. Row 2648-2649 ("A seventh was added later the same day and is explained at the foot of this group") goes with them.
- **PL-2FM6's removal of the recorded-sample store is stated twice.** Rows 2700-2704 ("`PL-2FM6` deleted `RunHistory`… in v0.4.12. The chart now evaluates the run's score *at* the instants it plots") and 2850-2853 ("`PL-2FM6` deleted that store, and `app/chart_frame.py` now deliberately says the opposite") give one fact. Keep it at PL-27H0, which is still open, and cut it from PL-DZFJ.
- **PL-LHBY and PL-4KZD describe the same defect, and the text contradicts itself about them.** Rows 2894-2896 say "draws the marks panel from the reference run alone, and a mark's *standing* is per-run where its *set* is not". Rows 3126-3128 say "drawn once from `snapshots[0]`, so while two runs are shown it states the reference run's standings for a set every run carries". The text then gives opposite dates for this defect: "the problem postdates the freeze by a fortnight" (2903) against "the problem is older than the freeze" (3135-3136). See the first query.
- **"PL-3K9B's decision unmasks PL-4KZD" is said three times:** at 3087 ("one problem and its consequence"), 3123-3124 and 3137-3138. Keep it once, in PL-4KZD.
- **The machine survey is described at its second mention.** Rows 3039-3043 describe `PL-4DCG`'s machine survey, but it first appears at 3007 and 3019. Merge the PL-NM7X group (3005-3028) with the PL-WQF1 group (3030-3083), which share a date and a source, and describe the survey where it first appears.
- **PL-D126's closing fragment repeats the group paragraph.** "A statement about the limits of a comparison rather than a defect in this implementation" (3069-3070) repeats 3041-3043. Cut it.
- **Rows 2680 and 2793-2794 may give the same fact.** PL-RFLN says "the apparatus was excluded" (2680), and PL-XWCY says "rules out circuit-wall absorption as a candidate for desflurane's residual" (2793-2794). Both come from the 2026-09-13 reading. If they are one fact, keep it in PL-XWCY and point to it from PL-RFLN. See the queries.
- **One group is out of date order.** The PL-LHBY group (2892-2909, dated 2026-09-20) sits between the 2026-09-14 and 2026-09-17 groups. Move it after the 2026-09-19 group, next to the other bookmark entries: PL-3K9B, PL-4KZD, PL-N3N5 and the 2026-09-21 entry. Both PL-N3N5 (3147-3154) and the 2026-09-21 paragraph (3161) refer back to it. Its phrase "the rule below" (2904) then needs rewording, or it goes once the rule is stated in the opening paragraph.
- **The 2026-09-13 group is out of order, and its opening is wrong.** PL-DJYF's paragraph (2761-2774) comes before PL-V6M0's list line (2776), but PL-DJYF's own list line is at 2805. Put PL-V6M0's line right after 2759. The group's opening, "These entries were found by the triage pass over the fourteen captures open that day (`PL-TQJ4`)" (2731-2732), covers only PL-V6M0. PL-DJYF came from a later pass over twenty-seven captures (2761-2762), and PL-QBKQ and PL-XWCY came from reading the Targ paper (2778-2780). Name each entry's source in the opening.
- **Two paragraphs in the 2026-09-17 group are in the wrong place.** The rule paragraph (2945-2953) applies to every group but sits after this group's list. Move it to the opening paragraph proposed above. The "not live" paragraph (2955-2963) explains PL-H4N8 and PL-QBX0. Put it before the list or inside those two entries.
- **Several headings do not say what their group holds.** The bold group headings at 2892, 3005, 3030, 3085 and 3140 all read "Added 2026-09-20 under the unconditional safety/science exception" and differ only in the count, so a reader scanning cannot tell them apart. Name each group's subject, for example "Default fresh gas flow wording", "Machine survey: what `docs/MODEL.md` must say about its limits" or "Bookmarks on branched runs". Alternatively, adopt the subject grouping in the next finding.
- **The section is too long to navigate.** At 5,898 words, a reader looking for one entry has to scan twelve groups ordered by triage date. Add subheadings by subject, and give each entry its added date:
  - Sources behind the reference patient: PL-LT51.
  - Statements in `docs/MODEL.md` that the shipped files no longer support: PL-7KDC, PL-S3Q0, PL-Q5NS, PL-27H0, PL-S6WW, PL-7DMJ, PL-D126, PL-WJNS, PL-NM7X.
  - Planned-milestone entries to correct before they are built: PL-MMWX, PL-H4N8, PL-QBX0.
  - Breathing circuit volume and absorption: PL-QBKQ, PL-XWCY, PL-DJYF, PL-RFLN.
  - Chart hover and the modelled-value notice: PL-YLKR, PL-YVHK, PL-DZFJ, PL-2K1R, PL-JVHL, PL-0RZ0.
  - Bookmarks on branched and failed runs: PL-LHBY, PL-3K9B, PL-4KZD, PL-N3N5, the 2026-09-21 entry.
  - Checks the interface port depends on: PL-BXB2, PL-V53R, PL-0PJG, PL-9KDK.
  - What happens when applying a setting fails: PL-V6M0.

  Make sure the new subheadings do not disturb the `### Declined to Gate ...` headings that the gate's check reads (2948).
- **Much of the chapter is written for a developer, not for this reader.** The reader does not know internal names of tests, checks and tools, yet the text is full of them:
  - error classes and `core/exceptions.py` (2737-2747);
  - `checks.py` and "the band" (2750-2751);
  - dataclass field names (2765-2769);
  - a test file name (2797);
  - check and tool names (2873-2890);
  - functions, constants and attributes (2894, 2978-2980, 3104-3123, 3127-3132, 3142-3147).

  These belong in the item briefs. The roadmap keeps what a learner sees and what each entry asks for. Several list entries have grown into essays, the writing rule's fifth pattern: PL-LHBY, PL-S6WW, PL-JVHL, PL-0RZ0, PL-3K9B, PL-4KZD and PL-N3N5. Their measurement details belong in each item, along with the derivation of PL-S6WW's decision (0.35 %, 5.6–6.2 %): PL-JVHL's 43.8–81.4 %, PL-3K9B's seven cases and its 3 600 of 3 600, and PL-0RZ0's 480 px row. In PL-S6WW and PL-3K9B, either keep the decision tag whole beside the decision or move it whole to the item.
- **Statements about the gate's rules belong in the section that sets out the rules.** Rows 2816-2820 ("The two statements do not conflict … Silence is the third option, and the only one that is forbidden") explain how the gate works and belong in § "The gate is a snapshot". Three sentences are rules for writers and should be cut here: "It is written down here because that rule requires it" (2813-2814), "They are listed because the presence rule requires their disposition to be written down…" (2870-2871), and "`test` is not a debt class, so they owe this gate no disposition" (3164-3165).
- **Most presence answers can go.** The text gives a presence answer for entries that the exception admits whatever that answer is: 2924-2925, 2989-2991, 3001-3003, 3011-3012, 3096-3099, 3135-3136, 3151-3153, and "Captured after the freeze" at 2876. Row 2991 itself says the exception "makes irrelevant" the answer, so the reader can do without them. Keep the answer only where it changes when the entry clears, as for PL-LHBY (2903-2909).
- Query: the reader needs to know whether PL-LHBY and PL-4KZD are one defect, or whether PL-LHBY's change fixed PL-4KZD. Row 3153-3154 says PL-LHBY now draws "the standing … in words on an attributed row". The text also says the defect both "postdates the freeze by a fortnight" (2903) and "is older than the freeze" (3135-3136).
- Query: the reader deciding what a release holds needs each entry's current status in one place, and the chapter gives it inconsistently. Only PL-S6WW's list line says "closed" (2920). These entries have no status in their list lines although the text implies they are done:
  - PL-RFLN: "Closed 2026-09-13" (2679), list line 2725.
  - PL-DZFJ: "corrected 2026-09-13" (2697), list line 2722.
  - PL-YLKR: its design landed (2823-2825), list line 2727.
  - PL-JVHL: "while closing `PL-JVHL`" (3051), list line 2978.
  - PL-LHBY: rows 3153-3154 describe what it changed.
- Query: § "Completed: v0.4.26 - the interface moves to Qt" (2866) says the port is complete. Yet PL-YVHK "cannot be done before the toolkit exists" (2826-2827), PL-2K1R "rides the Qt port" (2836), and the four PL-JRS3 entries "land before the port's first commit" (2868-2869). Are these entries closed, or is the text out of date?
- Query: rows 3087-3089 say that by 2026-09-20 work on a Required-scope item was under way: PL-B8MK was being built, and PL-VKJW's change is also mentioned at 2905-2906. So what does "must be cleared before implementation begins" (3013-3014, 3036-3037, 3093-3094) mean for entries added from that date? And how does it differ from PL-LHBY's "debt this milestone clears itself rather than a precondition to beginning it" (2906-2907)?
- Query: PL-2K1R "clears before v0.5.0 begins" (2839), but § "Sequenced past v0.5.0" "carries it in that table" (2840). Row 2814 also calls PL-YVHK "the one entry in this block that does not clear before implementation begins". Which is right? The text also does not say which "the five carried entries" are (2839).
- Query: two numbers conflict. Rows 2627-2628 give "two interlibrary loans in three days", and 2674-2675 give "three interlibrary loans". Which is right, and what is the third loan's item and date? "The last week" (2631, 2674) does not say which week.
- Query: rows 2945-2946 say "The gate is a snapshot" makes `safety` and `science` entries impossible to defer. Does the argument that the item can be closed (2623-2631, 2671-2675) still decide anything for PL-LT51 and PL-RFLN? This chapter does not give PL-LT51's class.
- Query: "Its three feature-mates from that review … One is deferred below. The other three are classed `test` alone" (3162-3164) adds up to four, not three. The text calls the 2026-09-21 entry "the third `safety` finding" from the review of `#784` (3159), but never names the second. Neither the entry's id nor its list line appears in this chapter.
- Query: PL-0RZ0's problem is "two slow compartments of one run" (3049), but its example is "the trunk's and the branch's fat values land on the same pixel row" (3052-3053). That is two runs' copies of one compartment, which is PL-JVHL's problem.
- Query: what does "not deferred with the apparatus" (2800) mean, given that PL-RFLN says "the apparatus was excluded" (2680)? Is that exclusion the same finding as PL-XWCY's ruling out of circuit-wall absorption?
- Query: row 2961-2962 says PL-S6WW's "sentence is false as written", in the present tense. Row 2920 says the entry closed on 2026-09-17, and rows 2925-2926 say it was resolved.
- Query: PL-LT51's list line says "starting with ICRP Committee II page 151" (2643), but rows 2634-2636 report that page as already read. Is the list line out of date?
- Query: in "`docs/MODEL.md` § "Parameter provenance" and `docs/machine-survey.md` § "(a2)" both restate it" (3020-3021), it is unclear whether "it" means the superseded claim or the survey's finding.
- Query: this chapter uses terms the reader needs but never explains them. If the first chapter does not explain them either, the reader needs them explained:
  - the presence test, presence rule and presence answer;
  - the two unconditional exceptions, of which only the second is cited;
  - Required scope;
  - tier 1, tier 2 and tier 3;
  - the carried-fix rule;
  - the `anticipated` class and "the band";
  - `status: blocked`, `P1` and debt class;
  - capture and triage pass, and "the store" (2968);
  - workflow lane, Gate 2 and M4.

  The chapter never states the freeze date either. It follows only from 2889: a tool shipped on 2026-09-04, "two days before this freeze".
```

**Chapter read 16: § "Debt gate: the frozen list", rows 3167-3219.**

```text
- **Same reasons given twice.** Rows 3178-3182 say PL-25DD was admitted "for the two reasons `PL-LHBY` was: the rule below makes `safety` not deferrable whatever the presence answer, and this gate's own Required scope is what created the hazard — `PL-VKJW` made two runs reachable from a shipped entry point for the first time. The widgets are older than the freeze; their ambiguity is not." Rows 3189-3193 say the same again: "They are admitted for the same two reasons as `PL-25DD`. First, the rule below makes `safety` not deferrable whatever the result of the presence test. Second, … The widgets predate the freeze, but their ambiguity does not."
  - Fix: give the reasons once, at PL-25DD (3178-3182), where the reader meets them first. In rows 3189-3193, keep only "They are admitted for the same two reasons as `PL-25DD`."
  - The two places use two names for one thing: "presence answer" and "presence test". Whichever place keeps the reasons should use one name.
  - Rows 3178-3179 say these are PL-LHBY's reasons. The outline read should check whether PL-LHBY's entry, outside this chapter, already gives them. If it does, that entry holds them. PL-25DD then keeps only a pointer to PL-LHBY and its own fact that the widgets predate the freeze but their ambiguity does not.
- **PL-25DD may be under the wrong subheading** (3167-3182). It was added the same day (2026-09-21), as a `safety` item, under the same rule as the two entries below the subheading at 3184 ("the unconditional safety/science exception — 2 entries"). Its own subheading is above row 3167, outside this chapter. If that subheading is not for the same exception:
  - move PL-25DD under 3184 and change the count to "3 entries";
  - give the two reasons once, in the paragraph that opens that subheading (3186-3195), instead of at PL-25DD.
- **The reader has to read ahead.** "The rule below" (3179, 3190) points past this chapter to the rule that both admissions depend on.
  - Where the rule is cited, say it in words, using the name the subheading at 3184 gives it: the unconditional safety exception, under which a `safety` item is never deferred, whatever the presence test finds.
  - If the outline read finds the rule after these lists, move it above them.
- **Code names written for another reader.** Each entry locates its fault in the code. These names serve the developer who fixes the item and belong in that item's brief in `docs/items/`:
  - PL-25DD (3169-3171): `_place_run`, `_off_scale_column`, `_wash_in_state_column`, `WASH_IN_STATE_TEMPLATE`, `off_scale_notice`; also "splitter" (3174);
  - the paragraph under 3184 (3187, 3194-3195): `_place_run`, `build_transport_row`, `_run_name_text`;
  - PL-TSZM (3197-3202): `_holder(self._notice_column, (run.build_notice(),))`, `NoticeLabel` and the three template names;
  - PL-C3GS (3208-3212): `_holder(self._sidebar_column, run.build_sidebar_panels())`, `CONTROL_TIMELINE_CAPTION`.

  `ROADMAP.md` should keep what the learner sees on screen and why it is unsafe. That includes the quoted screen text: "Now: F_A/F_I = {ratio}", "Simulation stopped", "this run reached the supported run length", "The simulation is unchanged and still running its previous setting", the sidebar headings, and "What was changed during this run, most recent first".
- **How the two entries were found belongs in their items.** Rows 3186-3188 ("Both were found while implementing `PL-25DD` above, not by the `#784` review. … Fixing two of them prompted a reading of the other four") belong in the briefs of PL-TSZM and PL-C3GS. The paragraph keeps what the owner needs to judge whether the list is complete:
  - each run's displays go into six places that the runs share;
  - PL-25DD covers two of them, and these two entries cover two more;
  - the other two already name the run or the agent (3193-3195, once the code names leave).
- **The reason for PL-C3GS's size belongs in its item.** Rows 3216-3219 ("`M` rather than `S` because the headings are built inline in `build_sidebar_panels` … needs the plumbing `set_run_name` has") are about the code, and belong in PL-C3GS's brief. The entry line keeps "(M)".
- **Query (undefined terms):** the reader needs to know what "the freeze" is and its date (3178, 3182, 3193), what the "presence answer" or "presence test" is (3179-3180, 3190-3191), and what "this gate's own Required scope" means (3180, 3191). This chapter explains none of them. The outline read should check that an earlier chapter does, and if none does, define each where it first appears.
- **Query (hazard table):** "the hazard table's existing row for reading a failed halt as a pause" (3204-3206) names neither the file that holds the table nor the row, so the reader cannot find it.
```

**Chapter read 24: § "Required scope", rows 5222-5497.**

```text
- **The same fact in two places: the added entry.** Rows 5228-5233 say "The nineteenth item was added on 2026-09-20 (`PL-XJ37`) … every mechanism that the Goal sentence depends on had shipped, but no shipped entry point called any of it." Rows 5453-5456 say "This is the entry the milestone was missing. The four entries above build every part of a branch, but none of them is reachable … Added 2026-09-20 (project owner, 2026-09-20, `PL-XJ37`)." The fact belongs in the `PL-VKJW` entry, and the decision history belongs in item `PL-XJ37`. The opening paragraph should keep only the count and the three groups.
- **Rows 5235-5245 are mostly decision history, about two items that are not on this milestone's list.** This reader needs one sentence: `PL-2FM6`, which draws the chart from the sampler, and `PL-8LXM`, which removed the decimation path, were required here and shipped in the `v0.4.x` track, so the list leaves them out. That sentence fits after the count in the opening paragraph, or after the list. Several details should go to items `PL-C4RS`, `PL-2FM6` and `PL-8LXM`: `PL-011`'s debt, what the decimation deletion took with it, the quoted note "drops to sixteen items", "frozen gate" and "declaration slot". Rows 5239-5240, "A sampler that computes any window in closed form", repeat rows 5248-5249 and can be cut.
- **The closed form is stated three times.** The fact appears at rows 5248-5250, 5239-5240 and 5296-5299 ("`state_at` computes any instant of it in closed form"). It belongs in the `PL-T691` entry, and the other two places keep nothing.
- **The canonical evaluation rule is stated in two places.** Rows 5253-5259 (`PL-P1Z3`) say what the rule is for. Rows 5302-5306 (`PL-J2TD`) say what it requires: "every replayed, compared or branch-opening value to be taken canonically", which rules out a resimulation driver. That requirement belongs in the `PL-P1Z3` entry. The `PL-J2TD` entry keeps only what it leaves out: no resimulation driver and no replay control. The figures 6.7e-16 and 1.8e-14 at rows 5300 and 5306 belong in `docs/MODEL.md` § "The canonical evaluation rule", which rows 5324-5325 say "carries the measurements". Leave a pointer there.
- **Rows 5293-5325, `PL-J2TD`'s "Narrowed" and "Mechanism replaced" paragraphs, are history and developer detail.** They cover the old wording, the 2026-09-14 changes, `PL-2R2C`, `RunDefinition`, `state_at`, the test file and `origin_s`. They belong in items `PL-J2TD` and `PL-ZMRT`. Rows 5317-5318, "opens the branch's definition *at* the fork, on the case's axis. So there is one time frame", repeat rows 5284-5285, "It runs on the case's own clock, and its run definition opens at the fork instant." Keep the version at rows 5284-5285.
- **Branch-equals-parent is stated four times.** Rows 5394-5397 (`PL-Z3W6`) say the branch reproduces its parent element by element, and rows 5306-5307, 5371 and 5414-5416 say it again. The fact belongs in `PL-Z3W6`. The `PL-8PSW` entry needs it as a reason, so it keeps a short clause there. The other places keep nothing.
- **Rows 5265-5270, `PL-RD3B`'s "Re-briefed" note, are history and belong in item `PL-5328`.** Rows 5268-5269 ("the vocabulary that addresses a trace, and the window that a frame draws") repeat rows 5264-5265. The entry keeps its first two sentences.
- **Rows 5352-5359, `PL-TFX5`'s "Split" paragraph, are history and belong in item `PL-TFX5`.** Its point that bookmark forking waits for the items that build the bookmark and its halt repeats row 5339 and rows 5371-5373, and belongs in the `PL-B8MK` entry. Its keyframe-only rule repeats row 5284. The entry keeps one sentence: forking at a bookmark is the next entry.
- **Rows 5363-5367 compare the two routes, which is how the decision was reached.** That comparison belongs in item `PL-B8MK`. The entry keeps the chosen route and what it guarantees: marking a run does not change the run. Rows 5377-5384, on the day when the model could fork at a bookmark and the control could not, belong in item `PL-TYWQ`. The entry keeps how the second control behaves, with its whole "ratified" tag. Rows 5370-5371 and 5380-5381 both say that no keyframe is recorded, so keep it at rows 5370-5371. The method names `resumed_at_halt`, `fork_at_halt` and `fork_points_s` are written for a developer and belong in the items.
- **Rows 5411-5448, the four `PL-8PSW` sub-paragraphs, argue reasons that `docs/MODEL.md` § "The six compartment traces" already holds.** Row 5421 says that section "carries this decision", and row 5427 says it gives the 1.01:1 figure. The 3:1 minimum appears twice, at rows 5419-5420 and row 5428. The compartment encoding stated at rows 5399-5400 is argued again at rows 5430-5431, 5435 and 5441. Keep these in the entry:
  - the encoding;
  - the stacked panels that were rejected, with their tag;
  - that the first run is drawn wider;
  - that the two-compartment cap is required because it frees line width for the run;
  - the fallback to test.

  The contrast and channel reasoning belongs in that `docs/MODEL.md` section, with a pointer from here. The history belongs in items `PL-HLD5` and `PL-GVXP`: `PL-HLD5`'s assumption, the reversal of 2026-09-07 and `PL-GVXP`'s finding.
- **The agent rule is given twice.** Rows 5349-5350 say "The branch carries its parent's agent and patient", and rows 5466-5467 say "`SimulationController.set_agent` already refuses on a branch (`PL-TFX5`)". Keep the fact in `PL-TFX5`. The `PL-VKJW` disposition can give its reason as "because a branch keeps its parent's agent".
- **Rows 5450-5452 and 5455-5456 are written for a developer.** They name `main()`, `BranchedCase`, `SimulationView`, `RunView` and `fork_at`, and belong in the brief for `PL-VKJW`. The entry should say what the learner can do. Rows 5468-5470 (`PL-QRD1`) are history and belong in that item.
- **The `PL-1XPX` and `PL-MN4J` entries overlap.** Both are owner decisions about naming which run a display describes. Row 5473 says "a decision rather than an implementation", and rows 5484-5485 say "Like `PL-1XPX`, it is a decision rather than an implementation". The safety reason at rows 5473-5475 matches the definition-of-done quote at rows 5489-5491. Say once that both are the owner's decisions and why. Rows 5479-5484 say twice that the hover is unclear only in compare mode. Rows 5478-5479 ("debt that this gate can clear") and row 5487 ("no session can close it") are rules for sessions. This reader needs only that the owner decides, and that the decision cannot come before compare mode.
- **Several entries have grown into essays.** Rows 5295-5307, 5333-5337 and 5460-5465 use "First … Second". The two `PL-LPLD` deviations and the two `PL-VKJW` dispositions are what the release leaves out, and each pair reads better as a short list. Once the history moves, each entry needs only a few sentences.
- **The section is too long to find one's way in.** It runs to 3065 words in one list of 19 entries. Add subheadings for the three groups that the opening paragraph names:
  - before row 5247: "Score architecture", or a plainer name (see the query on "score architecture");
  - before row 5263: "Boundaries that this milestone's code moves";
  - before row 5283: "Taking a branch".

  You could also add "Showing and comparing two runs" before row 5398.
- **Bold opening phrases that do not say what their paragraph holds.**

  | Rows | Current phrase | Suggested phrase |
  | --- | --- | --- |
  | 5459 | "Two dispositions are settled in that item's brief rather than left to its pull request" | "A second fork is refused while a comparison is shown, and a branch shows its agent without a dropdown" |
  | 5411 | "Which run carries the width offset was settled when it was built" | "The first run is drawn wider" |
  | 5423-5424 | "The channel assignment is reversed from what this bullet said until 2026-09-07 …" | "Line style and colour show the compartment, and line width shows the run" |
  | 5377 | "The interface half is `PL-TYWQ` and shipped 2026-09-21" | "A second fork control appears while the run stands on a bookmark halt" |
  | 5253 | "The canonical evaluation rule that carries determinism" (uses "carries" in a private sense) | "A rule for which route to an instant is authoritative" |

  The labels "Narrowed", "Mechanism replaced", "Split" and "Re-briefed" go with their paragraphs to the items.
- **Pointers by position break once anything moves.** The list is not numbered, and the subheadings or moves above would change positions. Pointers like this appear at row 5288 ("item 12's fork", "two bullets down") and in other places that point to "the entry below" or "the entry above" (rows 5295, 5306, 5339, 5358, 5373-5374, 5415 and 5453-5454). Name each entry by what it does instead.
- **Query: no single place gives each item's status.** The reader needs to know whether each of the 19 items has shipped or is still open, and in which release, to decide what v0.5.0 holds. Status is given in an item's own entry for `PL-LPLD`, `PL-B8MK` and `PL-TYWQ`. It is given only inside another entry for `PL-T691` (row 5296), `PL-CTD7` (row 5373), `PL-VKJW` (row 5377), `PL-J2TD` (row 5317) and `PL-8PSW` (rows 5411 and 5488). No place gives it for `PL-P1Z3`, `PL-49R8`, `PL-RD3B`, `PL-TCD1`, `PL-1PSX`, `PL-B9PY`, `PL-Y5WR`, `PL-Z3W6`, `PL-1XPX` or `PL-W7H9`.
- **Query: "the nineteenth item" (row 5228) is `PL-VKJW`, which stands sixteenth in the list.** A reader who counts arrives at `PL-W7H9`.
- **Query: rows 5373-5374 quote a phrase that the entry below does not contain.** They say the entry below is a branch "taken between two recorded samples". The entry below, `PL-Z3W6` (rows 5394-5397), does not contain that phrase.
- **Query: rows 5453-5456 are written in the present tense and contradict row 5377-5378.** They say "none of them is reachable. Nothing in `src/` constructs a `BranchedCase`", but rows 5377-5378 say `PL-VKJW` landed the fork panel on 2026-09-20.
- **Query: `PL-Y5WR` may not fit its group.** Rows 5280-5282 justify it as "carried here rather than lost", not as a boundary that this milestone's code moves. Which of the three groups does it belong to?
- **Query: the counts do not add up.** Row 5242 records a move that left "sixteen items". The only additions the text names are the split of 2026-09-14 (row 5352) and `PL-XJ37`, which make 18. The section lists 19. This needs an answer only if that sentence stays.
- **Query: the reader needs these terms, and this chapter does not explain them:**
  - "score architecture" (row 5225);
  - "frozen gate", "the heading that says so" and "declaration slot" (rows 5243-5244);
  - "gate" (rows 5278 and 5479);
  - "path-scoped rule" (row 5260);
  - "`PL-011`'s dropped growth debt" (row 5237);
  - "M4 decimation path" (row 5238);
  - "selector" (rows 5384 and 5461);
  - "running-agent chip" (row 5466);
  - "the Goal sentence" (rows 5230 and 5457), whose words are not given here.
- **Query: row 5461 calls the branch selector "out of scope" but does not say where it goes.** The reader needs to know which later milestone or item holds it.
```

**Chapter read 25: § "Definition of done", rows 5499-5526.**

```text
- Rows 5520–5521, "`PL-WZVZ`, which `PL-S5Q9` deferred to Gate 2, is the one entry that takes the last of these routes": this is a scope fact inside a completion rule. It goes out of date as soon as a second entry is deferred. Move it to `PL-WZVZ`'s entry in "the frozen list above", where the reader checks what v0.5.0 holds, and describe the item in words there. The record that `PL-S5Q9` made the decision belongs in `PL-S5Q9`. This rule keeps only the three routes: done, dropped with its reason, or deferred.
- Row 5519, "on the terms of beat 3 of § "The cadence"": the reader has to go back to another section to learn when a deferral is allowed. State those terms here, and keep the § "The cadence" pointer after them.
- Rows 5507–5508, "A threshold that is never reached ends in a distinct, visible outcome rather than in silence": this is a separate rule, which can be met or missed on its own. "And a test asserts this" comes before it, so it does not cover it. Give it its own list item.
- Rows 5525–5526, "`docket check`, `tools/doc_check.py`": this item is written for the session doing the work, and this reader does not know the project's internal tool names. Say in words what these two checks cover. The exact commands belong where the workflow documents its checks.
- No change to the order: the list goes from behaviour, to documentation, to scope, to regression tests, to automated checks, which suits a reader deciding what the release holds. The section is short enough to need no subheadings, and its heading says what it holds.
- Query: the reader needs to know what `PL-WZVZ` is, in words, to see what v0.5.0 leaves out. The chapter gives only its id.
- Query: the reader needs the terms for deferring an item, from beat 3 of § "The cadence". This chapter does not give them.
- Query: this chapter does not explain "the frozen list", "Required scope", "a later gate" / "Gate 2", "the canonical evaluation rule" or "sample store", and this reader may not know them.
- Query: in rows 5507–5508, is "a threshold" a kind of bookmark? If it is, use one name. If it is not, the reader needs to know what it is.
- Query: rows 5505 and 5507 require a test for branch reproduction and for bookmark halting. Rows 5509–5513 (comparing runs on one time axis, and the memory limit) do not say how they are checked. The reader needs to know whether a test is part of "done" for those too.
- Query: what do `docket check` and `tools/doc_check.py` check, in words?
```

**Chapter read 26: § "Explicitly out of scope for v0.5.0", rows 5528-5603.**

```text
- Rows 5543-5544 and 5555-5556 both describe `PL-ZW0J`: "whether returning to a mark forks or truncates, and the setting that chooses between the two" and "`PL-ZW0J` asks whether returning to a mark forks, or truncates after a confirmation". The description belongs once, in the list of five deferred items at 5543-5544, with "after a confirmation" added there. Rows 5555-5556 keep only "that question".
- Rows 5568-5569, 5573 and 5573-5574 give the same limit three times: "The comparison is specified for a trunk and one branch", "this milestone never compares one branch directly against another" and "A comparison is always of a branch against the trunk". Keep one sentence ("A comparison is always of a branch against the trunk") and cut the other two.
- Rows 5567, 5569 and 5578 give the two-run cap three times: "More than two runs displayed at once", "`MAX_DISPLAYED_RUNS` stays 2" and "The display is capped at two runs under either answer". The bullet's opening (5567) states the cap. Cut 5569. Rows 5577-5580 keep only the reason: a selector buys the choice of pair, not more curves.
- Rows 5570-5572 and 5582-5584 make one point twice: "a stable order, chosen so that a later selector does not renumber the branch a learner is looking at" and "adding the selector later is additive rather than a rework". Keep one sentence at 5582-5584 saying that the selector can be added later without rework, because branches keep a stable order. Cut 5570-5572.
- Rows 5565-5566 and 5569-5570 both say that N branches are allowed: "one trunk with N branches" and "N branches may exist". Keep the fact at 5565-5566 and cut it from 5569-5570.
- Rows 5563 and 5591 both send work to item 9. Merge them into one bullet: "Scenario save/load (item 9), including persisting bookmarks or branches across a restart", followed by the replay control (item 10) and its sentence on the resimulation driver.
- Rows 5537-5541 are in-scope work under an out-of-scope heading: "This milestone keeps four of them and does not defer them." The four items belong in Required scope and the definition of done. Here, keep one clause saying that four of the nine items are required there. Cut "They are named where they are required rather than here, because readers treat this heading as a scope declaration" (5540-5541), because it describes the text itself.
- Rows 5586-5590 describe in-scope behaviour: a second fork is refused while a comparison is displayed. The text itself says that "the fork-control entry in Required scope settles" this, so it belongs in that entry. Keep nothing here, or at most a pointer.
- Rows 5580-5582 are editing history of the roadmap text: "The sentence this bullet replaced read 'N branches may exist and be selected between'. That sentence stated a permitted future as though it were scope." They belong in `PL-XJ37` or the commit message. Cut them here.
- Rows 5557-5559 are decision history: "The project owner deferred that question on 2026-09-20 because they wanted to use the feature first". The date belongs in `PL-ZW0J`. Keep here only the reason a contributor acts on: the question waits until the owner has used the feature, and widening v0.5.0 would answer it first.
- Rows 5533-5536 are also decision history: the owner's quotation "a bit of a mess …" and "The count supports this: on 2026-09-21, nine open items concerned that surface". They belong in the item that records the 2026-09-21 decision. Keep "nine open items" here only if the arithmetic of four kept and five deferred is kept.
- Rows 5546, 5569 and 5570 use internal code names this reader does not know: `has_recorded_run`, `MAX_DISPLAYED_RUNS` and `BranchedCase.branches`. Each one belongs in its item or in the code. Here, describe it in words. For `PL-7TBQ`, for example, write "the case reports a recorded run before the learner has touched the branch".
- Order within the first bullet (5530-5561): the reader needs the exclusion, then the five deferred items, then where they go, then why. Use this order: 5530-5532 with the decision tag, the five items (5541-5547), Gate 2 (5549-5553), the reason (5555-5561), then a one-clause pointer to the four kept items.
- Order of the bullets: the branch exclusions are split up by the save/load bullet. Use this order: fork and bookmark interaction (5530), sub-forks (5565), more than two runs and the selector (5567), the merged save/load, persistence and replay bullet (5563, 5591), then the remaining bullets. Putting the remaining bullets in item-number order (items 1-5, 6-7, 27-28, 30, then panning, then the equations) would let the owner check them against the numbered list.
- Length: the bullets at 5530-5561 and 5567-5590 have each grown into a three-paragraph essay, together about 580 of the section's 773 words. Subheadings would not help. After the moves above, each bullet should be the exclusion, where it goes, and its reason in two or three sentences, and the list shape then fits.
- Heading: "Explicitly out of scope for v0.5.0" fits once rows 5537-5541 and 5586-5590 move out.
- Query (5549-5553): the reader needs to know what Gate 2 is. This chapter says only when it freezes and when it is cleared, and points to § "The cadence". Check that § "The cadence" defines Gate 2.
- Query (5545-5546): the reader needs the range of one-decimal times behind "refuses 35.5%" and the date the figure was found. This chapter gives neither, and it does not explain "the whole-step fork guard".
- Query (5552): "the area system" that v0.6.0 builds is not explained in this chapter.
- Query (5557): "the act this milestone is named for" leaves the act unnamed. Name it, for example as returning to a mark.
- Query (5599-5600): "the fit-run scale" is not explained, and "still" points to a context this chapter does not give.
- Query (5530-5532): the 2026-09-21 decision tag names no item. The quotation, the count and the reasoning at 5555-5561 have no item to move to until one is named.
- Query (5538-5540): the four kept items are not named here. The outline read should check that Required scope and the definition of done name them, and that the four plus the five deferred make nine.
```

**How to apply.** Move and deduplicate only. No sentence is reworded, except a pointer that replaces a restatement, a word such as "above" or "below" that a move made wrong, and a heading. The line edit of what this slice changes follows in `PL-YRY3`, once the copy editor no longer drops requirements (`PL-F0Q2`). Each finding is applied, or recorded here with the reason it was not. A query that the tree answers is answered in the pull request, and one that needs the author is filed as its own item under `roadmap-structure`. Whether a finding that moves decision history out of the roadmap and into an item is applied is decided by the project owner's answer in `PL-LVN8`. Before the pull request is marked ready, two reviewers compare the old and new text passage by passage for any change of meaning. The move-only restructures of the machine documents and of `docs/interface-provenance.md` each changed 10 or 11 meanings that only such a comparison found.

**Done when.** Each finding below is applied, or recorded here with the reason it was not. No statement is lost: every sentence that leaves its place is kept at its one home, or replaced by a pointer that names that home. `bin/docket wave`, `bin/docket gate` and `bin/docket check` give the same answers before and after the slice, and `make check` passes.

**Generator check.** The repeats came from accretion. Each change that touched a topic stated its own record in the section it was working in, instead of pointing to the section that already held it. The structure read found the same shape in every document it read (`PL-BSMF`, `PL-SVGH`, `PL-T8RL`, `PL-39ZK`, `PL-3MTS`), so these are one sweep's findings. No check can decide whether two sentences state one fact. The structure read, which the project owner put ahead of every line edit on 2026-11-07, is the procedure that catches the shape. Not recorded as a generator.

**Left for this slice by `PL-DWGC` (2026-11-07).** The timeline's v0.5.0 row
still lists the seven Required-scope items that shipped before v0.5.0 (five in
v0.4.25, `PL-8PSW` in v0.4.26 and `PL-MN4J` in v0.4.28). The structure read
puts them in v0.5.0's own section. The v0.4.26 section's sentence "A rewrite of
5 133 lines with its own goal, required scope, definition of done and
out-of-scope list is a milestone by this file's own test" restates what
§ "Project roadmap" says a milestone needs, and can keep only its point.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. Every record the item cites was in `ROADMAP.md` at `817a4d88`. Later edits in its range changed only wording.

**Next steps, written 2026-11-08 by the thread that ran slice 7.** Slice 7 (`PL-M3MV`) is the model to follow; its brief's "What this slice did" records each finding's fate under *Applied*, *Not applied, with the reason*, *Queries the tree answers* and *Queries filed*, then *Review* and *Checked*.

1. Bring `origin/main` in once slice 7's pull request has merged, and claim this item.
2. Capture `bin/docket wave --no-fetch`, `bin/docket gate --no-fetch`, `bin/docket check` and `tools/doc_check.py check` (under `uv run python` with `UV_SYSTEM_CERTS=true`) before any edit, and compare after. Keep a frozen copy of `ROADMAP.md` from before the first edit.
3. Search only inside § "Completed: v0.1.0" to § "Completed: v0.5.0", and leave v0.5.0's gate dispositions to slice 9 (`PL-4BCF`). v0.5.0's § "Sequenced past v0.5.0, so not clearable before it begins" is a gate disposition, and its table is the index the outline read keeps.
4. Slice 7 moved item 25's five rates into v0.4.0's `PL-SN2C` entry and pointed v0.5.0's `PL-LPLD` entry at the class `MacTarget` in `app/bookmarks.py`; the catalogue's items 8, 11, 12, 25 and 26 now point to these sections, so a record moved out of them must leave its pointer target in place.
5. Quote each sentence of decision history word for word into its item, under "**Moved from `ROADMAP.md` on DATE (`PL-V8SJ`).**" with a lead-in that glosses every word whose meaning depends on its old position. Keep a table's rows on separate quoted lines. A sentence another file already holds needs no quote; name that file in the record.
6. Before the reviews, list every sentence of the old sections that the new file lacks, by normalising whitespace and searching for each sentence, and route each one: kept elsewhere in the file, held by a named file, or quoted in an item.
7. Rewording findings go to `PL-YRY3` as a numbered list. Queries that need the author go to one new item under `roadmap-structure`, as `PL-NTHF` does for slice 7.
8. Two reviewers compare old and new, one for words that depend on position and one sentence by sentence, each given the frozen copies and the diff of the item files.
9. Close the item before pushing: the push hook refuses an open item whose `verify:` passes. Then run `bin/docket verify --self PL-V8SJ`, arm, and merge on green. Set slice 9 (`PL-4BCF`) `ready` with a `verify:` of an admitted shape (`! grep -qF` for a sentence the work removes) that fails until its work is done.
