---
id: PL-QY94
title: contrast_check's check_authored_disabled_colours_are_measured misses a :disabled rule built with a plus between two string literals, and reads :disabled in a docstring as a rule; latent
priority: P3
effort: S
status: done
classes: defect
touches: tools/contrast_check.py, tests/unit/test_contrast_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1435
payoff: Every authored :disabled rule is held to a measured contrast requirement however its string is joined, and prose about the rule draws no false refusal
verify: grep -q 'def test_a_disabled_rule_joined_with_a_plus_is_read' tests/unit/test_contrast_check.py && grep -q 'def test_a_docstring_naming_disabled_is_not_a_rule' tests/unit/test_contrast_check.py
---

**Problem.** contrast_check's check_authored_disabled_colours_are_measured misses a :disabled rule built with a plus between two string literals, and reads :disabled in a docstring as a rule; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
the larger `tools/` checks. The check looks for the
substring `:disabled` in each string constant `ast` gives, so a selector built
as `"QPushButton:" + "disabled {...}"` is two constants and never matches
(adjacent literals and f-string pieces are joined by `ast` and are found), and
a docstring mentioning the pseudo-state counts as a rule. Qt 6 refuses a
pseudo-state split across lines or a comment, so only the `+` form can hide
one.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16. Latent: the one docstring that names `:disabled` is
`transport_button_stylesheet`'s, which is measured, so no verdict is wrong;
no stylesheet is built with `+`.

**Re-confirmed 2026-10-11** on main at `16a20a4f`: a scratch copy of
`src/anesthesia_sim/app/` with one module added, holding the rule
`"QPushButton:" + "disabled { color: #777; }"` in one uncited function and a
docstring naming `:disabled` in another, drew one refusal, for the docstring,
and none for the rule. The tree itself draws none, so it stays latent.

**Why it matters.** This check is what holds an authored disabled colour to a
measured contrast requirement, so a rule it misses is a disabled label whose
contrast nothing measures - the failure `PL-DHBX` found, where the transport
row's labels rendered absent on macOS Dark. The docstring half refuses a
function for prose about a rule, which costs a session a false error rather
than a wrong answer.

**Generator check.** Not a member of `PL-R417`: a string built from parts is
not a statement continued across lines. `PL-PXT7` holds colours built from
parts and `:!enabled`. The fact misread is what text in Python source makes
a Qt stylesheet; no head's `misread:` states it, and `PL-PXT7` (ready) is the
only other item reading it, so a one-off pair rather than a generator, worth
one pass over the check.

**Done when.** A `+` of string constants is read as one string, and a
docstring is not read as a stylesheet; a test pins both.
