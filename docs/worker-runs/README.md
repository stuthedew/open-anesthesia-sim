# Headless worker runs

Each `.json` file here records one run of `tools/headless_worker.py`, the
runner that works a queue item on the monthly API credit, and how the run's
review went. The runner commits a run's record to the worker's branch. The
reviewing session adds the review's outcome with
`python3 tools/worker_runs.py review`, and `make check` fails until it does
(`PL-87BR`). `tools/worker_runs.py` defines the format.

The first headless run, on `PL-3R6L`, came before these records. Its facts are
in the message of commit `73013ffc`.
