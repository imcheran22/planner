// Vietnam trip research v6 (console): fills the gaps left by v5.
//   Step 1  the 4 threads that FAILED in v5
//   Step 2  ~35 searches on the plan's open questions (Ba Na fog/coaster, Han River cruise, our hotels,
//           January sea, no-pork food, Indian food, e-visa, flights from South India, honeymoon in Da Nang...)
//   Step 3  downloads the best NEW threads only - all 270 v5 threads are built in and skipped.
//
// It is deliberately SLOW (6-9 s between requests) and STOPS by itself if Reddit starts refusing
// (403/429), then saves what it has. Fast scraping is what got the account flagged last time.
//
// How to run (Chrome on the laptop):
//   1. Open https://www.reddit.com in a tab
//   2. F12 -> Console  (type   allow pasting   and press Enter if Chrome asks - no quotes)
//   3. Paste everything and press Enter. Keep the tab open (~25-35 minutes).
//   4. vietnam_reddit_v6.csv downloads by itself at the end (or when it stops early).
//      To save early at any time, type   saveV6()   in the console and press Enter.

(async () => {
  // ---------- Settings ----------
  const MAX_NEW_THREADS = 50;     // new threads to download in step 3
  const PER_SEARCH = 4;           // best new candidates taken from each search
  const MIN_COMMENTS = 5;
  const MIN_DATE = "2023-06-01";
  const DELAY_MS = 6000;          // + random 0-3 s on top
  const STOP_AFTER_BLOCKS = 3;    // consecutive 403/429 responses before giving up and saving

  const FAILED_THREADS = [
    "https://www.reddit.com/r/VietNam/comments/1poricr/as_an_indian_tourist_visiting_vietnam_for_two",
    "https://www.reddit.com/r/Vietnam_Tourism/comments/1un74xs/is_ninh_binh_worth_more_than_a_day_trip_my",
    "https://www.reddit.com/r/backpacking/comments/95nhmb/completed_the_hai_van_pass_on_a_motorbike_vietnam",
    "https://www.reddit.com/r/travel/comments/7041xz/seen_while_motorbiking_through_the_hai_van_pass",
  ];

  const VN = "VietNam", VT = "Vietnam_Tourism", DN = "DaNang", ALL = "ALL";
  const SEARCHES = [  // [query, where]  where = a subreddit, or ALL (adds "Vietnam" if missing)
    ["Da Nang January weather", ALL], ["Hoi An January", ALL], ["Hue rain January", ALL],
    ["Da Nang beach swim waves", DN], ["Ba Na Hills fog", ALL], ["Ba Na Hills worth it", VN],
    ["Ba Na alpine coaster", ALL], ["Golden Bridge cloudy", ALL],
    ["Han River cruise", ALL], ["Dragon Bridge fire show", DN], ["Asia Park Sun Wheel", ALL],
    ["Naman Retreat", ALL], ["Pilgrimage Village Hue", ALL], ["La Siesta Hoi An", ALL],
    ["Da Nang ocean view hotel", ALL], ["An Thuong bars", DN], ["Da Nang nightlife couple", ALL],
    ["Hoi An cooking class", ALL], ["Hoi An lantern making", ALL], ["Hue food tour", ALL],
    ["My Son sunrise", ALL], ["Hai Van Pass private car", ALL], ["Hue Da Nang heritage train", ALL],
    ["Marble Mountains Lady Buddha", ALL], ["Da Nang honeymoon", ALL], ["Hoi An honeymoon", ALL],
    ["no pork", VN], ["Indian food Da Nang", ALL], ["halal Da Nang", ALL],
    ["Vietnam honeymoon", "india"], ["Vietnam trip", "SoloTravel_India"], ["Vietnam e-visa Indian", ALL],
    ["Vietnam trip cost from India", ALL], ["Chennai Da Nang flight", ALL], ["Vietnam non veg food Indian", ALL],
  ];

  const CENTRAL = /hoi.?an|da.?nang|danang|\bhue\b|ba.?na|golden.?bridge|hai.?van|marble|my.?son|son.?tra|an.?thuong|han.?river|dragon.?bridge|asia.?park|central|lang.?co|naman|pilgrimage|siesta/i;
  const PLAN = /january|jan|honeymoon|couple|wife|india|indian|pork|beef|halal|veg|cooking|lantern|coaster|fog|cruise|ocean|sea.?view|swim|wave|budget|cost|visa|flight|scam/gi;
  const VN_WORDS = /vietnam|viet nam|hoi ?an|da ?nang|danang|\bhue\b|hanoi|saigon|ho chi minh|ba ?na|hai ?van/i;

  const KNOWN = new Set(`
10biddl 11tho2h 11xbc4s 13agplc 13h3x8g 13pma5f 13wbr01 14mr1h4 15i60zg 15jaaqe 165wegz 166tort
16877gc 17pxd64 17rzwke 17wbwm9 17yhz1z 18gawes 18hplr5 18hxesa 193vmix 198qdz0 19bzozv 19dltlu
1ahylts 1atn11t 1bgrb4b 1bvpmj5 1cxqb36 1dst0ft 1f4v7ps 1fu4dp0 1gbtw6z 1gonwvj 1gqwy1p 1grpxpg
1h7johm 1hg7k14 1hjemha 1hpquuw 1hxbds2 1i1qypz 1i4b5mi 1id1tl5 1if1esx 1ilf8kn 1iqnldt 1isdr37
1j3qlnb 1j6e3w9 1jbx8p4 1jn3fzc 1jorkpy 1jp9cpu 1k12fe6 1k9xtme 1khnqma 1kl7izs 1kvhre4 1kytbcs
1kz16i6 1l1n75f 1l3c895 1lcxjq3 1le7jm4 1lf4n3o 1lgt26d 1ll5xdj 1loy6fx 1lwc7ly 1lzh5qx 1m6f7x5
1meq56r 1mmgpsd 1mo27a1 1mo5bu3 1mp16b7 1n7rhye 1nikzxm 1np8a73 1nyicwa 1o55ocb 1o76p3p 1o9xcig
1obgl0a 1oc77qk 1oct2w9 1ofpada 1og9i2e 1on7tz3 1or3ca9 1osjngq 1oxwd88 1p1ivbi 1p2ip0o 1p4byyw
1pblkfs 1pc6tuk 1pdxke0 1pjih8v 1plm9wz 1py5ph7 1q01g1s 1q30rnb 1q4an6d 1q8iemm 1q9hroj 1qbpz0v
1qfmq10 1qgzqrq 1qn62a0 1qnll0c 1qqzdht 1qscb1h 1qsuyus 1qtumnc 1qwqqup 1qzkutj 1r0nuhl 1r2hykj
1r5rr3c 1ra0uhj 1ra974f 1rc1vpr 1rdbpvi 1rgpoi0 1rgy6b7 1rjlexs 1rklyr9 1rld765 1rm3t5i 1rm3zfg
1roxda9 1rrdfh4 1rrnbs2 1rw1wk5 1s1lynd 1s5lrh5 1s5rj05 1s770rx 1s8kzj8 1sabk0k 1sam5p3 1sh9r85
1sj20pl 1sjxrfe 1snc7b2 1sqem1x 1srtnig 1sxwvv4 1t0mu25 1t2fn36 1t2fuip 1t62ffb 1t8hd3h 1tdapli
1tfrgca 1tfuz4s 1tfy2u0 1tkbg8a 1tlbik8 1tldn6y 1tnzvfr 1tukbdh 1tuvgor 1tvh0sd 1tzt333 1u4vxh9
1uayeel 1ud9aws 1ugzpas 1upqsq4 1upskea 1usfazk 1ushjii 1uuvee1 1uwiq69 1uyrkjj 1uzvf3k 1v1r99a
1v4y4u6 1v619ou 1v6x8sk 1v7mlfg 1v9qof2 1vaesl5 1vfynu5 1vh3pnk 1vivw68 1vklueu 1vm9452 1vn013m
1vph5o1 1vqg9jm 1vti9us 1vv7sol 1vw7q1c 1vww0cg 1vxzvlg 1vyth14 1vzso1b 1w2dyxq 1w2gzte 1w2h1kt
1w5uedt 1w5vjqf 1w6cceb 1wc1wgo 1wdskpx 1wfjtiy 1wgte7g 1wgwtbq 1wh76hk 1whkfwr 1wi36yu 1wjljgf
1wjlw4a 1wm7q0q 1wmaqjs 1wmdcci 1wn44qn 1wnavh9 1wo03ng 1wo0okv 1wrnw9i 1wrpkqx 1wrpm4z 1ws08s8
1wt5sb5 1wtqid4 1wu87d9 1wvz4wv 1wwclmx 1wx75ol 1wxdn4f 1wymhem 1wzkkmo 1x01ed4 1x1izgs 1x2u5ti
1x3mbuc 1x4jb3c 1x4lc5e 1x5l762 1x5l7tf 1x5m8p0 1x6flch 1x6knoq 1x7dsp4 1x7gjyc 1x7mejp 1x7yrl9
1x84kzs 1x86l1n 1x894j2 1xai2gk 1xanxkj 1xbr8pk 1xcmw3s 1xcsaiq 1xd5jnk 1xdobko 1xe352r 1xex6ii
1xeyyih 1xg2hmx 1xgl9xe 1xgrm85 1xhtbvu 1xix5xc
`.split(/\s+/).filter(Boolean));
  const FAILED_IDS = new Set(FAILED_THREADS.map((u) => u.match(/\/comments\/([a-z0-9]+)/)[1]));

  // ---------- Helpers ----------
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const pause = () => sleep(DELAY_MS + Math.random() * 3000);
  const toDate = (s) => new Date(s * 1000).toISOString().slice(0, 10);
  const minEpoch = new Date(MIN_DATE).getTime() / 1000;
  let blocks = 0;
  class Stop extends Error {}

  async function get(url, kind) {
    for (let attempt = 0; attempt < 3; attempt++) {
      const r = await fetch(url, { credentials: "include" });
      if (r.status === 429 || r.status === 403) {
        blocks++;
        console.log(`  Reddit said ${r.status} (${blocks}/${STOP_AFTER_BLOCKS})`);
        if (blocks >= STOP_AFTER_BLOCKS) throw new Stop("Reddit is refusing requests");
        await sleep(30000 * (attempt + 1));
        continue;
      }
      if (!r.ok) throw new Error("HTTP " + r.status);
      blocks = 0;
      return kind === "json" ? r.json() : r.text();
    }
    throw new Error("refused 3 times");
  }

  function linksFromHTML(html) {
    const out = [], ids = new Set();
    const re = /\/r\/([A-Za-z0-9_]+)\/comments\/([a-z0-9]+)\/([A-Za-z0-9_%\-]*)/g;
    let m;
    while ((m = re.exec(html))) {
      if (ids.has(m[2])) continue;
      ids.add(m[2]);
      out.push({ id: m[2], slug: m[3], url: `https://www.reddit.com/r/${m[1]}/comments/${m[2]}/${m[3]}`.replace(/\/$/, "") });
    }
    return out;
  }

  const rows = [["thread_no", "found_via", "subreddit", "thread_title", "thread_date",
                 "thread_score", "num_comments", "type", "depth", "author", "score",
                 "date", "text", "thread_url"]];
  let threadNo = 1000;   // starts at 1001 so it never clashes with v5 numbering
  let skipped = 0, saved = false;
  const failed = [];
  const done = new Set();

  function walk(children, base, depth) {
    for (const c of children) {
      if (c.kind !== "t1") continue;
      const x = c.data;
      const body = (x.body || "").trim();
      if (body && body !== "[deleted]" && body !== "[removed]") {
        rows.push([base.no, base.via, base.sub, base.title, base.tdate, base.tscore, base.ncom,
                   "comment", depth, x.author, x.score, toDate(x.created_utc), body, base.url]);
      }
      if (x.replies && x.replies.data) walk(x.replies.data.children, base, depth + 1);
    }
  }

  async function downloadThread(url, via, check) {
    const j = await get(url + ".json?limit=500&sort=top&raw_json=1", "json");
    const p = j[0].data.children[0].data;
    if (done.has(p.id)) return { skip: "duplicate" };
    done.add(p.id);
    if (check) {
      if (p.created_utc < minEpoch) return { skip: "older than " + MIN_DATE };
      if (p.num_comments < MIN_COMMENTS) return { skip: "only " + p.num_comments + " comments" };
      if (!VN_WORDS.test(p.title + " " + (p.selftext || "") + " " + p.subreddit)) return { skip: "not about Vietnam" };
    }
    threadNo++;
    const base = { no: threadNo, via, sub: p.subreddit, title: p.title, tdate: toDate(p.created_utc),
                   tscore: p.score, ncom: p.num_comments, url };
    rows.push([threadNo, via, p.subreddit, p.title, base.tdate, p.score, p.num_comments,
               "post", 0, p.author, p.score, base.tdate, (p.selftext || p.url || "").trim(), url]);
    const before = rows.length;
    walk(j[1].data.children, base, 1);
    return { title: p.title, comments: rows.length - before };
  }

  function save() {
    const esc = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const csv = "﻿" + rows.map((r) => r.map(esc).join(",")).join("\r\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    a.download = "vietnam_reddit_v6.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
    saved = true;
    console.log(`Saved vietnam_reddit_v6.csv: ${threadNo - 1000} threads, ${rows.length - 1} rows.`);
  }
  window.saveV6 = save;

  try {
    // ---------- 1. Failed threads ----------
    console.log("Step 1/3: the 4 threads that failed in v5");
    for (const u of FAILED_THREADS) {
      try {
        const res = await downloadThread(u, "v5 failed link", false);
        console.log(`[${threadNo}] OK  ${res.comments} comments  ${res.title.slice(0, 60)}`);
      } catch (e) {
        if (e instanceof Stop) throw e;
        failed.push(u);
        console.log(`FAILED  ${u}  (${e.message})`);
      }
      await pause();
    }

    // ---------- 2. Searches ----------
    console.log(`Step 2/3: ${SEARCHES.length} searches`);
    const queue = [];
    const taken = (id) => KNOWN.has(id) || FAILED_IDS.has(id) || queue.some((x) => x.id === id);
    for (const [q, where] of SEARCHES) {
      let query = q, pageUrl;
      if (where === ALL) {
        if (!VN_WORDS.test(query)) query += " Vietnam";
        pageUrl = `https://www.reddit.com/search/?q=${encodeURIComponent(query)}&type=posts&sort=relevance&t=all`;
      } else {
        pageUrl = `https://www.reddit.com/r/${where}/search/?q=${encodeURIComponent(query)}&restrict_sr=1&type=posts&sort=relevance&t=all`;
      }
      try {
        const html = await get(pageUrl, "html");
        const links = linksFromHTML(html).filter((d) => !taken(d.id));
        const score = (d) => (CENTRAL.test(d.slug) ? 3 : 0) + ((d.slug.replace(/_/g, " ").match(PLAN) || []).length);
        const picks = links.map((d, i) => ({ ...d, s: score(d) - i * 0.05 })).sort((a, b) => b.s - a.s).slice(0, PER_SEARCH);
        picks.forEach((d) => queue.push({ id: d.id, url: d.url, s: d.s, via: "v6 search: " + q }));
        console.log(`  "${q}": ${links.length} new links, +${picks.length} queued (queue ${queue.length})`);
      } catch (e) {
        if (e instanceof Stop) throw e;
        console.log(`  search FAILED "${q}" (${e.message})`);
      }
      await pause();
    }

    // ---------- 3. Download the best new threads ----------
    queue.sort((a, b) => b.s - a.s);
    console.log(`Step 3/3: downloading up to ${MAX_NEW_THREADS} new threads from ${queue.length} candidates`);
    for (const t of queue) {
      if (threadNo - 1000 >= MAX_NEW_THREADS + FAILED_THREADS.length) break;
      try {
        const res = await downloadThread(t.url, t.via, true);
        if (res.skip) { skipped++; console.log(`  skipped (${res.skip})`); }
        else console.log(`[${threadNo}] OK  ${res.comments} comments  ${res.title.slice(0, 60)}`);
      } catch (e) {
        if (e instanceof Stop) throw e;
        failed.push(t.url);
        console.log(`FAILED  ${t.url}  (${e.message})`);
      }
      await pause();
    }
  } catch (e) {
    if (e instanceof Stop) console.log("STOPPED EARLY: Reddit is refusing requests. Saving what was collected. "
      + "Don't retry today - use reddit_gapfill_apify.py instead.");
    else console.log("Unexpected error: " + e.message + " - saving what was collected.");
  }

  save();
  console.log(`Done: ${threadNo - 1000} threads (${skipped} skipped by filters). Failed: ${failed.length}`);
  if (failed.length) console.log("Failed links:\n" + failed.join("\n"));
})();
