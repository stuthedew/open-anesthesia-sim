---
id: PL-B8YN
title: docs/MODEL.md Known limitations, under One reference condition, says the liquid-equivalent consumption figure is planned and nothing on screen shows the conversion's result yet, but the agent cost panel and the compartment schematic now show amounts in millilitres of liquid
status: untriaged
added: 2026-11-07
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
