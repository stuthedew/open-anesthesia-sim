---
id: PL-D126
title: Gas Man's published in-patient validation is materially worse during wash-in than during maintenance, and docs/MODEL.md's validation section does not say so
priority: P1
effort: S
status: done
classes: science, docs
feature: model-boundary-statements
milestone: v0.4.35
touches: docs/MODEL.md, tests/reference/test_published_wash_in_and_elimination.py
added: 2026-09-19
closed: 2026-09-20
pr: 771
payoff: tells a reader what a wash-in comparison against Gas Man is worth, in the phase this simulator most displays and its reference is least accurate
verify: grep -qF '10.1007/s10877-022-00842-0' docs/MODEL.md
---

**Problem.** Gas Man's published in-patient validation is materially worse during wash-in than during maintenance, and docs/MODEL.md's validation section does not say so
 — found while writing `docs/machine-survey.md` for `PL-4DCG`.

This project treats Gas Man as its reference implementation and compares against
it throughout `docs/MODEL.md`. A prospective in-patient validation of Gas Man
now exists and reports its accuracy split by phase, which changes what a
comparison against it is worth during the phase this simulator most emphasises.

**The measurement.** Candries E, De Wolf AM, Hendrickx JFA, "Prospective
validation of Gas Man simulations of sevoflurane in O2/air over a wide fresh gas
flow range", *J Clin Monit Comput* 2022;36(6):1881–1890, PMID 35318567,
[DOI 10.1007/s10877-022-00842-0](https://doi.org/10.1007/s10877-022-00842-0);
read at the abstract through the PubMed MCP server on 2026-09-19. Twenty-eight
patients, flows randomised from 0.2 to 6 L/min, on FLOW-i and Zeus workstations.
Over the hour, median performance error and median absolute performance error
were within 10%. Split by phase, the first 15 minutes gave MDPE 18% and MDAPE
21% on the FLOW-i and 7% and 13% on the Zeus, against 0% and 6%, and −1% and 5%,
over the last 45 minutes. The authors state the model performs better for
maintenance than for wash-in.

**Why it matters here.** The wash-in is where this simulator's teaching case
lives, and it is also where the machine's own contribution is largest — which is
the same finding `docs/machine-survey.md` reaches from the other direction. So
the phase in which this project's reference implementation is least accurate is
the phase this project most displays, and `docs/MODEL.md` does not say so
anywhere. It is a statement about the limits of a comparison rather than a defect
in this implementation, which is precisely what § "Known limitations" is for.

**Where.** `docs/MODEL.md` § "Known limitations", and wherever the document sets
out what agreement with Gas Man does and does not establish.

**Done when.** `docs/MODEL.md` records that Gas Man's own published in-patient
agreement is materially worse during wash-in than during maintenance, with the
figures and the citation, so a reader knows what a wash-in comparison against it
is worth.
