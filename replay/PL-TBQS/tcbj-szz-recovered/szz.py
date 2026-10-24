"""SZZ-style pass: for each closed defect/safety item, find the main commits
that fixed it, blame the src/ lines those commits removed or changed at the
fix's parent, and report which earlier pull requests introduced them."""
import re, glob, subprocess, collections, json, sys

def git(*a):
    return subprocess.run(['git', *a], capture_output=True, text=True).stdout

items = {}
for f in glob.glob('docs/items/*.md'):
    t = open(f).read()
    m = re.match(r'---\n(.*?)\n---\n', t, re.S)
    if not m: continue
    d = dict(re.findall(r'^(\w[\w-]*):\s*(.*)$', m.group(1), re.M))
    cl = d.get('classes', '')
    if not re.search(r'\b(defect|safety)\b', cl): continue
    if 'anticipated' in cl: continue
    if d.get('status') != 'done': continue
    items[d['id']] = d

log = git('log', 'origin/main', '--format=%H%x09%ad%x09%s', '--date=short').splitlines()
commits = [l.split('\t', 2) for l in log]
out = {}
for iid, d in items.items():
    fixes = [c for c in commits if re.match(r'^[^:]*\b' + re.escape(iid) + r'\b', c[2])]
    intro = collections.Counter()
    for sha, date, subj in fixes:
        diff = git('diff', '-U0', sha + '^', sha, '--', 'src/anesthesia_sim/')
        cur = None
        for line in diff.splitlines():
            if line.startswith('--- a/'): cur = line[6:]
            elif line.startswith('--- /dev/null'): cur = None
            elif line.startswith('@@') and cur:
                m = re.match(r'@@ -(\d+)(?:,(\d+))? ', line)
                start, n = int(m.group(1)), int(m.group(2) or 1)
                if n == 0: continue
                bl = git('blame', '--porcelain', '-L', f'{start},{start+n-1}', sha + '^', '--', cur)
                for b in re.findall(r'^([0-9a-f]{40}) \d+ \d+', bl, re.M):
                    intro[b] += 1
    rows = []
    for b, n in intro.most_common(4):
        s = git('log', '-1', '--format=%ad\t%s', '--date=short', b).strip()
        rows.append((n, b[:9], s))
    out[iid] = dict(added=d.get('added'), classes=d.get('classes'), fixes=[f[2][:90] for f in fixes], intro=rows)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
