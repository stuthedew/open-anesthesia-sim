---
id: PL-BD94
title: venous_blood_volume_l names a mixing volume but reads as the physiologic venous blood volume
priority: P2
effort: M
status: done
classes: refactor, docs
feature: model-spec-accuracy
milestone: v0.4.7
touches: src/anesthesia_sim/data/patients/reference_adult.json, src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/uptake_system.py, docs/MODEL.md
added: 2026-09-06
closed: 2026-09-07
pr: 423
verify: uv run pytest tests/unit/test_parameters.py && python3 -c "import json,pathlib; d=json.loads(pathlib.Path('src/anesthesia_sim/data/patients/reference_adult.json').read_text()); raise SystemExit(0 if 'venous_blood_volume_l' not in d and d['venous_pool_volume_l'] == 1.222 else 1)"
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

**Decision needed.** Is `venous_blood_volume_l` renamed to say what it is -
`venous_pool_volume_l`, `mixed_venous_mixing_volume_l` - with every reader
updated, or does the key stay and the note in the file plus the provenance
table's "Venous blood-pool volume" carry the distinction as the whole answer? A
rename is a schema change on a protected path, reaching the loader, the
balance, the provenance table, `doc_check`'s row mapping and any saved state.

**Classed `refactor, docs` rather than `science`, and it can be overruled.**
`PL-6Q8N` already wrote the distinction into the file's own `sources` note and
into `docs/MODEL.md`, so the reader who meets the misleading key meets the
correction in the same file, and nothing is displayed under this name. If the
key itself counts as a label under `CLAUDE.md`'s "the correct number with the
wrong label is still a safety failure", the class becomes `science` and the
band with it.

**Decided 2026-09-07: renamed, in the same edit as the revalue.** The key is
`venous_pool_volume_l`, which is the name `docs/MODEL.md`'s provenance table had
already been using for it - noted in this brief as evidence the ambiguity had
been felt before, and taken as the answer. `mixed_venous_mixing_volume_l` was
the alternative and was not taken: it is more explicit and less readable, and
the provenance table's existing wording is what a reader of the specification
will already have met.

**One edit rather than two, which is why this closes with `PL-8ZJQ`.** That item
moved the value to Davis and Mapleson's 1.222 L on the project owner's decision,
and a rename and a revalue on one key touching a protected path, the loader, the
balance, the provenance table and the test fixtures is one review rather than
two.

**What the rename reached**, each changed in the same commit:
`src/anesthesia_sim/data/patients/reference_adult.json` (the key and three
`sources` notes that named it), `src/anesthesia_sim/core/parameters.py` (the
dataclass field, the validated model and the loader), `src/anesthesia_sim/core/patient.py`,
`tests/unit/test_parameters.py`, `tests/reference/test_coupled_dynamics.py`, and
`docs/MODEL.md`'s provenance-table row. `ROADMAP.md`'s v0.4.6 baseline still
names the old key and was deliberately left alone: it records what that release
established, and editing it would falsify the release history rather than fix a
stale statement.

**The `verify:` command was run before the work and watched fail.** Against
`HEAD` it exits 1; against the finished tree it exits 0. It checks the stored key
and value directly rather than grepping prose, because the old name survives
correctly in a historical sentence in the Meybohm `sources` note.
