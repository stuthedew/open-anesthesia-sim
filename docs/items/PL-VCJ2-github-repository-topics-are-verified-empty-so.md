---
id: PL-VCJ2
title: GitHub repository topics are verified empty, so the repository is undiscoverable by topic search and the proposal from the 2026-09-01 self-description discussion is still unapplied
priority: P3
effort: S
status: done
classes: docs
feature: project-introduction
touches: docs/items/PL-VCJ2-github-repository-topics-are-verified-empty-so.md
added: 2026-09-21
closed: 2026-09-21
pr: 873
payoff: someone searching GitHub for an anesthesia pharmacokinetics teaching tool can find this one
not-delegable: the deliverable is a GitHub repository setting no session can write; only the project owner can apply it
---

**Problem.** GitHub repository topics are verified empty, so the repository is undiscoverable by topic search and the proposal from the 2026-09-01 self-description discussion is still unapplied

**Measured 2026-09-21, which is what makes this a fact rather than the
assumption it was.** `GET /repos/stuthedew/open-anesthesia-sim/topics` returned
`{"names": []}`, and the repository object's `topics` key returned `[]`. Two
endpoints that do report topics, against the search API's repository object,
whose omission of the key left this unresolvable before (`PL-S669`). The
repository is `public`, so topics are the discovery surface they are meant to
be.

**Why it matters.** Topic search is how someone looking for an anesthesia
pharmacokinetics teaching tool finds one; with none set, the repository is
reachable only by name or by full-text search. The proposal is also the last
unapplied piece of the 2026-09-01 self-description discussion, whose other
three outputs all shipped — `README.md`'s opening, the GitHub "About" field and
`pyproject.toml`'s `description`. This item is that discussion's remainder,
rehomed here when `PL-S669` deleted its resolved thread from
`docs/WORKING_NOTES.md`.

**Proposed set, derived rather than invented.** `CITATION.cff` already carries a
curated `keywords` list, so the topics come from it normalized to GitHub's rules
(lowercase letters, numbers and hyphens; 50 characters or less; no more than 20
topics, verified against GitHub's "Classifying your repository with topics" on
2026-09-21). That is the sequencing `PL-4MHK` used for the package summary —
derive the short form from the finished long document instead of drafting a
fourth version of it:

`anesthesiology`, `anesthesia`, `pharmacokinetics`, `inhaled-anesthetics`,
`simulation`, `medical-education`, `python`

`CITATION.cff`'s "uptake and distribution" is deliberately left out: it is the
domain phrase the `description` already carries and is not a term anyone
browses by. Add `pyside6` or `qt` only if the interface toolkit is something
the project wants to be found by, which is a different question from what the
project *is* about.

**Not a session's to apply.** Repository topics are a repository setting. No
`mcp__github__` tool in this harness writes them, so the steps belong to the
project owner and are written out in full at the point of asking.

**Done when.** The topics endpoint returns a non-empty `names` array for
`stuthedew/open-anesthesia-sim`.

## Applied and verified 2026-09-21: nine topics set, so the discoverability goal is met

**Measured, not taken on trust.** `GET /repos/stuthedew/open-anesthesia-sim/topics`
returns a non-empty `names` array and the repository object's `topics` key
agrees, both listing nine: `anesthesia`, `anesthesiology`,
`inhaled-anesthetics`, `medical-education`, `medical-simulation`,
`pharmacokinetic-modeling`, `pharmacokinetics`, `python`,
`volatile-anaesthetic`. Nine is inside GitHub's limit of twenty. `Done when` is
satisfied and this item is closed.

**Six of the seven proposed went in; the project owner changed one and added
three.** `simulation` was replaced by `medical-simulation`, which is the better
term - the bare word is a discipline-agnostic topic carrying everything from
circuit simulators to game engines, where `medical-simulation` names the field
this belongs to. `pharmacokinetic-modeling` and `volatile-anaesthetic` are new.

**`volatile-anaesthetic` was queried and the query was wrong; `PL-HWV1` is
filed and dropped, on the same day, for the audit.** This session read the topic
as contradicting `PL-XF89`, on the grounds that the decision put **inhaled** on
the project-describing surfaces and **volatile** on the release-describing one.
The project owner's challenge - that the two words are interchangeable in
clinical use - holds, and the objection fails twice: a topic list is a set of
search keys rather than prose, where an overlapping or spelling-variant key is
the point; and the claim that *volatile* was confined to `pyproject.toml` is
false, since `docs/MODEL.md` is titled "Volatile-agent patient uptake and
distribution model" and is *correct* to be, describing what is implemented.
`PL-HWV1` carries the full withdrawal, including what the volatile-is-a-subset-
of-inhaled taxonomy does and does not license, so that it is not re-litigated.
The nine topics stand as set.

**What could not be measured, so that the next session does not assume it was.**
How populated each candidate topic is - the evidence that would say whether
`volatile-anaesthetic` reaches any searcher at all - was not obtainable:
`GET /search/repositories?q=topic:...` is refused in this harness, which binds a
session to its configured repositories and returns "This GitHub API path is not
available". It is recorded because it is the evidence a future session would
want before touching the topic set at all - not because anything now turns on
it, `PL-HWV1` having been withdrawn on grounds a count would not have changed.
