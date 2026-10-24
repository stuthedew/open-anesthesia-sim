import json,re,subprocess,collections
def git(*a): return subprocess.run(['git',*a],capture_output=True,text=True).stdout
d=json.load(open('/tmp/claude-0/-home-user-open-anesthesia-sim/45eaf3d4-ced3-51a4-9eec-9faf4f65f319/scratchpad/szz.json'))
byPR=collections.defaultdict(list)
for iid,v in d.items():
    cl=v['classes']
    if re.search(r'\b(test|infra)\b',cl): continue
    for n,sha,s in v['intro']:
        date,subj=s.split('\t',1)
        m=re.search(r'\(#(\d+)\)$',subj)
        if not m or iid in subj: continue
        if n<2 and v['intro'][0][1]!=sha: continue
        full=git('rev-parse',sha+'^{commit}').strip()
        mt=int(git('log','-1','--format=%ct',full))
        f=git('ls-files','docs/items/'+iid+'-*').strip() or git('log','--all','--format=','--name-only','--diff-filter=A','--','docs/items/'+iid+'-*').split()[0]
        ft=git('log','origin/main','--diff-filter=A','--format=%ct','--',f).split()
        if not ft or int(ft[-1])<=mt: continue
        byPR[(m.group(1),full[:9],subj[:100])].append((iid,n,cl))
for (pr,sha,subj),ds in sorted(byPR.items(),key=lambda x:int(x[0][0])):
    st=git('show','--shortstat','--format=',sha,'--','src/anesthesia_sim').strip()
    ins=re.findall(r'(\d+) insertion',st); de=re.findall(r'(\d+) deletion',st)
    tot=git('show','--shortstat','--format=',sha).strip()
    ti=sum(map(int,re.findall(r'(\d+) (?:insertion|deletion)',tot)))
    print(pr,sha,(ins or ['0'])[0],(de or ['0'])[0],ti,';'.join(f'{i}({n})' for i,n,c in ds),subj,sep='\t')
