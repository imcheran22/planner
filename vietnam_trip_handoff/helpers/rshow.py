import pandas as pd, sys
d=pd.read_csv('vietnam_reddit_v5.csv'); d['text']=d.text.fillna('').astype(str)
def show(ids, n=12, L=380, PL=700):
    for i in ids:
        g=d[d.thread_no==i]
        p=g[g.type=='post'].iloc[0]
        print(f"\n### T{i} r/{p.subreddit} {p.thread_date} [{p.score}] {p.thread_title}\nPOST: {p.text[:PL].replace(chr(10),' ')}")
        c=g[(g.type=='comment')&(g.text.str.len()>40)].sort_values('score',ascending=False).head(n)
        for _,x in c.iterrows(): print(f"  - [{x.score}] {x.text[:L].replace(chr(10),' ')}")
if __name__=='__main__':
    ids=[int(a) for a in sys.argv[1].split(',')]; n=int(sys.argv[2]) if len(sys.argv)>2 else 12
    show(ids,n)
