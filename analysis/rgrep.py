import sys, pandas as pd
v = pd.concat([pd.read_csv('vietnam_reddit_v5.csv'), pd.read_csv('vietnam_reddit_v6.csv')])
v['text'] = v.text.astype(str)
pats = sys.argv[1:-1]; n = int(sys.argv[-1])
m = pd.Series(True, index=v.index)
for p in pats: m &= v.text.str.contains(p, case=False, regex=True)
s = v[m].sort_values('score', ascending=False).head(n)
print(m.sum(), 'hits')
for _, c in s.iterrows():
    t = c.text.replace('\n', ' ')
    import re
    i = re.search(pats[0], t, re.I); a = max(0, i.start() - 200) if i else 0
    print(f"[T{c.thread_no} {c.score}pts {str(c.date)[:7]}] {c.thread_title[:60]} :: ...{t[a:a+450]}")
