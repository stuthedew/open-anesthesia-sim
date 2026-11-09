---
id: PL-B8YN
title: docs/MODEL.md Known limitations, under One reference condition, says the liquid-equivalent consumption figure is planned and nothing on screen shows the conversion's result yet, but the agent cost panel and the compartment schematic now show amounts in millilitres of liquid
status: dropped
added: 2026-11-07
closed: 2026-11-09
reason: Duplicate of PL-N3SK, which names the same stale sentence in Known limitations; checked 2026-11-09, the sentence is still there
---

**Problem.** docs/MODEL.md § "Known limitations", under "One reference condition", says that the liquid-equivalent consumption figure is planned and that nothing on screen shows the conversion's result yet. The agent cost panel and the compartment schematic now show amounts in millilitres of liquid.

**Found 2026-11-07 while restructuring `docs/MODEL.md` (`PL-BSMF`).** The
sentence on the 5.8 % store bias reads: "It would matter only where an amount is
converted out of the litre unit, as the liquid-equivalent consumption figure
planned under § "Planned milestones" item 28 will be. The code for that
conversion exists, and nothing on screen shows its result yet." Elsewhere the
same document says the agent cost panel writes its delivered amount as "mL of
liquid" (§ "The compartment schematic: what its heights, amounts and share bar
assert"). It also says the agent cost display reads the amount and the
vapour-to-liquid ratio from one snapshot of the run (§ "Agent amounts in
millilitres, and the cost"). So the bias now affects a displayed figure, and
the limitation should say which figure and by how much. The fix corrects a
fact, so it can be made before the document's line edit.

**Checked 2026-11-09:** `grep -n 'nothing on screen' docs/MODEL.md` finds the
sentence in § "Known limitations" (lines 12162 to 12166). It says the
liquid-equivalent figure is "planned under § "Planned milestones" item 28" and
that "nothing on screen shows its result yet". § "Agent amounts in
millilitres, and the cost" (from line 8504) says the agent cost display shows
the delivered total in millilitres of liquid, and that the stored total is
refused in liquid because of this same 5.8% bias.
So no displayed figure carries the bias, contrary to the paragraph above. What
is stale is only "planned" and "nothing on screen".

`PL-N3SK` (filed 2026-11-05 from the copy editor's structure read) names the
same sentence and the same contradiction, so this later capture is dropped in
its favour. The reading above, and the generator check below, belong to that
item.

**Generator check.** An instance of `PL-4FBP`'s fact, the link between a
document sentence and the tree fact it restates, filed after that head closed
on 2026-09-19. The sentence states what the interface shows, with "yet" in
place of a date or a named test, and went stale when the cost display shipped.
