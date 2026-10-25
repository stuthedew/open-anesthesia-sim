---
id: PL-X9K0
title: docs/MODEL.md says the direction of circuit-wall absorption rules it out as a cause of desflurane's too-fast elimination, but a store that slows the washout and that the model lacks would move the model toward the published 0.140, so the direction alone rules nothing out
priority: P1
effort: S
status: done
classes: science
feature: model-spec-accuracy
touches: docs/MODEL.md, tests/reference/test_published_wash_in_and_elimination.py
added: 2026-10-25
closed: 2026-10-25
pr: 1819
payoff: docs/MODEL.md no longer teaches that a store which slows the washout cannot explain a model that washes desflurane out too fast, and it names the measured circuit and the published apparatus as what rules circuit-wall absorption out.
verify: grep -q 'The direction does not rule it out, because a store that this model leaves' docs/MODEL.md && grep -q 'PL-X9K0' tests/reference/test_published_wash_in_and_elimination.py
---

**Problem.** `docs/MODEL.md` § "Desflurane's residual, and why the parameter
file was not changed" strikes circuit-wall absorption on two grounds. The
first is Targ, Yasuda and Eger's measurement of a real circle system, which
found desflurane's washin and washout close to the ideal exponential. The
second, in the paragraph headed "The direction rules it out independently",
is an argument from direction. It says a wall gives agent back during the
washout, holds the inspired fraction up and slows the alveolar fall. Since
the residual is the model washing desflurane out too fast, it says a
mechanism that can only slow a washout cannot produce it.

The argument is backwards. The residual is measured with the apparatus
removed: the model gives a five-minute $`F_A/F_{A0}`$ of 0.0935 against the
published 0.140. A wall in the published apparatus is a store the model
lacks. It would hold the real inspired fraction up and raise the published
ratio above what an inert apparatus gives. So it would produce a residual of
exactly this sign, and adding it to the model would move 0.0935 toward 0.140.
The candidate table's own sixth row shows the same direction: returning agent
to the inspired gas in the published apparatus, at $`F_I/F_A`$ = 0.30, does
reach 0.140.

The same error appears in three more places on the branch that found it:

- the candidate table's wall row, whose "What reaching 0.140 takes" cell says
  "nothing it can supply";
- the sevoflurane and isoflurane bullet, which calls its own (correct)
  argument "the same directional argument that strikes the candidate for
  desflurane";
- `test_a_larger_circuit_can_only_slow_the_elimination` (`PL-P1P6`), whose
  docstring and failure message present it as pinning the desflurane ruling.

**Why it matters.** The conclusion survives. The measurement strikes the
candidate on its own, and the section says so. But a reader who follows the
stated reasoning learns a wrong rule: that a slowing store cannot explain a
too-fast model. The same rule, applied to any later candidate, would strike
the right answer.

**Found by.** The prose reviewer of pull request 1819 (close-out step 8)
flagged it on 2026-10-25, and blind review pass 1 found it independently in
the same hour. Both readings were checked against the section's own numbers
before this item was filed.

**Where.** `docs/MODEL.md` (the direction paragraph, the wall row of the
candidate table and the sevoflurane and isoflurane bullet) and
`tests/reference/test_published_wash_in_and_elimination.py`
(`test_a_larger_circuit_can_only_slow_the_elimination`).

**Done when.** The direction paragraph says the direction favours the
candidate for desflurane and that the measurement strikes it. The table row
and the sevoflurane and isoflurane bullet agree with it. The test's docstring
and failure message say which argument the direction supports: the one for
sevoflurane and isoflurane, which the shipped circuit already washes out too
slowly.

**Done 2026-10-25.** The direction paragraph now says that a store this model
leaves out would move the comparison toward the published value, as the
sixth row's rebreathing does. It names the two grounds that strike the
candidate instead: Targ, Yasuda and Eger's measurement of a real circuit, and
the published apparatus, which had no circle system. The wall row's cell now
reads "the right direction, as in the sixth row". The sevoflurane and
isoflurane bullet says the direction rules the candidate out there because the
departure it would explain is the model washing out too slowly. The test's
docstring and failure message say the direction supports the sevoflurane and
isoflurane ruling and not the desflurane one. No number changed, and the
section's conclusion, that the residual's cause is not identified, still holds.
