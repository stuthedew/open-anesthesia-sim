---
id: PL-HPQT
title: docs/MODEL.md v0.2.0 says five of the nine stored tissue:gas coefficients differ from Yasuda, Targ and Eger's means, while Source hierarchy and Known limitations say seven; the table shows seven differ, five of them by more than rounding to the stored precision
status: untriaged
added: 2026-11-07
---

**Problem.** docs/MODEL.md § "v0.2.0: isoflurane and desflurane" says that five of the nine stored tissue:gas coefficients differ from Yasuda, Targ and Eger's means, while § "Source hierarchy" and § "Known limitations" say seven. The v0.2.0 table shows that seven differ, five of them by more than rounding to the stored precision.

**Found 2026-11-07 while restructuring `docs/MODEL.md` (`PL-BSMF`, finding 47).**
§ "v0.2.0: isoflurane and desflurane" says "Five of the nine differ from the
study's means by up to 9%". § "Source hierarchy" says "In all seven cells
where Gas Man's ..." and § "Known limitations" says the stored values "differ
from Yasuda, Targ and Eger's means in seven of the nine cells". The two cells
that differ only by rounding to the stored precision are 2.38 against 2.4 and
2.09 against 2.1. Say which count is meant in each place, or use one count with
its definition.
