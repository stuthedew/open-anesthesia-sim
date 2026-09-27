---
id: PL-YD2V
title: Supported run length and the validation section's caveat 4 bound the slow tail on metabolism and fat flow alone, but the fourth compartment this model lacks is the largest term in Yasuda 1991's measured washouts from about hour 2-3 to hour 21-29, inside the 24 h envelope, and neither passage says so
priority: P1
effort: S
status: done
classes: science, docs
feature: late-washout-evidence
milestone: v0.5.15
touches: docs/MODEL.md, docs/items/PL-KK1Q-compare-this-model-s-washout-over-the-first-24.md, tests/reference/test_published_wash_in_and_elimination.py, src/anesthesia_sim/core/supported_ranges.py
added: 2026-09-26
closed: 2026-09-27
pr: 1167
payoff: a reader of Supported run length learns that the washout tail lacks its largest measured term from about the third hour, not only past the 24-hour boundary
verify: grep -qF 'PL-YD2V' docs/MODEL.md
---

**Problem.** Supported run length and the validation section's caveat 4 bound the slow tail on metabolism and fat flow alone, but the fourth compartment this model lacks is the largest term in Yasuda 1991's measured washouts from about hour 2-3 to hour 21-29, inside the 24 h envelope, and neither passage says so

**Found 2026-09-26 while working `PL-WMCJ`.** The figures are in `docs/MODEL.md` § "Known limitations", the intertissue-diffusion note that item added, which carries the table, the pages of both Yasuda 1991 papers read from the private reference corpus, and how each ratio and crossing time was computed.

**Premise checked 2026-09-27.** § "Supported run length" ("What bounds it is
what this model omits. Metabolism, first of all...") and caveat 4 under §
"Published wash-in and elimination validation test" name metabolism and the fat
group's flow as what the slow tail lacks, and neither names the fourth
compartment. "Known limitations" says "The two omissions above are what bound
the supported run length" in the paragraph before the intertissue-diffusion
note `PL-WMCJ` added.

**Why it matters.** § "Supported run length" is where a reader learns how long
a run can be trusted, and it frames the omissions as mattering over days, past
the boundary. On the published mean coefficients the term this model lacks is
the largest in the measured washout from 1.8-3.1 hours after a 30-minute
administration until 20.7-29.4 hours, so inside the envelope the tail already
misses its largest measured component, and a reader trusting the section trusts
that stretch of the trace further than the evidence goes.

**Done when.** § "Supported run length" and caveat 4 each say that inside the
supported 24 hours the tail lacks the fourth compartment's term, the largest in
the measured washout over the hours "Known limitations" gives, pointing at that
note; the "two omissions" paragraph in "Known limitations" says which omissions
bound the run length and which the tail inside it; and `docs/MODEL.md` cites
`PL-YD2V` where it changes. Whether the 24 hours should move is `PL-KK1Q`'s to
raise, once its measurement gives the size.

**Note from `PL-HBH2`, 2026-09-27.** The two passages this item rewrites still
restate the fat flow as "about twice the reachable resting measurement", the
PET reading alone; `PL-HBH2` made the fat-perfusion paragraph two-sided (the
Yasuda washout fits put the flow at or a little above the stored figure), so
carry that reading into both restatements as well.

**Handoff, 2026-09-27, from the thread that closed `PL-HBH2` (#1164).** It
claimed this item on `claude/project-thread-adxyd4`, restarted from
`origin/main` at the #1164 merge, and stopped for context length before
editing anything; a fresh thread continues on that branch. What it had worked
out, so nothing is re-derived:

- **The three passages**, by their opening words in `docs/MODEL.md`:
  § "Supported run length", the paragraph "**What bounds it is what this model
  omits.** Metabolism, first of all."; § "Published wash-in and elimination
  validation test", caveat 4, "*This model has no metabolism, which is why
  five minutes is the limit.*"; and § "Known limitations", the paragraph
  "**The two omissions above are what bound the supported run length.**". The
  intertissue-diffusion note's bullet "**The late washout loses its largest
  measured term.**" already gives the hours and is what the three should point
  at, not restate at length.
- **What each should say.** The first two: inside the supported 24 hours the
  tail already lacks its largest measured term, the fourth compartment (fat
  reached by intertissue diffusion, which this model has no counterpart for),
  whose exponential is the largest in Yasuda 1991's measured washouts from
  about 1.8-3.1 h after a 30-minute administration until 20.7-29.4 h; all else
  equal the modelled tail falls faster from about the third hour, and how much
  is `PL-KK1Q`'s measurement. Both also restate the fat flow as "about twice
  the reachable resting measurement"; carry `PL-HBH2`'s two-sided reading
  instead (the PET depot measurement says twice, the washout fits put it at or
  a little above the stored figure, direction unsettled). The third: say which
  omissions bound the run length (metabolism; fat flow on its PET reading) and
  which the tail inside it (the fourth compartment from about the second or
  third hour; the fat flow whichever way it errs). Cite `PL-YD2V` at each
  change. The 24 hours stays: whether it moves is `PL-KK1Q`'s to raise.
- **The crossing hours were re-derived 2026-09-27 from Tables 1 and 2 of both
  papers** and match the note: for the muscle-group and fourth-compartment
  terms, $`t = \ln(A_3/A_4)/(1/\tau_3 - 1/\tau_4)`$ gives 3.1 h (sevoflurane),
  3.0 h and 2.7 h (isoflurane, each study) and 1.8 h (desflurane); for the
  fourth-compartment and fat-group terms, the same form with $`A_4, A_5`$ and
  $`\tau_4, \tau_5`$ gives 29.4, 28.7, 27.5 and 20.7 h. The coefficients are
  recorded in `PL-KK1Q`'s brief, which needs them next.
- **Procedure.** `make check` in the thread container needs the uv upgrade
  and the Qt libraries that the project memory records; the pull request
  changes `docs/MODEL.md`, so it stays unarmed for the owner's read, with one
  line on what a learner would see change (nothing on screen; the run-length
  rationale names the missing compartment); `bin/docket record N` after it
  opens; `bin/docket verify --self PL-YD2V` to `ACCEPT`.

**Closed 2026-09-27.** What changed, and where:

- § "Supported run length": the fat-flow clause of "What bounds it is what
  this model omits" now carries `PL-HBH2`'s two-sided reading, and a new
  paragraph after it says the tail inside the boundary is already missing its
  largest measured term - the fourth compartment, largest in the measured
  washout from about 1.8-3.1 h after a 30-minute administration until about
  20.7-29.4 h - that a tail without it falls faster from about the third hour,
  that how much is `PL-KK1Q`'s measurement, and that the 24 hours certifies
  nothing about the late tail inside it.
- Caveat 4 of § "Published wash-in and elimination validation test": its
  italic lead names both omissions; the body carries the two-sided fat reading
  and the fourth compartment's hours, and says the gap over those hours
  belongs to a measurement recorded beside the gate (`PL-KK1Q`), not to the
  gate, so caveat 4's refusal of the multi-day curves stands.
- § "Known limitations": the "two omissions" paragraph now says which bound
  the run length (metabolism; the fat flow on its depot reading) and which the
  tail inside it (the fourth compartment from about hour 2-3; the fat flow
  either way, as an uncertainty of up to about a factor of two in the fat
  trace's loading).
- Two mirrors kept in step, declared in `touches`: the same caveat 4 in the
  module docstring of `tests/reference/test_published_wash_in_and_elimination.py`,
  and the run-length comment in `src/anesthesia_sim/core/supported_ranges.py`,
  which still restated the one-sided fat reading `PL-HBH2` retired. Neither
  changes behaviour.
- "About one part in twenty of what remains" at five minutes, as caveat 4 now
  says: on the mean hybrid coefficients in `PL-KK1Q`'s brief, the fourth
  compartment's term at t = 5 min, $`A_4 e^{-5/\tau_4}`$, is 0.709, 1.282,
  0.762 and 1.113 (x100) against the sum of all five terms 19.4, 24.3, 14.7
  and 22.8, so 3.7%, 5.3%, 5.2% and 4.9% for sevoflurane and isoflurane
  (*Anesth Analg*) and desflurane and isoflurane (*Anesthesiology*). The
  crossing hours were re-derived the same way in this thread (3.1, 3.0, 1.8,
  2.7 h and 29.4, 28.7, 20.7, 27.5 h) and match the note.
- The 24 hours did not move. Whether it should is `PL-KK1Q`'s to raise, and
  its brief already says so.
