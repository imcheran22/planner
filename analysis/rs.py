import sys, pandas as pd
v = pd.concat([pd.read_csv('vietnam_reddit_v5.csv'), pd.read_csv('vietnam_reddit_v6.csv')])
ids = [int(x) for x in sys.argv[1].split(',')]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
L = int(sys.argv[3]) if len(sys.argv) > 3 else 400
for i in ids:
    t = v[v.thread_no == i]
    p = t[t.type == 'post']
    if len(p): print(f"\n##### T{i} [{p.subreddit.iloc[0]}] {p.thread_title.iloc[0]} ({p.thread_date.iloc[0]}, {p.thread_score.iloc[0]} pts)\n  POST: {str(p.text.iloc[0])[:L]}")
    for _, c in t[t.type == 'comment'].sort_values('score', ascending=False).head(n).iterrows():
        print(f"  [{c.score}] {str(c.text)[:L]}".replace('\n', ' '))
