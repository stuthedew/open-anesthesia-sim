---
id: PL-H47Y
title: docs/machine-survey.md section (a1) says Shin et al.'s three Draeger apparatus volumes cite sources nobody could open; the full text names them as Draeger's instructions-for-use manuals (refs 12-14), says the 1.2 L is a Hudson RCI circuit, and its sums leave the set-up's 3 L reservoir bag out - the table should say so, as PL-TBMX's rule in docs/MODEL.md now does
priority: P3
effort: S
status: ready
classes: docs
feature: machine-profile-framework
touches: docs/machine-survey.md
added: 2026-10-04
payoff: a machine-profile author sent to the survey learns that Shin et al.'s volumes are Draeger's own manual figures and that the with-circuit totals leave out a 3 L bag, which would otherwise nearly double a Perseus A500's circuit time constant
verify: grep -qF 'Hudson RCI' docs/machine-survey.md && grep -qF '3 L reservoir bag' docs/machine-survey.md && ! grep -qF 'onward citations this session could not reach' docs/machine-survey.md
---

**Problem.** docs/machine-survey.md section (a1) says Shin et al.'s three Draeger apparatus volumes cite sources nobody could open; the full text names them as Draeger's instructions-for-use manuals (refs 12-14), says the 1.2 L is a Hudson RCI circuit, and its sums leave the set-up's 3 L reservoir bag out - the table should say so, as PL-TBMX's rule in docs/MODEL.md now does

**Reproduced 2026-10-04** on `main` at `8f24fe78`:
`grep -cE 'Hudson RCI|3 L reservoir bag' docs/machine-survey.md docs/MODEL.md src/anesthesia_sim/core/parameters.py src/anesthesia_sim/data/machines/reference_circle_system.json`
prints 0 for the survey and 2, 2 and 1 for the three places that send a
profile author to it, and the survey still says Shin et al. "cite them onward
to sources this session could not open" (§ "How a value gets into this
document", its second point) and, in its Sources entry, "with onward
citations this session could not reach". The paper's JATS full text from
PubMed Central (PMC5248460, DOI 10.1186/s12871-016-0294-y, fetched through
NCBI efetch) bears out all three of the title's claims. The volume sentence
cites refs 12 to 14, which are Dräger Medical's instructions for use for the
Primus IE (2014), the Perseus A500 (2013) and the Zeus IE (2015); the set-up
joined each machine to a Hudson RCI breathing circuit (Teleflex) of 1.2 L
internal volume, a reservoir bag of 3 L and a test lung; and its sums are
"the internal volume of AM + the volume of breathing circuit 1.2 L", which
leaves the bag out. The manuals themselves stay unread: on the same day the
egress proxy refused `www.draeger.com` at CONNECT with a 403.

**Why it matters.** The survey's § "(a1) Apparatus gas volume" is where
`docs/MODEL.md`'s rule for `circuit_volume_l` (`PL-TBMX`), the docstring in
`core/parameters.py` and the reference machine profile's `provenance_gap` all
send a machine-profile author, and it is the one of the four that leaves the
three volumes' origin unnamed and says only "a 1.2 L patient circuit". An
author working from its table cannot tell that the figures are Dräger's own
manual values republished, or that the with-circuit totals leave out a 3 L
bag; counting the bag would put a Perseus A500 at 6.3 L and its circuit time
constant at 94.5 s at 4.0 L/min, against the 49.5 s the rule gives. No stored
value draws on the table today, so this is documentation, but it is the
documentation the next machine profile is built from.

**Done when.** `docs/machine-survey.md` says what `docs/MODEL.md` § "Governing
equations" → "Breathing circuit" now says, in each of the three places it
describes these figures. The second point of § "How a value gets into this
document" and the Shin et al. entry under § "Sources" name the onward sources
as Dräger's instructions for use, the paper's refs 12 to 14, still unread
because `www.draeger.com` is refused; and § "(a1) Apparatus gas volume" names
the circuit as the Hudson RCI and says that the with-circuit column, and the
time constants built on it, leave the set-up's 3 L reservoir bag out.

**A lead, not verified.** Read from the same full text by the triage pass,
2026-10-04: Table 1's caption cites refs 12, 13 and 15, and ref 15 is Meyer et
al. 2008, the Dräger-authored *Modern Anesthetics* chapter, which may be an
openable source for the same volumes where the manuals are not. Check it
before citing it.
