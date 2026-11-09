---
id: PL-56DQ
title: docs/references/yasuda-1991-anesthesiology-desflurane-isoflurane-halothane-kinetics.md's page 494 entry, 'The pulmonary elimination clearances and the total body clearances', names a topic, not a fact: give the values with units, or the method (copy editor structure read, 2026-11-07)
priority: P2
effort: S
status: ready
classes: defect, docs
feature: references-structure
touches: docs/references/yasuda-1991-anesthesiology-desflurane-isoflurane-halothane-kinetics.md
deferred-from: v0.7.0 - a new problem: the note did not exist at the freeze (817a4d88); 0d8ad8f9 (PL-4QCJ, 2026-10-25) created it with the page 494 entry as written
added: 2026-11-07
payoff: the clearances docs/MODEL.md argues from are recorded beside their page and checked against it, so a reader can verify the dead-space argument at its source
verify: grep -qiF 'l/min' docs/references/yasuda-1991-anesthesiology-desflurane-isoflurane-halothane-kinetics.md
---

**Problem.** docs/references/yasuda-1991-anesthesiology-desflurane-isoflurane-halothane-kinetics.md's page 494 entry, 'The pulmonary elimination clearances and the total body clearances', names a topic, not a fact: give the values with units, or the method (copy editor structure read, 2026-11-07)

**Checked 2026-11-09:** `grep -n 'Page 494' docs/references/yasuda-1991-anesthesiology-desflurane-isoflurane-halothane-kinetics.md` finds the entry, which still reads in full "The pulmonary elimination clearances and the total body clearances." It gives no value, unit or method. `docs/MODEL.md` § "Desflurane's residual, and why the parameter file was not changed" quotes values for these clearances from the paper: desflurane 4.11 ± 0.45, isoflurane 3.94 ± 0.34 and halothane 3.94 ± 0.33 L/min, as V_1 k_10. The note holds no copy of them. The note also says that the page 494 facts were recorded on 2026-09-13 and not checked against the paper again. No wrong value was found, so this is an incomplete record and not a wrong one. If the page shows a value different from the one `docs/MODEL.md` quotes, that difference is a `science` finding to file at `P1`.

**Why it matters.** This note is where the repository records what it takes from this paper, with pages. A reader checking the clearances that `docs/MODEL.md` uses cannot find them in the note, and the values have not been checked against the page since they were first recorded.

**Done when.** Page 494 is read again from the private corpus. The entry gives the pulmonary elimination clearances and the total body clearances as the page prints them, with units, mean ± SD and n, or says where on the page each appears. The values are checked against those in `docs/MODEL.md`, and the reading date is recorded.

**Generator check.** One-off: a finding from the `docs/references/` structure read (2026-11-07).
