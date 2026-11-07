---
id: PL-FDW6
title: MODEL.md's isoflurane and desflurane section says any weighted average of Yasuda's brain, heart, liver and kidney values lands away from sevoflurane's stored 1.1, but their equal-weight mean is 1.0975; it also says storing Yasuda's figures would move three displayed time constants, though seven of the nine stored values would change
status: untriaged
touches: docs/MODEL.md
added: 2026-11-07
---

**Problem.** MODEL.md's isoflurane and desflurane section says any weighted average of Yasuda's brain, heart, liver and kidney values lands away from sevoflurane's stored 1.1, but their equal-weight mean is 1.0975; it also says storing Yasuda's figures would move three displayed time constants, though seven of the nine stored values would change

**Where it was found.** The copy editor raised both as queries while `PL-F0Q2` tested it on this section as it stood before `#2049`, and `main` still has both sentences. In § "v0.2.0: isoflurane and desflurane", the vessel-rich bullet says "Any weighted average of the four would land away from the stored figure", yet sevoflurane's four values (1.15, 1.21, 1.25, 0.78) span the stored 1.1, and their equal-weight mean, 1.0975, rounds to it. The *Declined* paragraph says that storing Yasuda's figures "would move three displayed time constants", but the table shows seven of the nine stored values differing from Yasuda's means, such as isoflurane muscle at 4.5 against 4.40. The section should say which weighting it means and which time constants are displayed, or correct the claims. The copy editor also asked whether "Only the partition coefficients differ" means to exclude each agent's stored MAC, which the same section mentions.
