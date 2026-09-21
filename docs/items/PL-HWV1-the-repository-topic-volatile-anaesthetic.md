---
id: PL-HWV1
title: The repository topic volatile-anaesthetic contradicts PL-XF89's settled decision twice - volatile belongs only on pyproject.toml's release-level description, and the British anaesthetic was deliberately replaced by the US spelling everywhere else
priority: P3
effort: S
status: dropped
classes: docs
feature: project-introduction
touches: docs/items/PL-HWV1-the-repository-topic-volatile-anaesthetic.md
added: 2026-09-21
closed: 2026-09-21
reason: withdrawn on the project owner's challenge: volatile and inhaled are interchangeable in clinical use, the objection applied a prose-framing rule to a keyword index, and its premise that PL-XF89 confined volatile to pyproject.toml is false - docs/MODEL.md is titled Volatile-agent and is correct to be
payoff: the project's public topic list stops contradicting the scope word and spelling PL-XF89 settled
not-delegable: the deliverable is a GitHub repository setting no session can write; only the project owner can apply it
---

**Problem.** The repository topic volatile-anaesthetic contradicts PL-XF89's settled decision twice - volatile belongs only on pyproject.toml's release-level description, and the British anaesthetic was deliberately replaced by the US spelling everywhere else

**What is set.** Nine topics, applied by the project owner on 2026-09-21 and
verified through `GET /repos/stuthedew/open-anesthesia-sim/topics`:
`anesthesia`, `anesthesiology`, `inhaled-anesthetics`, `medical-education`,
`medical-simulation`, `pharmacokinetic-modeling`, `pharmacokinetics`, `python`,
`volatile-anaesthetic`. Eight are consistent with each other and with the tree.
The ninth is this item.

**Why it matters, and why it is a finding rather than tidiness.** `PL-XF89`
settled both halves of this, and a repository topic is a project-level surface
where both apply:

1. **Scope word.** That decision put **inhaled** on the surfaces describing the
   *project* - `README.md`'s opening and the GitHub "About" field - and confined
   **volatile** to `pyproject.toml`'s `description`, which describes the
   *release*, on the reasoning that "a package `Summary` is metadata about the
   artifact it ships with". Topics describe the project, so the settled word
   here is `inhaled` - and `inhaled-anesthetics` is already in the set,
   which is what makes this one redundant as well as off-decision.
2. **Spelling.** The same decision replaced the British *anaesthetic* in the
   "About" field with "the US *anesthetic* the package name, the module, the
   repository name and every document in the tree use". This topic reintroduces
   it, and is the only British spelling among the nine - `anesthesia` and
   `anesthesiology` beside it are US-spelled.

**The one reading under which it is deliberate, which is why this asks rather
than asserts.** Much of the field's literature is British-spelled - *Anaesthesia*,
the *BJA* - so carrying one British-spelled topic to reach those searchers is a
defensible choice rather than a slip. If that was the intent, `volatile-anaesthetic`
is still the wrong instrument for it: the reach would come from `anaesthesia`,
the mass noun that mirrors the `anesthesia` already set, not from a singular
adjective-noun compound.

**Recommendation.** Remove `volatile-anaesthetic`. `inhaled-anesthetics` already
carries the scope on the surface where `PL-XF89` put it, so nothing is lost. If
reaching British-spelled searches is wanted, add `anaesthesia` in its place
rather than keeping this string.

**What was not measured, and must not be assumed.** Whether either spelling
reaches anyone - the repository count behind each topic - could not be obtained:
`GET /search/repositories?q=topic:...` is refused in this harness, which binds a
session to its configured repositories. So the case above rests on the recorded
decision, which is verified, and not on a count of reach, which is not. A
session with an unrestricted token should count both spellings before choosing
between "remove" and "replace with `anaesthesia`".

**Not a session's to apply.** Repository topics are a repository setting; no
`mcp__github__` tool in this harness writes them.

**Done when.** `volatile-anaesthetic` is either gone from the topic set, or
replaced by `anaesthesia`, or kept with a recorded reason that says why the
British spelling earns a place the "About" field was deliberately corrected out
of.

## Withdrawn 2026-09-21: the objection rested on a category error, and one of its premises is false

**Dropped on the project owner's challenge** - that *volatile* and *inhaled* are
synonyms in clinical use and used interchangeably. That is correct, and two
separate things above do not survive it.

**1. The scope-word half applied a prose rule to a keyword index.** `PL-XF89`
decided how three *sentences* should read. Repository topics are not a sentence:
they are a set of search keys, where overlapping and even spelling-variant
entries are the point rather than a contradiction. Someone searching
`volatile` is looking for precisely what this release models today - three
volatile agents - so the topic reaches its reader accurately. Nothing about a
keyword list makes `inhaled-anesthetics` and a volatile-flavoured key mutually
exclusive, and the brief above treated a discovery surface as a
self-description surface.

**2. "Confined volatile to `pyproject.toml`" is false, and the tree says so.**
`docs/MODEL.md` is titled "**Volatile-agent** patient uptake and distribution
model" and its "Intended use" opens "This is a teaching simulator for
**volatile-agent** uptake and distribution." That is a reader-facing simulator
document, not the package summary. `PL-XF89`'s decision governed the three
self-description statements only; this brief restated it as a tree-wide rule it
never was.

**And `docs/MODEL.md` is *right* to say volatile, which shows the scheme is
coherent rather than violated.** Under `PL-XF89`'s own logic a document
describing what is *implemented* takes the narrower word, and `docs/MODEL.md`
excludes nitrous oxide explicitly - "The alveolar volume is held constant, and
that is what excludes nitrous oxide". So the tree has three surfaces doing three
jobs: project-level prose says *inhaled*, implementation-level prose says
*volatile*, and topics are keys rather than prose. No finding remains.

**What the taxonomy does and does not license, recorded so this is not
re-litigated.** Inhaled anesthetics subdivide into the volatile agents - liquids
at room temperature, delivered by vaporizer - and the gaseous agents, nitrous
oxide and xenon, which are gases at standard temperature and pressure and come
from cylinders through flowmeters. So `volatile` is a proper subset of `inhaled`
rather than a synonym *as a category*, and the two are nonetheless
interchangeable in clinical speech, which is the usage that governs a search
key. A future session must not reopen this on the subset argument alone: the
subset relation is why `README.md` says *inhaled*, and it says nothing about
what belongs in a topic list.

**The residue, and why it is not worth an item.** `volatile-anaesthetic` is the
only British spelling among the nine and is a singular adjective-noun compound
rather than a mass noun, so it is probably a sparse topic string. Both halves of
that were unmeasurable here - `GET /search/repositories?q=topic:...` is refused
to a session bound to its configured repositories - and under the search-key
framing a British spelling is reach rather than a defect. An objection that
cannot be measured and would not matter if it could is not a finding.
