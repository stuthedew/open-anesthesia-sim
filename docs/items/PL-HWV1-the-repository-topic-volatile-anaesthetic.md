---
id: PL-HWV1
title: The repository topic volatile-anaesthetic contradicts PL-XF89's settled decision twice - volatile belongs only on pyproject.toml's release-level description, and the British anaesthetic was deliberately replaced by the US spelling everywhere else
priority: P3
effort: S
status: ready
classes: docs
feature: project-introduction
touches: docs/items/PL-HWV1-the-repository-topic-volatile-anaesthetic.md
added: 2026-09-21
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
