---
id: PL-QY94
title: contrast_check's check_authored_disabled_colours_are_measured misses a :disabled rule built with a plus between two string literals, and reads :disabled in a docstring as a rule; latent
status: untriaged
added: 2026-10-10
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

**Generator check.** Not a member of `PL-R417`: a string built from parts is
not a statement continued across lines. `PL-PXT7` holds colours built from
parts and `:!enabled`.

**Done when.** A `+` of string constants is read as one string, and a
docstring is not read as a stylesheet; a test pins both.
