---
id: PL-8ZJQ
title: Davis and Mapleson 1981 gives a published, quantified blood-pool structure, which is the source PL-3YZW's 1.0 L venous pool has never had
status: untriaged
feature: model-spec-accuracy
added: 2026-09-06
---

**Problem.** `venous_blood_volume_l` is 1.0 in
`src/anesthesia_sim/data/patients/reference_adult.json` and has no counterpart
in the Gas Man Workbook table the file cites - the Workbook's `Blood` row reads
5.00 L, which is a blood volume rather than this model's venous mixing pool.
`PL-3YZW` carries that gap and has had no candidate source to close it with.

Lerou and Booij (Br J Anaesth 2001;86:12-28, read at full-text depth
2026-09-06) have one. Their Table 7 partitions total blood volume, taken as
0.07 x body mass, into arterial 0.2 and venous 0.8, and then splits the venous
share into four named pools "that serve to mimic circulation times in the
body" - adipose tissue 0.111, central 0.126, lean tissue 0.364 and viscera
0.399, each as a fraction of venous volume. The caption attributes the
structure to Mapleson and to **Davis NR, Mapleson WW. Structure and
quantification of a physiological model of the distribution of injected agents
and inhaled anaesthetics. Br J Anaesth 1981;53:399-405** - a journal article
with a purpose-built structure for exactly this question, and reachable where
the 1981 monograph in `PL-7HDS` is not.

**Why it matters.** The stored 1.0 L is the least defensible number in the
file: it is not the physiologic venous blood volume, it matches nothing in the
cited table, and its only role is to set a mixed-venous time constant of 12 s.
A published model that quantifies the same structure is the difference between
"a mixing volume chosen to give 12 s" and a value with a lineage.

**One arithmetic coincidence, recorded as a thing to check and not as a
finding.** At 70 kg their total blood volume is 4.9 L, of which the *arterial*
share is 0.2 x 4.9 = 0.98 L - within 2% of this file's 1.0 L *venous* pool.
Their arterial volume over their cardiac output is 0.98/5.345 = 11 s, against
this model's 1.0/5.0 = 12 s. The two compartments are not the same thing and
this model has no arterial volume at all, since it sets F_a = F_A; so this is
either coincidence or a sign that the stored pool is doing an arterial
compartment's job under a venous name. Which of those it is, is worth knowing
before any value is changed, and it is not established here.

**Where.** `src/anesthesia_sim/data/patients/reference_adult.json`
(`venous_blood_volume_l` and its `sources` entry); `docs/MODEL.md` - "Parameter
provenance" and the compartment definitions. Work it with `PL-3YZW`, which
states the gap this would close, and note `PL-024` (what the venous pool does
to early mixed-venous readings) reads on the same compartment.

**Done when.** Davis and Mapleson 1981 has been read at the source, and the
file either adopts a blood-pool volume with that provenance or records why the
1.0 L mixing volume is kept and what it is not - with the arterial/venous
question above answered rather than left open.
