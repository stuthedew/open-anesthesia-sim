python3 - <<'EOF'
import random
rows=[l.rstrip('\n').split('\t') for l in open('/tmp/claude-0/-home-user-open-anesthesia-sim/45eaf3d4-ced3-51a4-9eec-9faf4f65f319/scratchpad/candidates.tsv')]
rows=[r for r in rows if int(r[4])<=6000]
rng=random.Random(20261024); rng.shuffle(rows)
for i,r in enumerate(rows[24:44]): print(i+25,'#'+r[0],r[1]+':',' '.join(r[5].split(';')),sep=' ')
EOF
git show 692f0dc23 -- src/anesthesia_sim/core/supported_ranges.py | grep -nE '^\+.*(def require_supported_case_instant|isfinite\(instant_s\))' ; git show 9123d3868 -- src/anesthesia_sim/app/playback.py | grep -nE '^\+.*(round\(exact\)|never a modelling)'
