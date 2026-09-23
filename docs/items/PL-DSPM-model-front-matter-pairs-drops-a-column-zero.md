---
id: PL-DSPM
title: model._front_matter_pairs drops a column-zero root_cause_of: or Root-cause-of: line with no unknown-field report, so a hand-written generator head is lost at exit 0
priority: P3
effort: S
status: done
classes: defect
feature: generator-identification
milestone: v0.5.8
touches: subprojects/docket/src/docket/model.py, subprojects/docket/tests/test_model.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the first 2026-09-23 triage pass
added: 2026-09-22
closed: 2026-09-23
pr: 945
payoff: a generator claim typed with an underscore or a capital is refused by name instead of vanishing at exit 0, so a session that believes it recorded a generator is told when nothing ranks it
verify: grep -q 'def test_a_field_spelt_outside_the_key_grammar_is_reported_as_unknown' subprojects/docket/tests/test_model.py
impairs-generators: model._front_matter_pairs passes over a column-zero line whose key model.FIELD_RE cannot match, so root_cause_of: or Root-cause-of: (and the same spellings of impairs-generators:) never reach unknown_fields - a hand-written generator claim vanishes at docket check exit 0 and nothing ranks or reports it
recurrences: 2026-09-23 PL-JD4L withdrawn 2026-09-23 PL-JD4L
---

**Problem.** model._front_matter_pairs drops a column-zero root_cause_of: or Root-cause-of: line with no unknown-field report, so a hand-written generator head is lost at exit 0

**Reproduced 2026-09-23.** The test used a scratch store holding one open head
over three members. With the head's field written `root_cause_of:` or
`Root-cause-of:`, `bin/docket check --items <store> --no-git` exits 0 and says
nothing about the head, and `bin/docket generators` answers "no item carries a
sound `root-cause-of:`". Written `root-cause-of:`, the same head is seen and
asked for its `generator:` verdict. Written `root-cause-off:`, it is refused as
"unrecognized field(s) root-cause-off; a misspelled field is silently ignored,
so it is rejected here". The cause is that `model.FIELD_RE` admits only
`[a-z][a-z0-9-]*` keys, and `_front_matter_pairs` passes over a column-zero line
it cannot match, so that line never reaches `unknown_fields`. It has not fired
yet. No front matter in the store holds such a line, and git history finds the
string only in this item's title.

**Why it matters.** `unknown_fields` exists so that a misspelt field is refused
rather than ignored. It misses the two misspellings a hand-typed key is likeliest
to carry: an underscore and a capital. On `root-cause-of:` or
`impairs-generators:`, the result is a generator claim that the session believes
it recorded, lost at exit 0 with nothing reporting it. That is the failure the
generator-machinery rule exists to prevent. `bin/docket set --root-cause-of`
writes the right spelling, so only a hand edit reaches this.

**Why `impairs-generators:`** (triage, 2026-09-23). This breaks the
`root-cause-of:` field itself, the first function `subprojects/docket/README.md`
lists for the field. It also contradicts rules the code already states: the
README's "Where a field cannot be read, it is reported rather than guessed at",
and `_front_matter_pairs`' own "A line that is not a `key: value` line is not
passed over". It is a defect in what exists, so `PL-6Q9L`'s pause does not hold
it.

**Done when.** A column-zero `key: value` line whose key falls outside
`FIELD_RE`'s grammar, such as `root_cause_of:` or `Root-cause-of:`, reaches
`unknown_fields`, and `docket check` therefore refuses it.
`test_a_field_spelt_outside_the_key_grammar_is_reported_as_unknown` in
`subprojects/docket/tests/test_model.py` pins this. A column-zero line with no
`key:` shape is still passed over, as
`test_a_line_at_column_zero_continues_nothing_as_it_continues_nothing_in_yaml`
requires.

**Generator check.** An instance of closed head `PL-9HD1`'s mechanism, filed
2026-09-22, the day after that head closed. The mechanism is `FIELD_RE`'s
line-at-a-time read passing over a line it cannot match, with nothing reporting
it. `PL-9HD1`'s fix gave indented lines a meaning and left column-zero lines
passed over. `PL-KVDK` recorded the head as spent and holding, and this instance
qualifies that verdict. It is the first post-close instance, so it makes no
generator yet.
