---
id: PL-8GJ6
title: The agent files record what Anesthesiology 69:A615 contains as unknown, and the authors' own reference list now confirms it is the 1988 abstract of the 1989 human-tissues paper
priority: P3
effort: S
status: done
classes: docs
feature: model-spec-accuracy
touches: src/anesthesia_sim/data/agents/sevoflurane.json, src/anesthesia_sim/data/agents/isoflurane.json, src/anesthesia_sim/data/agents/desflurane.json, docs/MODEL.md
added: 2026-09-13
closed: 2026-09-13
pr: 539
verify: grep -q 'A615' src/anesthesia_sim/data/agents/sevoflurane.json
---

**Problem.** `PL-ZP7Z` established that the Gas Man Workbook's reference 45 is
`Anesthesiology 69:A615`, an ASA annual-meeting abstract, rather than the 1989
*Anesthesia & Analgesia* paper the three agent files cite. It could not
establish what that abstract *is*, and each file records the honest form: "What
that abstract reports, and whether it differs from the paper, is unknown here
and is left recorded as unknown rather than assumed identical."

Half of that is now answerable from a primary document. Targ AG, Yasuda N, Eger
EI II, Anesth Analg 1989 Aug;69(2):218-25 (PMID 2764290) - the companion paper,
supplied by the project owner 2026-09-13 and read at full text the same day -
carries as its **reference 10**: "Yasuda N, Targ AG, Eger EI II. Solubility of
I-653, sevoflurane, isoflurane, and halothane in human tissues (abstr).
Anesthesiology 1988;69:A615."

So the authors themselves cite A615 as the abstract of the human-tissues work,
which is what `PL-ZP7Z` inferred from the volume year and the venue. The
inference is now a citation, from the same three authors, in the same volume.

**What it still does not settle**, and the note must keep saying so: what the
abstract *reports*. An abstract preceding a full paper by one issue may carry
different numbers, fewer tissues, or a preliminary analysis, and nothing here
has read it. The Workbook's attribution therefore remains unconfirmed for the
same reason as before, and `PL-B9K7` is still the item that would close it.

**Where.** The Yasuda `sources` entry in each of
`src/anesthesia_sim/data/agents/{sevoflurane,isoflurane,desflurane}.json` - the
sentence beginning "What that abstract reports". `docs/MODEL.md` § "Parameter
provenance", the bullet naming A615.

**Done when.** All three files, and `docs/MODEL.md`, record that the identity of
A615 is confirmed by the companion paper's own reference list, and keep the
distinction between knowing which document it is and knowing what it says.

**Closed 2026-09-13 alongside `PL-B9K7`, and its second half dissolved rather
than being answered.** All three agent files record that the companion circuit
paper's reference 10 cites A615 as the abstract of the human-tissues work, which
confirms its identity from a primary document, and they keep saying its contents
are unread.

What changed is that the contents stopped mattering. A615 was interesting only
as the nearest reachable form of the tissue measurements; the full paper is now
held and the stored coefficients have been checked against it directly
(`PL-B9K7`). Reading the abstract would settle nothing the full text has not
already settled, so this closes without anyone needing to find it.
