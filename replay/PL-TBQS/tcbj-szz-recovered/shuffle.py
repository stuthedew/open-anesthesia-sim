import random
rows=[l.rstrip('\n').split('\t') for l in open('/tmp/claude-0/-home-user-open-anesthesia-sim/45eaf3d4-ced3-51a4-9eec-9faf4f65f319/scratchpad/candidates.tsv')]
rows=[r for r in rows if int(r[4])<=6000]
rng=random.Random(20261024)
rng.shuffle(rows)
for i,r in enumerate(rows[:24]): print(i+1,*r,sep='\t')
