---
id: PL-BD94
title: venous_blood_volume_l names a mixing volume but reads as the physiologic venous blood volume
status: untriaged
added: 2026-09-06
---

**Problem.** `venous_blood_volume_l` is 1.0 L. The physiologic venous blood
volume of a 70 kg adult is several times that - most of a roughly 5 L total
blood volume sits on the venous side. The stored 1.0 L is not a wrong
measurement of that quantity; it is a different quantity. `docs/MODEL.md`
§ "Venous blood" defines it as the volume of a single well-stirred pool whose
only role is `dF_v/dt = (sum_i Q_i F_i - Q F_v) / V_v`, so what it actually
sets is the mixed-venous time constant `V_v / Q`, here 12 seconds.

**Why it matters.** The name is the whole of the hazard. A reader who knows
physiology and meets `venous_blood_volume_l = 1.0` in a data file has two
readings available, and the wrong one - that this simulator thinks an adult
holds a litre of venous blood - is the one the name invites. `CLAUDE.md`'s
safety-critical standard puts naming inside the standard rather than beside it:
the correct number under a misleading label is a presentation failure. It is
also the parameter a future patient-editing feature would most plausibly expose
to a user, at which point the label reaches someone who can change it.

**Where.**

- `src/anesthesia_sim/data/patients/reference_adult.json` - the key itself.
- `src/anesthesia_sim/core/parameters.py` and `core/uptake_system.py` - the
  loader and the balance that reads it.
- `docs/MODEL.md` - § "Venous blood", the symbol table's `M_v` row, and the
  provenance table row "Venous blood-pool volume".

**What was already done.** `PL-6Q8N` wrote the distinction into the file's
first `sources` note and into `docs/MODEL.md` § "Parameter provenance", in
those words: a mixing volume, not the physiologic venous blood volume. So the
gap is documented; this item is about whether documenting it is enough.

**The decision.** Renaming the key is a data-file schema change on a protected
path, touching the loader, the provenance table, `doc_check`'s row mapping and
any saved state - real cost, for a file most readers will never open. The
alternatives are leaving the note as the whole answer, or renaming only the
displayed and documented label while the stored key stays. Note the provenance
table already calls it "Venous blood-pool volume", which is the better name and
is evidence the ambiguity was felt before.

**Done when.** Either the key is renamed to say what it is (candidates:
`venous_pool_volume_l`, `mixed_venous_mixing_volume_l`) with every reader
updated, or the decision to keep the name is recorded with its reasoning.
