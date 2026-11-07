---
id: PL-D89D
title: "Cut v0.4.20: the release where four stored values' sources were read back against the publications"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
milestone: v0.4.21
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-13
closed: 2026-09-13
pr: 540
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.20"' pyproject.toml && test -f docs/releases/v0.4.20.md
---

**Problem.** Cut v0.4.20: the release where four stored values' sources were
read back against the publications.

Five items have finished since v0.4.19 and none has shipped, so `bin/docket
next` and the session-start digest ask every session to offer a release before
taking new work. One of the five is `PL-6BP6`, v0.4.19's own cut item, which is
the open gate entry `PL-KRS6` (release counts the previous release's own cut
item as releasable work) demonstrating itself; the release's real content is the
other four.

**Why it matters.** The four are one piece of work rather than a miscellany, and
the release name should say so. `PL-4YY1` recorded provenance for the circuit
volume and the default fresh gas flow, which had none. `PL-0NQ1` found the
reference patient's cited sources disagreeing on vessel-rich perfusion.
`PL-ZP7Z` found the Workbook attributing the volatile partition coefficients to
Yasuda's *Anesthesiology* abstract and to Abbott package-insert data, which is
not what the agent files say. `PL-ZDWL` re-ran the published elimination
comparison at Yasuda's own measured alveolar ventilation, which the methods text
states and this project had not read out. In every one of the four the stored
number was checked against what the publication actually says, which is the
`docs/MODEL.md` source hierarchy being exercised rather than asserted.

Filed before the cut rather than after it, per `CLAUDE.md`'s rule that
repository work taking a commit of its own is filed first: every in-flight guard
this project has matches a `PL-` id, and a release cut has none until somebody
starts one. `PL-66FP` is what the unfiled version cost - two sessions cut v0.3.7
within the hour and the second was discarded at the merge. Checked before
starting: `bin/docket release --dry-run` reported no ref carrying a cut, `main`
holds no 0.4.20, v0.4.19 is tagged on the remote at `fdb13c9e`, and of the four
live sessions on the list none is cutting a release.

**Known and accepted at the cut.** Three sessions are working and may merge
during it, so work can land inside this tag's span and be absent from its notes.
That is the open entry `PL-028F` (work landing between a cut and its merge is
inside the tag's span but absent from the release notes), a known defect with no
fix yet rather than a reason to hold the release.

**Done when.** `pyproject.toml` is at 0.4.20, `docs/releases/v0.4.20.md` exists,
`ROADMAP.md` carries the version-table row, the moved `current baseline` mark
and the baseline section, and `make check` passes.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.20 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> The second half is measured rather than asserted: every numeric value in every data file that existed at `v0.4.19` is identical at this release - all twelve partition coefficients, the eleven reference-patient parameters, every MAC and MAC-awake - and `src/anesthesia_sim/app/` and `.github/` resolve to the same tree objects. `src/anesthesia_sim/core/` is *not* byte-identical, and this release cannot make v0.4.19's claim: `PL-4YY1` moved `circuit_volume_l = 6.0` and `default_fresh_gas_flow_l_min = 4.0` out of `core/circuit.py`'s dataclass field defaults into a new `data/machines/reference_circle_system.json` - machine parameters as their own kind, beside patients and agents - changing neither value, and `AgentUptakeSystem.for_agent()` now passes both explicitly so that every scientific constant a run uses comes from a cited file. **They had been invisible to the only tool built to catch exactly this:** `tools/doc_check.py`'s `check_provenance` walks *data files* in both directions, so a constant that never entered one could not be missing from anything. The new file records that the Workbook's published circuit volume is 8.0 L against this project's 6.0, kept on the project owner's ruling of 2026-09-01 that the value is not critical, and what the departure is worth - $`\tau_C = V_C / \dot V_F`$ is 90 s here against 120 s at 8.0 L, a 25 percent shorter machine lag, which is the part of the early rise belonging to the apparatus rather than to uptake and the most-taught point about a circle system. `default_fresh_gas_flow_l_min` has no published counterpart at all, and the `provenance_gap` says so rather than leaving the silence to read as an oversight. The literals stay in `circuit.py` as defaults so a bare unit test can exercise circuit physics without loading package data, pinned to the file by a test. `PL-M85T` later made the volume a required argument and retired that test with the default. **The other three read a source and came back with a negative, which is the outcome this kind of work mostly has.** `PL-0NQ1`: `reference_adult.json` stores vessel-rich perfusion 0.76, and De Wolf et al. 2012's Table 1 - the same table all twelve partition coefficients come from - prints 75.8 / 18 / 6, which sums to 99.8. The stored value does not move and *could not*: `_perfusion_fractions_must_sum_to_one` and `core/patient.py` independently reject any set differing from 1.0 by more than `FLOW_FRACTION_TOLERANCE = 1e-12`, so a session deciding the published figure was right would discover that only after editing the file. What the difference is worth is recorded instead - $`\tau = V_i / (Q_i \lambda)`$ scales inversely with perfusion, so 0.76 against 0.758 moves the vessel-rich time constant by 0.26 percent - and the finding as relayed was corrected rather than smoothed: the review said this file cites De Wolf, and it does not; the three *agent* files do, which makes the finding sharper, since the table carrying the discrepant number is one this file never cites. `PL-ZP7Z`: the Workbook's page-168 note says its volatile coefficients are Yasuda, Targ and Eger's and, one sentence later, that sevoflurane's are "taken from the package insert and Abbott data" - and its reference 45 is `Anesthesiology 69:A615`, the 1988 ASA meeting *abstract*, not the 1989 *Anesthesia & Analgesia* paper the agent files cite. The arithmetic is close and settles nothing about the route: 1.70 x 0.65 = 1.1050 against a stored 1.1, desflurane 1.29 x 0.42 = 0.5418 against 0.54, isoflurane 1.57 x 1.3 = 2.0410 against 2.1, missed by 2.9 percent and still inside half the measurement's own standard deviation. **The tier stays at 3 and would stay there even if the attribution were confirmed** - a program's statement about its own provenance is the program talking - and the one comparison that would settle it needs Yasuda 1989's tissue:gas tables, which are in neither PubMed Central nor the private corpus. `PL-ZDWL` is the flattest negative of the three and the one that closes a question: `PL-RFLN` had left the operating-point ventilation load-bearing, both Yasuda papers were read at full text from the private corpus, and **neither publishes a ventilation at all** - it was titrated per subject to normocapnia at an end-tidal carbon dioxide of 5.5-6.5 percent rather than set to a figure, with no $`\dot V_E`$ and no $`f_A`$ reported in either paper. What the *Anesthesiology* paper does settle is the definition the derivation needed, doses to the alveoli as $`F_I \dot V_A \times 30`$ min "where $`\dot V_A = f_A \dot V_E`$", so $`f_A`$ is the alveolar fraction of *total* minute ventilation; the candidate table's second row is recorded as still unreadable from the text rather than becoming a sourced result. Five items, one of which is the v0.4.19 cut itself.
