---
paths:
  - "/src/**"
  - "/tests/**"
  - "/docs/MODEL.md"
  - "/docs/INTERFACE.md"
  - "/docs/VERIFICATION.md"
  - "/docs/PARAMETERS.md"
  - "/docs/references/**"
---

# Where a value came from, and what a docstring owes a reader

The code-and-provenance half of the specialist standard. The fields it is
reviewed against and the design principles behind it are in
`.claude/rules/expert-review.md`, which is resident because it governs a reply.
The rules below fire with a file already open, which is why they load on a
path instead (`PL-WWDT`).

## A reference implementation is not a source

A **reference implementation measured nothing**, and saying otherwise in a
reply is the same error as writing it into a file. It may still be *adopted* as
the authority for a constant, on a recorded decision, and this project has done
so for most of what it stores, so a reply ruling the practice out in general is
wrong about the shipped set.

`docs/PARAMETERS.md` § "Source hierarchy: what may be cited as the authority for a
value" is the full statement — the three tiers, why republication does not
promote a value between them, and what a `sources` note owes a reader. Read it
before writing or reviewing a provenance note; this is only what a session
needs at the moment it names where a number came from.

Gas Man is this project's **reference implementation**: the working example
its starting values were taken from, and a behavior to compare against. It
measured nothing, and neither did a paper whose table simply reprints its
parameter set — De Wolf et al. 2012 and Weber et al. 2021 are both Gas Man
simulation studies, and neither measured a coefficient. Where a stored value
is one of theirs, say so, name what the primary literature reports instead,
and give the difference.

**Which is not to say one may not be adopted, and here many are.** The
blood:gas coefficients are De Wolf et al.'s table, kept in preference to the
primary measurements cited beside them on the project owner's decision of
2026-09-03 (`PL-D6LX`). The tissue:gas coefficients print in the same table,
but their adopted authority has been Yasuda, Targ and Eger since 2026-09-13.
That changed once the stored values were found to be
Gas Man's figures for Yasuda, Targ and Eger's measurements, each within one
standard deviation of the paper's mean. The paper's own figures were not
substituted (`PL-FN5F`). All of the reference patient's parameters but its
venous pool are the Gas Man Workbook's, for want of a primary source any
session can reach.
Both declare it in the file — `"tier": "reference-implementation"`,
`"adopted": true` — so what a provenance note has to answer is not whether the
adoption was allowed but whether the entry says what it owes: the tier, why no
primary was adopted, and, where one was available, whose decision it was and
when. Those three obligations are stated in `docs/PARAMETERS.md` § "Source
hierarchy: what may be cited as the authority for a value", with the rest of
the rule.

This binds replies as well as files. "It comes from Gas Man" is a statement
about a program's parameter set, not about a measurement, and offering it as
the provenance of a constant is the same error made out loud.

## What a docstring and an error message owe a reader

Two of the ten rules Lee gives for documenting scientific software are not yet
practice here, and are adopted as written (Lee BD. Ten simple rules for
documenting scientific software. PLoS Comput Biol. 2018;14(12):e1006561.
doi:10.1371/journal.pcbi.1006561). The rest of that paper this repository
already meets or exceeds; `PL-MPZ0` carries the audit, rule by rule.

**A function that refuses says so.** Strict mypy settles a function's input and
output types, so what its docstring still owes a reader is the third thing Lee
asks for: which conditions it rejects, and which exception it raises.
`src/anesthesia_sim/core/exceptions.py` documents what each branch of the
hierarchy means to a caller; the docstring is where a caller learns which call
sites can produce one. `AlveolarCompartment.set_alveolar_ventilation` is the
shape — it names what it rejects and points at
`src/anesthesia_sim/core/supported_ranges.py` rather than restating the range.

**A refusal names what was refused.** An error message states the condition,
the value that failed it, and where to read why the limit sits where it does.
`src/anesthesia_sim/core/supported_ranges.py` is the worked example, and
`src/anesthesia_sim/core/validation.py` is what it is being contrasted with: a
message naming only the parameter leaves a rejected setting untraceable to the
input that produced it, which `CLAUDE.md`'s safety-critical standard treats as
part of the value rather than as presentation.

**Both are facts, not a license for commentary.** Each obligation above puts
something in the docstring or the message that a reader cannot get anywhere
else — which condition is refused, which value failed it. Neither is served by
words around it. `.claude/rules/plain-writing.md` says how to word each
sentence, and the `prose-quality` feature's items rewrite the existing text.
Lee's eighth rule — a generated documentation site — is
declined outright: there is no external API consumer to serve it to, and
`tests/reference/` already does what its verification half asks for, against
published data rather than against the code's own claims.

## Write these files plainly

`.claude/rules/plain-writing.md` decides how every text is worded. These are
the parts of it that apply only with one of these files open (`PL-GDN7`).

**Where the rest goes.** Decision history goes in the item. In `docs/MODEL.md`,
detail of the numerical method goes in a note for developers at the end of its
section, a paragraph that opens with "**For developers.**" (`PL-TZ7R`). The
numerical method itself is specified in `docs/VERIFICATION.md` (`PL-6PPZ`).
That note may name the tests for the paragraphs directly above it
(`PL-W8FL`). State a model
limitation only where it could change what a clinician concludes from a
displayed value (`PL-BS6N`). `docs/INTERFACE.md` ends a section with the same
note for developers, for the tests and code behind its requirements.

**Take the reason for a chosen value from a record.** Where a docstring, a
comment or a note for developers explains a chosen value, such as a tolerance
or a limit, take the reason from the code or test that uses the value, or from
a cited record. When the reason is not at hand, trace the value's history
first, with `git log -S` and the items. Search for the value as the code
writes it: a 0.5% tolerance was `5e-3` in the test that used it. When the
trace finds no reason, file an item for the missing record, and say in the
text what the trace found. Never state a reason that no record holds.

**A paragraph of `docs/MODEL.md`**, for a clinician. The project owner accepted
it on 2026-11-04 (`PL-ZDZ0`).

"The smallest change the MAC readout can show is therefore 0.02
percentage points of sevoflurane, 0.012 of isoflurane and 0.06 of desflurane,
never less than the percent readout's. The two readouts round separately, so
the MAC value can occasionally change while the percent stays the same."

**A docstring**, for a developer. Say what the function returns or does, with
its unit, then what it refuses, then anything a developer would get wrong
without being told. Leave out what the signature, the body or a named type
already shows.

"Return this group's blood flow $`Q_i = f_iQ`$ at a cardiac output, in
L/min. `docs/MODEL.md` § "Tissue groups" defines it. The group stores no flow
of its own, so no write can leave its flow out of step with the cardiac output
(`PL-HQF5`). Raises: TypeError: `cardiac_output_l_min` was not built as a
`CardiacOutput` (`core/supported_ranges.py`)."

Write each part in whole sentences:

"Reject a volume or tissue:gas partition coefficient that would make the
tissue's capacity less than the amount of agent it already holds."
