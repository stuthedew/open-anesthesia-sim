---
id: PL-9RJM
title: The Projects run's web container had no libegl1 and uv 0.8.17 on 2026-09-25, so make check stopped at uv's required-version floor and then at the first PySide6 import until apt-get install -y libegl1 and python3 -m pip install --user --upgrade uv were run by hand
status: untriaged
added: 2026-09-26
---

**Problem.** The Projects run's web container had no libegl1 and uv 0.8.17 on 2026-09-25, so make check stopped at uv's required-version floor and then at the first PySide6 import until apt-get install -y libegl1 and python3 -m pip install --user --upgrade uv were run by hand

**Found 2026-09-25** by slam-dunk batch 2's first `make check`. `PL-VHLZ`
(done) put `libegl1` in the environment setup script and `PL-SPZT` (ready)
covers the uv half, so this is evidence that the setup script does not reach
the environment the Projects run uses, rather than a new mechanism: the
`apt-get` and `pip` lines `README.md` names both worked from inside the session.
