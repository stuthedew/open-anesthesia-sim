---
id: PL-T7QR
title: docket next ranks every sound root-cause-of at the generator tier, so the recurrence test the project owner ratified on 2026-09-21 has no carrier: a recorded-but-spent generator is still offered above every band and the session has to demote it by hand
priority: P2
effort: M
status: done
classes: infra
feature: generator-machinery-rank
milestone: v0.5.0
touches: CLAUDE.md, subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/README.md, subprojects/docket/tests/test_model.py, subprojects/docket/tests/test_plan.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_cli.py, tools/generator_check.py, .claude/skills/docket/modes/picking.md
added: 2026-09-21
closed: 2026-09-21
pr: 836
payoff: a generator can be recorded for the audit without being ranked above every band, so the count stays honest and the tier stays scarce
verify: uv run pytest subprojects/docket/tests/test_model.py subprojects/docket/tests/test_plan.py subprojects/docket/tests/test_cli.py -k "verdict or spent or generator" -q
---

**Problem.** docket next ranks every sound root-cause-of at the generator tier, so the recurrence test the project owner ratified on 2026-09-21 has no carrier: a recorded-but-spent generator is still offered above every band and the session has to demote it by hand

**Where it comes from.** `PL-J870`'s decision, ratified 2026-09-21: the count of
three or more items decides whether `root-cause-of:` is *recorded*; expected
recurrence - whether the store is still handing the mechanism new members -
decides whether it *ranks* above every band but `P0`. `CLAUDE.md` now says so.
`bin/docket next` does not.

**What the code does today.** `plan.recommend` builds its generator map from
startable items carrying a sound `root-cause-of:`, and `model.is_generator`
defines sound as "three or more distinct ids the store knows". Nothing in
either reads recurrence, so every recorded generator ranks at the tier, and a
session that judged one spent has to demote it by hand - or, worse, declines to
record it at all to keep the ranking honest, which loses the audit fact the
count was supposed to guarantee. That trade is exactly what the ratified
decision was meant to remove.

**The design question, which is the work.** How the judgment reaches the tool
without the tool making it. `CLAUDE.md` refuses to script the judgment half, so
this is not "infer still-generating from `recurrences:`". The candidates:

- a field the recording session writes, the way `impairs-generators:` carries
  prose rather than `yes`, with `docket check` refusing an empty claim;
- a default, so that recording alone no longer ranks and the tier is opt-in;
- nothing new - `plan` reads the item's own prose, which is the option to
  refuse, because that is inference over judgment.

Whichever lands, `plan.recommend`'s docstring is the place the reasoning goes;
it already carries the 2026-09-17 placement argument and would otherwise
describe a rule the code no longer follows.

**Zero blast radius today, which is why this is not urgent.** All 11 recorded
`root-cause-of:` heads and the 1 `impairs-generators:` head are closed, and a
closed item is never startable, so nothing in the store ranks at the generator
tier right now. The first item to carry the field under the new rule is the
one that would be mis-ranked.

**Why it matters.** The generator tier is the only rank that outranks a
`safety`-classed `P1`, so what sits in it has to be scarce and deliberate. With
the tool ranking on the count alone, a session facing a three-item cluster it
judges spent has two bad options: record the field and let it outrank a safety
item, or withhold the field and lose the audit fact. Both were observed on
2026-09-21 over `PL-9HD1`, which is what produced `PL-J870` in the first place.

**Done when.** `bin/docket next` ranks a recorded generator at the tier only
when the recording session has claimed it is still generating, and ranks a
recorded-but-spent one on its own band - with the claim carried by the store
rather than inferred from prose, and `bin/docket check` refusing an empty or
absent claim the way it refuses an unsound `root-cause-of:`. `plan.recommend`'s
docstring states the two tests, and `test_plan.py` covers a spent generator
ranking on its band.
