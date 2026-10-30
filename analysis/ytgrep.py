import sys, re, pandas as pd
y = pd.read_csv('youtube_transcripts_v2.csv'); y['transcript'] = y.transcript.fillna('').astype(str); y['title'] = y.title.fillna('').astype(str)
pat = sys.argv[1]; n = int(sys.argv[2]); w = int(sys.argv[3]) if len(sys.argv) > 3 else 300
k = 0
for _, r in y.iterrows():
    for m in re.finditer(pat, r.transcript, re.I):
        a = max(0, m.start() - w); print(f"[{r.video_language} | {r.title[:55]} | {r.upload_date}] ...{r.transcript[a:m.end()+w]}...\n".replace('\n', ' ') + '\n')
        k += 1
        if k >= n: sys.exit()
        break
