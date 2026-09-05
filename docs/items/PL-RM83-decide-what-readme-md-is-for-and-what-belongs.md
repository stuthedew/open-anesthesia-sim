---
id: PL-RM83
title: Decide what README.md is for and what belongs in it before the rewrite starts
priority: P2
effort: S
status: done
classes: docs
feature: project-introduction
milestone: v0.4.0
touches: README.md
added: 2026-09-05
closed: 2026-09-05
pr: 338
verify: grep -c '^### [123]\. ' docs/items/PL-RM83-decide-what-readme-md-is-for-and-what-belongs.md | grep -qx 3 && grep -q '^blocked-by: PL-XYRN$' docs/items/PL-N092-rewrite-readme-as-a-human-readable-introduction.md
not-delegable: the command below proves only that `PL-N092` is unblocked. Whether the three answers recorded here are the right ones is the project owner's judgment, which is what the item was for
---

**Problem.** `README.md` has no stated audience or scope, so every session that
touches it applies its own, and the result is 236 lines that read as accumulated
implementation notes. `PL-N092` (rewrite README as a human-readable
introduction) names the symptom but not the target: "human-readable
introduction" does not by itself say who the reader is or where the boundary
with `docs/MODEL.md` falls, which is why a rewrite started against it would be
one more session's guess.

**Why it matters.** This is the file a first-time reader meets, and the project
owner has stopped README work over it (2026-09-05). Until the audience and the
boundary are fixed, no rewrite can be judged right or wrong, so no rewrite
should start — `PL-QTN6` (freeze README edits) blocks both `PL-N092` and
`PL-RCTQ` on this item.

## Decision, 2026-09-05

### 1. Who is the reader? — answered by the project owner

Two audiences, both trained in science, medicine and/or code. Neither is a
general-public reader, so the README may assume domain literacy and should not
explain anesthesia or programming from first principles.

- **A — the contributor.** Interested in both anesthesiology and code, and
  considering working on the project. Needs to know what it is, whether the
  science is sound, how it is built, and how to get it running.
- **B — the user.** No interest in the code; wants to use the program as a
  simulator, most plausibly for teaching. Needs to know what it does, what it
  is not for, and how to get it.

**Consequence, and it constrains the rewrite: audience B cannot be served
today.** There is no packaged build. Running the simulator requires `uv` and a
clone, and `ROADMAP.md` puts packaging, signing and installers explicitly out
of scope for now (item 23, "add packaging, signing, and distribution work for
shipping the app"). So the README addresses audience B honestly — what the
simulator is, what it is not for, and that it is not yet distributed as an
application, with a link to the roadmap — rather than offering a setup path
that audience cannot complete. Writing install steps as if B could follow them
would be the same defect as a plausible-looking wrong number: it reads as an
answer and is not one.

### 2. Where is the boundary with `docs/MODEL.md`? — decided from the standards below

**The rule: if changing the model, a constant, or a parameter set would make
the sentence wrong, it belongs in `docs/MODEL.md`.** The README carries what a
reader needs in order to decide and to start; `docs/MODEL.md` carries every
statement whose truth is tied to a model version.

This is deliberately sharper than the candidate rule this item was captured
with ("every quantitative claim lives in `docs/MODEL.md`"), which was too
strong: "a single reference adult patient" and "volatile agents only" are
quantitative, decision-relevant, and belong on the front page. Version-coupled
is the property that matters, not numeric. The test is decidable by a reader
with the diff in front of them, which is what the previous formulation was not.

It also disposes of the sentence that prompted `PL-N092` — display precision
"is the resolution the numerical method supports" is true only of the current
numerical method, so it is `docs/MODEL.md`'s.

### 3. Does it carry current status? — decided: capability, not version

`PL-Z4GF` removed a version number from the "Current status" heading because it
went stale every release, and the same argument reaches the rest of the
section. But dropping status entirely fails Lee 2018's rule 6, that a reader
must be able to tell which version of the software the documentation describes.

Both are satisfied by stating **capability rather than version**: a short
paragraph on what the simulator models today and what it does not, with a
relative link to `ROADMAP.md` for the milestone map. Capability changes across
milestones; version numbers change every release. No version string, and no
restatement of the roadmap table.

## The standards this was decided against

Consulted 2026-09-05 rather than recalled, per `CLAUDE.md`. Recorded here so
`PL-N092` needs no network to be worked.

- **GitHub, "About the repository README file."** "A README should only contain
  information necessary for developers to get started using and contributing to
  your project." Use **relative** links for files in the repository — "absolute
  links may not work in clones." A `CITATION.cff` at the root is parsed by
  GitHub into APA and BibTeX citation snippets. README, license, citation file
  and contribution guidelines together communicate what the project expects.
- **JOSS review criteria.** A **statement of need** must "clearly state what
  problems the software is designed to solve and who the target audience is" —
  which is this item's question 1, treated as a documentation requirement
  rather than a preference. Also required: installation instructions with a
  stated dependency list; example usage; functionality documentation;
  automated tests or described manual verification; and community guidelines
  covering how to contribute, report issues, and seek support.
- **Lee BD, "Ten simple rules for documenting scientific software," PLoS Comput
  Biol 2018;14(12):e1006561** (doi:10.1371/journal.pcbi.1006561). Rule 4: the
  README "acts like a homepage"; assume it is "the only documentation your
  users read", so it carries install and configuration, where the full
  documentation lives, the license, how to test, and acknowledgments. Rule 3: a
  quickstart, because "if people must spend a long time figuring out how to use
  your software, they're likely to give up." Rule 6: make the version the
  documentation describes unmistakable. Rule 10: tell people how to cite it.

GitHub and Lee pull in opposite directions — "only what is needed to get
started" against "assume it is the only thing they read." The boundary rule in
section 2 is the resolution: everything needed to decide and to start goes in,
and nothing whose accuracy is coupled to a model version.

**Done when.** The audience, the `docs/MODEL.md` boundary and the status
question are recorded in this item's body, `PL-N092` is unblocked and its brief
restated against them, and `.claude/rules/readme-hold.md` is deleted in the
commit carrying the first README change.

**Closing note.** The first two are done here. `PL-N092` was unblocked by this item and then deferred by the project owner to `PL-XYRN` (decide when the repository goes public) the same day - a timing decision, not a reopening of anything settled here.

The first two are done here. The freeze file is deliberately
**not** deleted by this item: `.claude/rules/readme-hold.md` says it goes in the
commit carrying the first README change, which is `PL-N092`'s, so `README.md`
stays frozen until that rewrite actually runs.
