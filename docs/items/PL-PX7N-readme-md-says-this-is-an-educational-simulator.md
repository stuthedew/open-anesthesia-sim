---
id: PL-PX7N
title: README.md says 'This is an educational simulator, not a medical device', the device-status claim PL-32QH removed from docs/MODEL.md's Intended use because the project makes no regulatory claim; say what it is not intended for instead
priority: P2
effort: S
status: done
classes: defect, docs
feature: model-md-structure
milestone: v0.6.19
touches: README.md
added: 2026-11-16
closed: 2026-11-22
pr: 2212
payoff: An educator reading the README meets the same intended-use statement as docs/MODEL.md, with no claim about regulatory status that the model document says the project does not make.
verify: grep -qF 'This is a teaching simulator.' README.md
---

**Problem.** README.md says 'This is an educational simulator, not a medical device', the device-status claim PL-32QH removed from docs/MODEL.md's Intended use because the project makes no regulatory claim; say what it is not intended for instead

**Checked 2026-11-22**, at `d4e8200c`. `grep -n 'medical device' README.md`
printed line 13: "**This is an educational simulator, not a medical device.**"
The same sentence was in `README.md` at the Gate 3 freeze (`0947408`). The rest
of the warning box (lines 13 to 16) states what the simulator is not for and is
already in the form `docs/MODEL.md` § "Intended use" now uses.

**Why it matters.** "Not a medical device" is a claim about regulatory status.
`docs/MODEL.md` § "This is an engineering bar, not a regulatory status" says the
project makes no such claim, and `PL-32QH` (the device-status contradiction in
`docs/MODEL.md`) removed the same claim from § "Intended use" for that reason.
The README is the first page an educator or trainee reads, so it is where the
two documents now disagree in front of the reader.

**Done when.** The warning box at the top of `README.md` says what the
simulator is not intended for, in the terms of `docs/MODEL.md` § "Intended use"
(clinical prediction, dosing, monitoring a patient, or any other use as a
medical device), and no sentence in `README.md` states the simulator's device
status. The box still says that no displayed value should guide a real
patient's care and that every value is a model output, not a measurement.

**Generator check.** The fact is the project's intended use and its regulatory
claim, which `docs/MODEL.md` § "Intended use" states and `README.md` copies.
One-off: `PL-32QH` fixed one of the two copies, and this item was filed in the
commit that closed it as the copy it left, so it is not a fix that failed to
hold. No head's `misread:` states this fact.

**Done 2026-11-22.** The warning box now opens "**This is a teaching simulator.**" and says it is not intended for clinical prediction, dosing, monitoring a patient, or any other use as a medical device, in the words of `docs/MODEL.md` § "Intended use". It still says that nothing it displays should guide a real patient's care and that every value is a model output. Files checked for another device-status claim: `README.md` (none left, by `grep -n -i 'medical device\|regulat' README.md`), and every `*.py`, `*.md` and `*.json` file outside `docs/items/` by `grep -rn -i "not a medical device"`, which found only two item titles quoted in `ROADMAP.md`'s frozen gate list.
