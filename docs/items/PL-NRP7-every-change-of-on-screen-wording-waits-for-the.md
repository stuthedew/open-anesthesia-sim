---
id: PL-NRP7
title: Every change of on-screen wording waits for the owner, because a session may not rewrite the approved wording list, when only a change of clinical meaning needs a clinician
priority: P2
effort: S
status: done
classes: infra, docs
milestone: v0.6.20
touches: tests/integration/test_interface_wording.py, docs/ARCHITECTURE.md, .claude/skills/pull-request/SKILL.md, docs/maintainer.md
added: 2026-11-22
closed: 2026-11-22
pr: 2230
payoff: A change of on-screen wording that alters no clinical meaning, such as a document pointer in a notice, merges on green, and the owner is asked only about wording whose clinical meaning changes.
verify: ! grep -qF 'until a person approves' tests/integration/test_interface_wording.py
---

**Problem.** Every change of on-screen wording waits for the owner, because a session may not rewrite the approved wording list, when only a change of clinical meaning needs a clinician

**What happens now.** `tests/integration/test_interface_wording.py` compares
every string on screen with `approved_interface_strings.json` (`PL-86VL`,
`PL-4G79`), and its docstring says a change fails "until a person approves
it". Sessions read "a person" as the owner, and auto mode refuses a session
that sets `APPROVE_INTERFACE_WORDING=1` after a real change of wording. So on
2026-11-22 `#2222` waited for the owner over two fault notices whose source
pointer changed from `(docs/MODEL.md, "Concentrations")` to
`(docs/VERIFICATION.md, "Concentrations")`, which no clinician needs to judge.
The owner asked to reconsider the check and to research whether he should be
approving (project owner, 2026-11-22, "reconsider the wording check I
approved. Research best practice on whether I should be approving").

**What the sources say.** Each was read in this session on 2026-11-22.

1. FDA, *Deciding When to Submit a 510(k) for a Software Change to an Existing
   Device*, 25 October 2017, document 1500055,
   https://www.fda.gov/media/99785/download, read in full. Every change gets a
   risk-based assessment and is documented (Guiding Principle 2, p. 6;
   Principle 8, p. 8). The depth of review follows the risk: "Cosmetic
   Changes – No Change to Functionality" are "changes made to the appearance of
   the device that do not impact the clinical use of the device", and are
   documented to file (Section VI, p. 16). A change that "could significantly
   affect clinical functionality or performance specifications" gets the
   heavier route (Question 4, pp. 13-14), and a changed warning is described
   explicitly (Principle 9, p. 9). This simulator is not a device, so the
   guidance is used only for its tiering of review by clinical effect.
2. FDA, *Applying Human Factors and Usability Engineering to Medical Devices*,
   reissued 3 August 2026 from 3 February 2016,
   https://fda.gov/media/80481/download, pages 1-15 read verbatim. Displays and
   labels are part of the user interface (Section 2, p. 2), and the effort is
   set by harm: "You should categorize the user tasks based on the severity of
   the potential harm that could result from use errors" (Section 6.1, p. 12),
   with a critical task defined as one whose error "would or could cause
   serious harm" (Section 3, p. 3).
3. IEC 62304:2006+AMD1:2015, consolidated edition 1.1, the publisher's preview
   at https://webstore.ansi.org/preview-pages/IEC/preview_iec62304%7Bed1.1%7Den.pdf.
   The introduction says the standard "does not specify an organizational
   structure for the MANUFACTURER or which part of the organization is to
   perform which PROCESS, ACTIVITY, or TASK". The bodies of clause 7.4 ("RISK
   MANAGEMENT of software changes") and clause 8.2 ("Change control") are not
   in the preview and were not read.
4. INACSL Standards Committee, *INACSL standards of best practice:
   Simulation design*, Clinical Simulation in Nursing 2016;12(S):S5-S12,
   doi:10.1016/j.ecns.2016.09.005, read in full. Criterion 4: "Use subject
   matter experts to strengthen validity of the simulation scenario and the
   critical performance measures." Criterion 5: "cases or scenarios should be
   reviewed by subject matter expert(s) and pilot tested before use with
   participants." The 2021 edition (Clinical Simulation in Nursing 2021;58:66,
   doi:10.1016/j.ecns.2021.08.018) subsumes it, and its Simulation Design
   criteria could not be read.

Together they put the expert's sign-off on content that carries clinical
meaning, and put every other change under a recorded check by whoever makes
it. None asks a clinician to approve every string an interface shows.

**Decision.** Keep the test and its list, because the list makes every change
of wording visible in the pull request's diff, which is the record the FDA
guidance asks for. The session that changes the wording checks each changed
string, rewrites the list, and decides the pull request's `Owner-read:` record
as for any other simulator change. A change of wording needs the owner when it
changes clinical meaning: the name, label or unit of a clinical value; whether
a value reads as modeled or measured; what a warning, halt, refusal or stated
limitation tells a learner about a value or what to do; or any wording that
reads as a recommendation. Any other change merges on green, such as a
layout notice, a document pointer, punctuation, a corrected typo, or the name
of a control or View that names no clinical value. Where a change fits both,
it waits for the owner. The
forbidden-phrase checks in `tests/integration/simulation_view/` still run on
every change. This session recommends it on the sources above. It reopens
how `PL-86VL` was read, and it changes a rule sessions run under, so it waits
for the owner's answer before it merges.

**Why it matters.** The owner's attention goes to the wording only a
clinician can judge, and a wording change with no clinical effect no longer
holds a pull request for hours. A check that holds every change trains a
reader to approve without reading, which is how a misleading change would get
through.

**Done when.** The test's docstring and failure message, `docs/ARCHITECTURE.md`, the
`pull-request` skill and `docs/maintainer.md` say that the session rewrites the
list and that only a change of clinical meaning waits for the owner, naming
the four kinds above.

**Generator check.** Not a generator: one pull request held so far (`#2222`).
The fact sessions misread is who "a person" in the test's docstring is, and
this item states it where the test is read.

**Blind review, 2026-11-22.** One pass found three things. It held that the
change needs the owner's answer, because it changes a rule sessions run under
that he did not ask for in his own words; the pull request now records that
and asks him. It found that a control's name can also name a clinical value,
so the text now says the kinds that wait for the owner win. And it found the
list copied into `docs/maintainer.md`, which now points to the docstring.

**Owner's answer, 2026-11-22.** "Agree with recs", to the question whether a
session approves on-screen wording changes itself and brings him only those
that change clinical meaning (project owner, 2026-11-22, ratified, over
keeping every wording change for his approval).
