import pandas as pd, sys, re
c=pd.read_csv('youtube_comments.csv'); c['text']=c.text.fillna('').astype(str)
v=pd.read_csv('youtube_videos.csv')
def show(pattern, n=8, L=300, maxv=12):
    vv=v[v.title.str.contains(pattern,case=False,na=False)]
    for _,x in vv.head(maxv).iterrows():
        cc=c[(c.video_id==x.video_id)&(c.text.str.len()>35)].sort_values('likes',ascending=False).head(n)
        if len(cc)==0: continue
        print(f"\n## {x.title[:100]} | {x.upload_date} | views {x.views} | {x.channel}")
        for _,y in cc.iterrows(): print(f"  - [{y.likes}] {y.text[:L].replace(chr(10),' ')}")
if __name__=='__main__': show(sys.argv[1], int(sys.argv[2]) if len(sys.argv)>2 else 8)
