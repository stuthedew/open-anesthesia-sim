---
paths:
  - "/src/**"
  - "/docs/MODEL.md"
  - "/docs/references/**"
---

# Where a value came from, and what a docstring owes a reader

The code-and-provenance half of the specialist standard. The fields it is
reviewed against and the design principles behind it are in
`.claude/rules/expert-review.md`, which is resident because it governs a reply.
Both rules below fire with a file already open, which is why they load on a
path instead (`PL-WWDT`).

## A reference implementation is not a source

`docs/MODEL.md` § "Source hierarchy: what may be cited as the authority for a
value" is the full statement — the three tiers, why republication does not
promote a value between them, and what a `sources` note owes a reader. Read it
before writing or reviewing a provenance note; this is only what a session
needs at the moment it names where a number came from.

Gas Man is this project's **reference implementation**: the working example
its starting values were taken from, and a behavior to compare against. It is
never the authority for a constant, and neither is a paper whose table simply
reprints its parameter set — De Wolf et al. 2012 and Meybohm et al. 2021 are
both Gas Man simulation studies, and neither measured a coefficient. Where a
stored value is one of theirs, say so, name what the primary literature
reports instead, and give the difference.

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
words around it, and `PL-XXBD` is the standing pass on comments that pad rather
than communicate. Lee's eighth rule — a generated documentation site — is
declined outright: there is no external API consumer to serve it to, and
`tests/reference/` already does what its verification half asks for, against
published data rather than against the code's own claims.
