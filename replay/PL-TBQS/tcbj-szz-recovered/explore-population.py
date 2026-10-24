import re,glob
rows=[]
for f in glob.glob('docs/items/*.md'):
    t=open(f).read()
    m=re.match(r'---\n(.*?)\n---\n(.*)',t,re.S)
    if not m: continue
    fm,body=m.groups()
    d=dict(re.findall(r'^(\w[\w-]*):\s*(.*)$',fm,re.M))
    cl=d.get('classes','')
    if not re.search(r'\b(defect|safety|science)\b',cl): continue
    tch=d.get('touches','')
    if 'src/anesthesia_sim' not in tch: continue
    intro = re.findall(r'(?:introduced|regress|since|landed|added) (?:in|by) [^.\n]{0,80}',body,re.I)
    prs=re.findall(r'#(\d{3,4})',body)
    rows.append((d.get('id'),d.get('status'),d.get('added'),cl,len(prs),intro[:2]))
rows.sort(key=lambda r:r[2] or '')
print(len(rows))
for r in rows:
    if r[5] or r[4]: print(r)
