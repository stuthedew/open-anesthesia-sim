---
id: PL-4BGX
title: docs/MODEL.md's paragraph on the two classes of vaporizer is unclear and uses its own terms: it never says the maxima are dial maxima or how the classes differ, and states the altitude difference more firmly than a source the project can cite
priority: P2
effort: S
status: done
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md
added: 2026-11-07
closed: 2026-11-16
pr: 2171
payoff: a clinician reads which vaporizer design sets each agent's dial limit, and the altitude behaviour no more firmly than its sources state it
verify: ! grep -qF 'three maxima come from two classes of vaporizer' docs/MODEL.md
---

**Problem.** docs/MODEL.md's paragraph on the two classes of vaporizer is unclear and uses its own terms: it never says the maxima are dial maxima or how the classes differ, and states the altitude difference more firmly than a source the project can cite

**Where.** `docs/MODEL.md` § "Delivery-limit and MAC parameters", the paragraph that opens "**The three maxima come from two classes of vaporizer, which this model would need to tell apart only away from sea level.**" (line 4068 on `main` on 2026-11-07).

**What the owner said.** Shown the copy editor's edit of this paragraph in `PL-F0Q2`'s debug runs, the project owner asked "“The three maxima come from two classes of vaporizer.” what does that mean?", rejected it ("Yes. Reject"), and asked for the terms to match the reference chapter, Dorsch and Dorsch's chapter 6 (2026-11-07, 21:59Z to 22:04Z). The rejected edit was kept in the copy editor's test set, which `PL-GL45` removed on 2026-11-14; `git show d8ba53b8:docs/prose-review/rejected/unclear-2026-11-07-two-classes-of-vaporizer.md` prints it. The original has the same two gaps: "maxima" never says it means each agent's highest dial setting, and the paragraph names the two classes without saying how they work.

**A source the project can cite.** Dosch MP, Tharp D. *The Anesthesia Gas Machine*, "Processing: Vaporizers". University of Detroit Mercy, revised February 2026. https://healthprofessions.udmercy.edu/academics/na/agm/05. It classifies the Vapor 2000 and similar vaporizers as "variable bypass, flow over, temperature compensated, agent-specific, out of circuit", and describes the Tec 6 as "electrically heated, dual circuit injector, constant-temperature, agent specific, and out-of-circuit". It says "The Tec 6 desflurane vaporizer is not a variable bypass vaporizer, it is an injector (i.e. gas-vapor blender)". On altitude it says "The effect of altitude on vaporizer performance is controversial", that some sources say variable-bypass vaporizers need no adjustment "but the Tec 6 must be dialed up beyond the desired dose at higher altitudes", and "Other sources disagree". A session cited Dorsch JA, Dorsch SE, *Understanding Anesthesia Equipment*, 5th ed., chapter 6, but no session could open it on 2026-11-07. The Tec 6's design is also in Johnston RV, Andrews JJ, et al., Anesth Analg 1994;79:548-52, doi:10.1213/00000539-199409000-00025.

**Recommendation.** Rewrite the paragraph for a clinician. Say that each agent's limit is the highest setting of its vaporizer's dial. Name the two designs in the source's terms: sevoflurane's and isoflurane's limits come from variable-bypass vaporizers, and desflurane's from the Tec 6, an electrically heated, dual-circuit gas-vapor blender. Keep why the model need not tell them apart (ambient pressure fixed at 760 mmHg), and state the altitude difference only as firmly as the cited source does. Check Dorsch and Dorsch's chapter 6 for its terms first, where a copy can be reached. This is a content fix to the safety-critical specification, so it needs the owner's review.

**Order.** [superseded 2026-11-14: the copy editor was removed (`PL-GL45`), so no line edit of `docs/MODEL.md` is coming] Land this before the copy editor's line edit of `docs/MODEL.md`.
In `PL-F0Q2`'s rerun of this section on 2026-11-08 (`fix8-p043`), the fixed
copy editor kept the rejected opening, "The three maxima come from two classes
of vaporizer", word for word. Three other runs that day rewrote it. A copy
edit of the paragraph as it stands on `main` may keep that opening again.

**Checked 2026-11-09:** The restructure split the paragraph, and the opening
the owner rejected is still there. § "Delivery-limit and MAC parameters" says
the model need not know each maximum's class "because the three maxima come
from two classes of vaporizer that it would need to tell apart only away from
sea level" (lines 3708 to 3710). The paragraph before it now says that each
maximum is "the calibrated dial maximum" of named vaporizers, which settles the
first gap. The two classes and their response to altitude moved to § "Known
limitations" (from line 12250). There they are named "variable-bypass
vaporizers" and "gas–vapour blenders", with quotations from Datex-Ohmeda's
Tec 6 Plus sheet and from Andrews and Johnston. That section also says "The
direction of each class's response is not in doubt", where Dosch and Tharp
call the effect of altitude "controversial".

**Why it matters.** The owner could not tell what the sentence meant, and the
copy editor kept it word for word on a rerun. A clinician working at altitude
could act on how firmly the document states the real vaporizers' behaviour,
so that statement should be no firmer than its sources.

**Done when.** The sentence in § "Delivery-limit and MAC parameters" names the
two designs in the source's terms (variable-bypass vaporizers for sevoflurane
and isoflurane, and the Tec 6's heated gas–vapour blender for desflurane). It
also says why the model need not tell them apart: ambient pressure is fixed at
760 mmHg. § "Known limitations" states the altitude difference no more firmly
than its cited sources do, and cites Dosch and Tharp where they disagree.
Dorsch and Dorsch's chapter 6 is checked for its terms where a copy can be
reached. This is a content change to the safety-critical specification, so its
pull request waits on the owner's review.

**Generator check.** One-off: a paragraph the owner could not follow, found
when the copy editor was tested on this section (`PL-F0Q2`).

**Present at the Gate 3 freeze (checked 2026-11-09).** The passage this item
fixes was already in its file at `817a4d88`, the commit that froze Gate 3, so
under ROADMAP.md § "The gate is a snapshot, not a moving target" the item
joins v0.7.0's frozen list rather than being deferred by its capture date.

**Done 2026-11-16.** Following the item's recommendation, the sentence in
`docs/MODEL.md` § "Delivery-limit and MAC parameters" that the owner could not
follow is replaced by a paragraph that names the two designs in Dosch and
Tharp's terms. The sevoflurane and isoflurane vaporizers are variable-bypass
vaporizers, and the Tec 6 is a gas–vapour blender, which
Johnston et al. 1994's abstract calls "an electrically heated, pressurized,
electromechanically coupled dual-circuit blender". The paragraph says the
model need not tell them apart because it fixes ambient pressure at 760 mmHg.
That value was checked in `docs/MODEL.md` § "Assumptions" and in
`core/liquid_agent.py`, where the reference pressure is one standard
atmosphere, 101 325 Pa. In § "Known limitations", "respond to falling ambient
pressure in opposite directions" became "respond differently", and "the dial
needs no altitude correction" and "The direction of each class's response is
not in doubt, and neither is the contrast between the two" were removed. The
Tec 6's response is still stated as fact, because its manufacturer's
instruction and Andrews and Johnston's description of its mechanism support
it. Dosch and Tharp's statement that the effect of altitude is
"controversial" is quoted as applying to how large the variable-bypass
response is and whether its dial needs correcting, with their report that Dorsch and Dorsch say to consult each model's
operator's manual. The Datex-Ohmeda and Andrews and Johnston quotations are
kept unchanged. § "Assumptions" said the two classes "diverge in opposite
directions" and pointed at § "Known limitations"; it now says they respond
differently, so the two sections agree. Dosch and Tharp is added to the
list of sources as tier 2, and the owner-attested count reads "two of those
six".

What was read on 2026-11-16: Dosch and Tharp's chapter, in full, by `curl`
from its address. Johnston et al. 1994 (PMID 8067562), the abstract only,
through the PubMed MCP server; it says nothing about altitude. Dorsch and
Dorsch's chapter 6 could not be read: Open Library lists the book with no
e-book, the Internet Archive holds no copy, the Google Books API refused the
query for quota, and the private reference corpus does not hold it. Its terms
are therefore not checked, and its altitude advice is cited only as Dosch and
Tharp report it.

One difference found and not acted on: Dosch and Tharp give the Tec 6's
vapour pressure at 39 °C as "around 1550 mm Hg", where `docs/MODEL.md` takes
1460 mmHg from Weiskopf et al. 1994, which it records as read in full. The
primary source is kept. Docs sweep: `docs/MODEL.md` § "Assumptions",
§ "Delivery-limit and MAC parameters" and § "Known limitations";
`docs/INTERFACE.md`, `README.md`, `docs/machine-survey.md`,
`docs/machine-abstraction.md` and `docs/ARCHITECTURE.md` (no altitude
statement); `tests/` (no test quotes the changed text).

Blind review, 2026-11-16. The first pass found that the draft hedged both
classes as "said to respond differently", which put Dosch and Tharp's
unnamed "other sources" against the Tec 6's direction as well, although its
manufacturer and a primary description support it. The hedge now applies only
to the variable-bypass response. The pass also found that calling the Tec 6
"an injector" beside the sentence saying an injector into the circle is not
bound by the 18% maximum could reverse that sentence's meaning, so the new
paragraph calls it a gas–vapour blender only.

Owner's read, 2026-11-21. Asked how firmly `docs/MODEL.md` should state what real vaporizers do at altitude, with this change recommended over keeping both classes stated as certain, the project owner answered "Agree with recs" (project owner, 2026-11-21, ratified, over the firmer wording that said the sevoflurane and isoflurane dials need no altitude correction).
