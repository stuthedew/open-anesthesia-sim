---
id: PL-8JV2
title: A schema version is checked as a whole number from 1 in three places (Migration, _check_version, oldest_readable) and carried as a bare int everywhere else - kept_file_name(True) writes workspaces.vTrue.json and set_aside_file_name(when, -1) writes a double hyphen - so build it once as a SchemaVersion type in serialization._read_version and carry the type through migrations, the store's Loaded and UnsupportedSchemaVersion (found reviewing PL-SSQW)
priority: P2
effort: M
status: done
classes: refactor, defect
feature: parse-dont-validate
touches: src/anesthesia_sim/layout/serialization.py, src/anesthesia_sim/layout/migrations.py, src/anesthesia_sim/layout/store.py, src/anesthesia_sim/layout/exceptions.py, docs/ARCHITECTURE.md, tests/unit/test_layout_serialization.py, tests/unit/test_layout_migrations.py, tests/unit/test_layout_store.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-17
closed: 2026-10-19
pr: 1674
payoff: a saved layout can no longer be written or set aside under a file name that states a version or attempt that does not exist, so a later read never refuses it for the wrong reason
verify: grep -q 'class SchemaVersion' src/anesthesia_sim/layout/migrations.py && grep -q 'def test_a_file_name_cannot_name_a_version_or_an_attempt_that_does_not_exist' tests/unit/test_layout_store.py
reenters: PL-ZGYX
---

**Problem.** A schema version is checked as a whole number from 1 in three places (Migration, _check_version, oldest_readable) and carried as a bare int everywhere else - kept_file_name(True) writes workspaces.vTrue.json and set_aside_file_name(when, -1) writes a double hyphen - so build it once as a SchemaVersion type in serialization._read_version and carry the type through migrations, the store's Loaded and UnsupportedSchemaVersion (found reviewing PL-SSQW)

**Reproduced 2026-10-17.** `kept_file_name(True)` returns
`workspaces.vTrue.json`, and `set_aside_file_name(when, -1)` returns
`workspaces.invalid-20261017T000000Z--1.json`.

**Why it matters.** A layout file name built from an unchecked version can name
a version that does not exist. A later read then sets aside or refuses a file
for the wrong reason, and the reader loses a saved layout. The three separate
checks also mean the rule can drift at one of them.

**Done when.** A `SchemaVersion` type is built once, where the version is read,
and the migrations, the store's `Loaded` and `UnsupportedSchemaVersion` take the
type rather than an `int`. `kept_file_name` and `set_aside_file_name` cannot be
called with a bare `bool` or a negative attempt, by type or by refusal.

**Generator check.** An instance of `PL-ZGYX`'s fact, "which values a quantity
may take, and whether a number in hand was already checked against them",
filed after that head closed on 2026-10-11.

**Checked 2026-10-19:** still reproduced on `main` at `6fd84bd5`.
`kept_file_name(True)` returned `workspaces.vTrue.json`, and
`set_aside_file_name(datetime(2026, 10, 17, tzinfo=UTC), -1)` returned
`workspaces.invalid-20261017T000000Z--1.json`.

**Fixed 2026-10-19.** `SchemaVersion` is defined in `layout/migrations.py`
rather than in `layout/serialization.py`, which this brief named. The
serialization module imports the migrations module, and `Migration` needs the
type, so defining it in the reader would make the two modules import each
other. `layout/migrations.py` already holds `LAYOUT_SCHEMA_VERSION` as "one
record" with the steps, so the type sits beside it. The reader's
`_read_version` is where a `SchemaVersion` is built from a file, and its
refusal of a version below 1 moved there from `_check_version`, with the same
message. `Migration.reads`, `oldest_readable`, `migrate`, `ReadWorkspaceSet`,
and `Loaded` take the type. `UnsupportedSchemaVersion` is handed
`SchemaVersion`s but is annotated with the `int` the type subclasses, since
`layout/migrations.py` imports the exceptions module, and a checker-only
import there broke `test_supported_range_edges.py`, which resolves every
annotation in the package at run time. `Migration` builds its
version through the type, so a bare `int` from an unchecked caller is checked. `kept_file_name` builds its argument through the type
too, so `True` and 0 are refused, and `set_aside_file_name` refuses a `bool`
or a negative attempt.

**Regression record.** The new tests import `SchemaVersion`, so they cannot be
collected against `6fd84bd5`. The variant that needs no new interface is the
reproduction above: against `6fd84bd5`, `kept_file_name(True)` and
`set_aside_file_name(MOMENT, -1)` return a name instead of raising, which
`test_a_file_name_cannot_name_a_version_or_an_attempt_that_does_not_exist`
asserts they do.
