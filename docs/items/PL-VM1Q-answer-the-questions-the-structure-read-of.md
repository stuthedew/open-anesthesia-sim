---
id: PL-VM1Q
title: Answer the questions the structure read of ROADMAP.md's v0.1.0 to v0.5.0 records left for their author: missing outcomes of completed releases, counts that disagree, contradictions between passages, and terms never defined
status: untriaged
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-08
---

**Problem.** Answer the questions the structure read of ROADMAP.md's v0.1.0 to v0.5.0 records left for their author: missing outcomes of completed releases, counts that disagree, contradictions between passages, and terms never defined

**Source.** The copy editor's structure read of `ROADMAP.md` (chapter reads 6 to 16 and 24 to 26, § "Completed: v0.1.0" to § "Completed: v0.5.0"), quoted whole in `PL-V8SJ`. Slice 8 (`PL-V8SJ`) applied the moves, answered from the tree each query the tree answers, and listed both in its brief's "What this slice did". What follows needs the author. Where a passage the question is about moved to an item, the question names that item.

**The questions.**

1. v0.1.0's tolerance, reference scenarios and step sizes are named without a pointer. Where are the documented tolerance and the reference scenarios recorded?
2. v0.2.0: did the Pydantic migration happen, were the equilibrium tests and the numerical note delivered, does the default still load sevoflurane only, and where is vaporizer physics planned? Which item holds the halothane and later-agents stretch goal? No item is named for the milestone itself.
3. v0.2.8's frozen-list entries carry no outcomes, and the section gives no ship date (its tag is dated 2026-09-01). Should each entry record how it closed?
4. v0.2.8: `PL-1CYR`'s scope test against the owner's direction (the paragraph now in `PL-J295`); "after the four above" and "the four of 2026-09-01"; "the weakest of the seven". Which entries do these name?
5. v0.2.8: the decisions tagged 2026-08-30 and 2026-08-31 name no item. Which items record them? Do v0.2.8's rules apply to every frozen list or only to its own?
6. v0.2.8 uses "beat", "cadence", "parse floor", "grandfathered", "captures" and "groom" without defining them. Where should each be defined?
7. v0.3.0 says nothing may be added to Gate 0's list, and its out-of-scope list says findings that § "The gate is a snapshot, not a moving target" re-admits are not excluded. If "re-enters" means joining the list, which statement holds?
8. v0.3.0 is headed "Completed" but gives no facts of a finished release: whether each criterion was met, which items were dropped and why, and whether either safety item needed a change to a modelled value.
9. v0.4.0's Gate 0 heading gives "14 and 15 at the freeze", while PL-SWFM "surfaced later" and the opening counts fourteen open items cleared before implementation. Which count of ids at the freeze is right? The heading also says "three notes beneath this list", and four follow.
10. v0.4.0 marks four of the 21 Gate 0 entries done and records no closed count. Did the other 17 close, and should the "done" marks stay?
11. v0.4.0 says "This milestone's out-of-scope list names these classes as ones that re-enter the gate", but v0.4.0's out-of-scope list names no classes. Which list is meant?
12. `PL-011` (the sentence now in its brief) gives a simulated day at 300x as 8 minutes, while twelve hours take 2.4 minutes, which makes a day 4.8 minutes. Were these figures, and the 140 KiB against 3.16 GB, measured or computed, on what date, and for what case length is 3.16 GB?
13. v0.4.0's note on the two entries added 2026-08-30 never names them; they are PL-N2N1 and PL-K79K by inference. Confirm.
14. v0.4.0 uses "Gate 1", "the presumption", "the refilling-queue problem", "Phase 0", "the cut", "score architecture", "keyframe" and "bucket cache" without defining them here. What does "an outside review of the repository, which recorded nothing of its own" mean?
15. `PL-W3DD`'s scoped entry (now in its brief) said item 12 was "promoted below to Designed for forking", while v0.4.0's Goal says it does not promote item 12. Which was meant?
16. v0.4.26's Goal says "do the interface pass once on the way", while Required-scope item 3 says "The visual pass is not here". Should the Goal change?
17. v0.4.26's Goal says "none of it is about speed", then gives input latency as the first ground. Which is meant?
18. v0.4.26's closing section says `PL-LPLD`'s bookmark list moved into the port, while the out-of-scope list says v0.5.0's bookmarks "belong to that milestone, and this one does not touch them". Which is right?
19. v0.4.26's ground 1 says the Flet build gets "no automated rendering check at all", while the `PL-7J96` bullet says "no automated wrapping check before the port". Which claim is meant?
20. v0.4.26 is headed "Completed", but several passages read as open, for example "The port ships with the styling composed where it is today". What remains open after v0.4.26 (items 33 and 34), and was each definition-of-done criterion met, including `PL-GS3R`'s re-measured departure at every rung?
21. v0.4.26: "a fourth entry beside `PL-16ZC`" names no second or third entry. "That item has the measurement" (in the `PL-YVHK` paragraph): `PL-YVHK` or `PL-YLKR`? "That note is argued again rather than cited either way" (item 5): what does it mean?
22. v0.4.26's undated figures: the 5 133-line rewrite, 27 `setStyleSheet` sites, the 49.4 ms and about 78 ms costs, the 0.85-2.46 ms and 20-30 ms latencies, and "than it would have a week ago". On what dates were they measured?
23. v0.4.26 uses "presentation-safety", "six channels are already spent", "two-compartment cap", "owes an attribution to its run", "the 12 h base", "rung of `TIME_BASE_LADDER`" and "the hedges that `PL-NV9W` requires" without defining them.
24. v0.5.0's opening says the spine "ships on the schedule it had", but the milestone shipped on 2026-09-21. Should the opening record what shipped, and say in words what each spine item delivered?
25. v0.5.0's Goal: which item delivers the score architecture and removes the sample store, which promoted item closes which of the three gaps, and is the store's removal the replay half of item 8?
26. v0.5.0's Gate 1 section never states the presence rule, the two unconditional exceptions or the late-finding exception it applies, and never says what the product and workflow lanes cover. Should it state them, or point to where they are stated?
27. Gate 1's counts disagree: Required scope "drops to sixteen items" and "stays at eighteen" (the latter now in `PL-YXXG`), both dated 2026-09-08; "and one added" against "rises by two"; a total of 132 against group headings that sum to 151 plus one; and "44 cleared" against the rule that the section records no closed count. Which are current?
28. Gate 1: `PL-T691` is described as a restructure still to come, listed under "Cleared by v0.5.0 itself", and said to have shipped in v0.4.8. `PL-NBWP`, `PL-NBCJ` and `PL-B1WW` are paired with "the step size, the control resolution of the playback burst, and the oracle" in an order their entries contradict. Which is right?
29. Gate 1: the KTKP note (now in `PL-KTKP`) says the list contained none of the project's open `P1` items on 2026-09-07, while five `safety` or `science` items were on it from 2026-09-06. Had all five closed?
30. Gate 1: are `PL-LHBY` and `PL-4KZD` one defect? The text says the problem both "postdates the freeze by a fortnight" and "is older than the freeze".
31. Gate 1: entries still read as waiting on the Qt port (`PL-YVHK`, `PL-2K1R`, the four `PL-JRS3` entries) after v0.4.26 shipped. What does "must be cleared before implementation begins" mean for entries added once `PL-B8MK` was under way, and how does it differ from the words "debt this milestone clears itself" in Gate 1's `PL-LHBY` entry?
32. Gate 1: `PL-2K1R` "clears before v0.5.0 begins" but § "Sequenced past v0.5.0" carries it; which are "the five carried entries"?
33. Gate 1: two interlibrary loans in three days, or three (the second count is now in `PL-RFLN`)? What is the third loan, and which week is "the last week"? Does the closeability argument still decide anything for `PL-LT51` and `PL-RFLN`, and what is `PL-LT51`'s class? Its list line says "starting with ICRP Committee II page 151", which the paragraph above reports as read.
34. Gate 1: "Its three feature-mates" counts four; the second `safety` finding from the `#784` review is never named. `PL-0RZ0`'s problem is two compartments of one run, but its example is two runs' copies of one compartment. "Not deferred with the apparatus" against "the apparatus was excluded": is that `PL-XWCY`'s finding? The words "sentence is false as written" in Gate 1's `PL-S6WW` entry are present tense after that item closed. In the `PL-NM7X` group, what does "it" refer to in "both restate it"?
35. Gate 1 uses presence test, rule and answer, tiers 1 to 3, the carried-fix rule, `anticipated`, "the band", `status: blocked`, debt class, capture, triage pass, "the store", workflow lane, Gate 2 and M4 without defining them, and never states the freeze date. The hazard table's row named under `PL-TSZM` gives no file or row.
36. v0.5.0's Required scope gives a status for some items and not others. Should one place give each of the 19 items' status and release?
37. v0.5.0's Required scope: "taken between two recorded samples" is quoted from the `PL-Z3W6` entry, which does not contain it. `PL-Y5WR` is justified as "carried here rather than lost", not as a boundary this milestone moves: which group does it belong to? Where does the declined branch selector go?
38. v0.5.0's Required scope uses "frozen gate", "declaration slot", "path-scoped rule", "selector", "running-agent chip" and "the Goal sentence" without defining them.
39. v0.5.0's definition of done: what is `PL-WZVZ` in words, what are beat 3's terms for a deferral, is "a threshold" a bookmark, and how are the one-axis comparison and the memory bound checked? What do `docket check` and `tools/doc_check.py` cover, in words?
40. v0.5.0's out-of-scope list: what is Gate 2 (does § "The cadence" define it)? What range of one-decimal times and what date stand behind "refuses 35.5%", and what is "the whole-step fork guard"? What is "the area system", "the act this milestone is named for", and "the fit-run scale"? Which item records the 2026-09-21 decision, so the owner's quotation and the count can move there? Which are the four kept items?
