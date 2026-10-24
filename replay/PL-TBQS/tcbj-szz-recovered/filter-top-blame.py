import json,re
d=json.load(open('/tmp/claude-0/-home-user-open-anesthesia-sim/45eaf3d4-ced3-51a4-9eec-9faf4f65f319/scratchpad/szz.json'))
rows=[]
for iid,v in d.items():
    if not v['intro']: continue
    n,sha,s=v['intro'][0]
    total=sum(r[0] for r in v['intro'])
    date,subj=s.split('\t',1)
    if not re.search(r'\(#\d+\)$',subj): continue
    if iid in subj: continue
    if date> (v['added'] or ''): continue
    rows.append((v['added'],iid,v['classes'],n,total,sha,date,subj[:110]))
rows.sort()
print(len(rows))
for r in rows: print(*r,sep=' | ')
