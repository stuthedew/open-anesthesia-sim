---
id: PL-GKG4
title: Blood flow is a bare float checked by hand at three places in core (blood.py, tissue.py, governing_equations.py) and is not a checked type as cardiac output is, so the next function that takes one can skip the check
status: untriaged
added: 2026-11-10
---

**Problem.** Blood flow is a bare float checked by hand at three places in core (blood.py, tissue.py, governing_equations.py) and is not a checked type as cardiac output is, so the next function that takes one can skip the check
