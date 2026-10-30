// Vietnam trip research v5: your 21 threads + top Reddit threads found by search.
// Run in Chrome while logged in to Reddit:
//   1. Open https://www.reddit.com
//   2. F12 -> Console (type "allow pasting" + Enter if Chrome asks)
//   3. Paste everything and press Enter. Keep the tab open ~15-20 minutes.
//   4. vietnam_reddit_v5.csv downloads automatically when it prints "Done".

(async () => {
  // ---------- Settings ----------
  const MAX_THREADS = 270;        // total threads to download (yours + searched)
  const MIN_NEW = 220;          // keep topping up until at least this many extra threads are queued
  const PER_SEARCH = 8;           // best threads taken from each search
  const MIN_COMMENTS = 10;        // skip threads with fewer comments
  const MIN_DATE = "2023-01-01";  // skip older posts (prices, visas, transport have changed)
  const DELAY_MS = 2000;

  // Your original threads (add any new links you find to this list)
  const LINKS = [
    "https://www.reddit.com/r/Vietnam_Tourism/s/gwNljANVWc",
    "https://www.reddit.com/r/Vietnam_Tourism/s/bKfbQv7Y3Z",
    "https://www.reddit.com/r/travel/s/YSKAoj9bdV",
    "https://www.reddit.com/r/Vietnam_Tourism/s/fSwyn0b2ed",
    "https://www.reddit.com/r/travel/s/VS8HmnwJNh",
    "https://www.reddit.com/r/travel/s/hDypBAitO1",
    "https://www.reddit.com/r/Vietnam_Tourism/s/QLPnK7SyrH",
    "https://www.reddit.com/r/Vietnam_Tourism/s/JTLALcd1tC",
    "https://www.reddit.com/r/Vietnam_Tourism/s/K2PBO3hKLr",
    "https://www.reddit.com/r/VietnamTravelAdvice/s/J1s5ifbfDh",
    "https://www.reddit.com/r/Vietnam_Tourism/s/qdi9KCmMpI",
    "https://www.reddit.com/r/Vietnam_Tourism/s/ttxlukVzLZ",
    "https://www.reddit.com/r/Vietnam_Tourism/s/N76TxAhPp8",
    "https://www.reddit.com/r/FilipinoTravel/s/PuMQfbBmKs",
    "https://www.reddit.com/r/Vietnam_Tourism/s/eiqBxlz55W",
    "https://www.reddit.com/r/travel/s/3xQu4VUief",
    "https://www.reddit.com/r/VietNam/s/fu3wZJtwDQ",
    "https://www.reddit.com/r/PinoyTraveller/s/OPUqeRp0Tj",
    "https://www.reddit.com/r/Vietnam_Tourism/s/AhvfkB6tqU",
    "https://www.reddit.com/r/Vietnam_Tourism/s/xWwcFS1PmI",
    "https://www.reddit.com/r/VietNam/s/kHH5e75eeg",
  ];

  // Vietnam travel subreddits searched together; "ALL" = search all of Reddit
  const VN_SUBS = "VietNam+Vietnam_Tourism+VietnamTravelAdvice+travel+solotravel+honeymoon+backpacking";
  const INDIA_SUBS = "ForeignTravelIndia+SoloTravel_India";
  const SEARCHES = [
    // Route & timing
    ["Vietnam 7 days itinerary", VN_SUBS],
    ["one week Vietnam", VN_SUBS],
    ["Vietnam January weather", VN_SUBS],
    ["Vietnam in January", "ALL"],
    ["central Vietnam itinerary", VN_SUBS],
    ["north or central Vietnam", VN_SUBS],
    ["Vietnam before Tet", VN_SUBS],
    // Honeymoon & couples
    ["Vietnam honeymoon", "ALL"],
    ["Vietnam couple trip", VN_SUBS],
    // Places
    ["Hoi An", VN_SUBS],
    ["Da Nang", VN_SUBS],
    ["Hue Vietnam", VN_SUBS],
    ["Ba Na Hills", "ALL"],
    ["My Son sanctuary", "ALL"],
    ["Hanoi itinerary", VN_SUBS],
    ["Ha Long Bay cruise", VN_SUBS],
    ["Ninh Binh", VN_SUBS],
    ["Phu Quoc", VN_SUBS],
    ["Hai Van Pass", "ALL"],
    // Stays
    ["Da Nang beachfront resort", "ALL"],
    ["Hoi An beach resort", "ALL"],
    // Food, classes, nightlife, meeting people
    ["Hoi An cooking class", "ALL"],
    ["Vietnam food tour", VN_SUBS],
    ["Vietnam no pork no beef", "ALL"],
    ["Vietnam halal food", "ALL"],
    ["Hanoi nightlife", VN_SUBS],
    ["Da Nang nightlife", "ALL"],
    ["Vietnam meet people", VN_SUBS],
    // Practical
    ["Vietnam scams", VN_SUBS],
    ["Vietnam e-visa", VN_SUBS],
    ["Vietnam Indian tourist", "ALL"],
    ["Vietnam from India", "ALL"],
    ["Vietnam budget cost", VN_SUBS],
    ["Vietnam SIM card Grab", VN_SUBS],
    ["Vietnam travel tips first time", VN_SUBS],
    // Extra searches (v3)
    ["Vietnam 6 days", VN_SUBS],
    ["Vietnam 8 days", VN_SUBS],
    ["Vietnam 10 days itinerary", VN_SUBS],
    ["Hanoi Ha Long Ninh Binh", VN_SUBS],
    ["Da Nang Hoi An Hue itinerary", VN_SUBS],
    ["Vietnam February weather", VN_SUBS],
    ["Hoi An lantern boat", "ALL"],
    ["Hoi An tailor", VN_SUBS],
    ["An Bang beach", "ALL"],
    ["My Khe beach", "ALL"],
    ["Marble Mountains Da Nang", "ALL"],
    ["Son Tra peninsula", "ALL"],
    ["Hue imperial city tombs", "ALL"],
    ["Hai Van pass motorbike", "ALL"],
    ["Lan Ha Bay", "ALL"],
    ["Ha Long Bay overnight cruise worth it", "ALL"],
    ["Sapa trek", VN_SUBS],
    ["Ha Giang loop", VN_SUBS],
    ["Hanoi Old Quarter hotel", VN_SUBS],
    ["Hanoi train street", "ALL"],
    ["Hanoi street food", VN_SUBS],
    ["Hanoi cooking class", "ALL"],
    ["Ho Chi Minh City itinerary", VN_SUBS],
    ["Mekong Delta tour", VN_SUBS],
    ["Da Lat", VN_SUBS],
    ["Nha Trang", VN_SUBS],
    ["Phu Quoc resort", "ALL"],
    ["Vietnam seafood restaurant", VN_SUBS],
    ["Vietnam chicken dishes", "ALL"],
    ["Vietnam Indian food", "ALL"],
    ["Vietnam coffee shops", VN_SUBS],
    ["Vietnam rooftop bar", VN_SUBS],
    ["Vietnam pub crawl", "ALL"],
    ["Vietnam spa massage", VN_SUBS],
    ["Vietnam domestic flights Vietjet", VN_SUBS],
    ["Vietnam limousine bus", "ALL"],
    ["Vietnam train Hanoi Hue", VN_SUBS],
    ["Vietnam cash ATM card", VN_SUBS],
    ["Vietnam taxi scam airport", "ALL"],
    ["Vietnam Klook tours worth it", "ALL"],
    ["Vietnam mistakes to avoid", VN_SUBS],
    ["Vietnam regret", VN_SUBS],
    ["Vietnam trip report", VN_SUBS],
    ["Vietnam overrated", VN_SUBS],
    ["Vietnam hidden gems", VN_SUBS],
    ["Vietnam vs Thailand", "ALL"],

    // ---- v4: Indian traveller subreddits ----
    ["Vietnam", INDIA_SUBS],
    ["Vietnam budget", INDIA_SUBS],
    ["Vietnam itinerary", INDIA_SUBS],
    ["Vietnam honeymoon", INDIA_SUBS],
    ["Vietnam flights", INDIA_SUBS],
    ["Vietnam visa", INDIA_SUBS],
    ["Vietnam forex card", INDIA_SUBS],
    ["Vietnam food", INDIA_SUBS],
    ["Da Nang", INDIA_SUBS],
    ["Hanoi", INDIA_SUBS],
    ["Vietnam honeymoon", "chubbytravel"],

    // ---- v4: specific threads from your list (searched by title, best 3 matches each) ----
    ["Vietnam trip report Hanoi Ninh Binh Ha Long Bay Da Nang Hoi An", "travel", "title"],
    ["Vietnam suggestions travel itinerary", "travel", "title"],
    ["Vietnam itinerary advice 1 month", "travel", "title"],
    ["Vietnam travel report", "travel", "title"],
    ["Vietnam itinerary advice north central south", "travel", "title"],
    ["Trip report Vietnam 12 days", "solotravel", "title"],
    ["Vietnam itinerary advice", "travel", "title"],
    ["Planning a trip to Vietnam advice recs", "travel", "title"],
    ["First international trip Vietnam budget breakdown", "ForeignTravelIndia", "title"],
    ["Vietnam experience Hanoi Ho Chi Minh", "SoloTravel_India", "title"],
    ["Vietnam trip experience", "ForeignTravelIndia", "title"],
    ["Honeymoon trip in Vietnam", "VietNam", "title"],
    ["8 day vacation honeymoon Vietnam", "VietNam", "title"],
    ["20 night honeymoon itinerary Vietnam", "chubbytravel", "title"],
    ["laid back clean beach honeymoon", "VietNam", "title"],
    ["Travelling to Da Nang Ho Chi Minh Phu Quoc", "VietNam", "title"],
    ["Planning a trip to Da Nang Hoi An", "VietNam", "title"],
    ["Planning a trip to Vietnam in December", "VietNam", "title"],
    ["Vietnam December vs May", "VietNam", "title"],
    ["Vietnam weather December", "VietNam", "title"],
    ["travel tips advice first time travelers", "VietNam", "title"],
    ["tips you wish you knew earlier", "Vietnam_Tourism", "title"],
    ["e-visa arrival form", "VietNam", "title"],
    ["overcharged foreigner prices", "VietNam", "title"],
    ["HCMC taxi scam", "VietNam", "title"],
  ];

  // Top-up: most-discussed posts in the main Vietnam subs, used if searches find too few
  const TOPUP_SUBS = ["VietnamTravelAdvice", "Vietnam_Tourism", "VietNam"];

  const VN_WORDS = /vietnam|viet nam|hanoi|ha noi|hoi an|da nang|danang|\bhue\b|saigon|ho chi minh|ha long|halong|ninh binh|sapa|ha giang|phu quoc|nha trang|da ?lat|mekong|ba na|my son|hai van/i;

  // ---------- Helpers ----------
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const toDate = (s) => new Date(s * 1000).toISOString().slice(0, 10);
  const minEpoch = new Date(MIN_DATE).getTime() / 1000;

  async function getJSON(url) {
    for (let attempt = 0; attempt < 4; attempt++) {
      const r = await fetch(url, { credentials: "include" });
      if (r.status === 429) { console.log("  rate limited, waiting..."); await sleep(15000 * (attempt + 1)); continue; }
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    }
    throw new Error("rate limited too many times");
  }

  async function getHTML(url) {
    for (let attempt = 0; attempt < 4; attempt++) {
      const r = await fetch(url, { credentials: "include" });
      if (r.status === 429) { console.log("  rate limited, waiting..."); await sleep(15000 * (attempt + 1)); continue; }
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.text();
    }
    throw new Error("rate limited too many times");
  }

  // Pull thread links (in page order) out of a normal Reddit page
  function linksFromHTML(html) {
    const out = [];
    const ids = new Set();
    const re = /\/r\/([A-Za-z0-9_]+)\/comments\/([a-z0-9]+)\/([A-Za-z0-9_%\-]*)/g;
    let m;
    while ((m = re.exec(html))) {
      if (ids.has(m[2])) continue;
      ids.add(m[2]);
      out.push({ id: m[2], url: `https://www.reddit.com/r/${m[1]}/comments/${m[2]}/${m[3]}`.replace(/\/$/, "") });
    }
    return out;
  }

  const rows = [["thread_no", "found_via", "subreddit", "thread_title", "thread_date",
                 "thread_score", "num_comments", "type", "depth", "author", "score",
                 "date", "text", "thread_url"]];
  const seen = new Set();
  const failed = [];
  let threadNo = 0;
  let skipped = 0;

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

  // check = apply date / comment-count / Vietnam filters (for searched threads)
  async function downloadThread(url, via, check, minComments) {
    const j = await getJSON(url + ".json?limit=500&sort=top&raw_json=1");
    const p = j[0].data.children[0].data;
    if (seen.has(p.id) && via !== "your link") return { skip: "duplicate" };
    seen.add(p.id);
    if (check) {
      if (p.created_utc < minEpoch) return { skip: "older than " + MIN_DATE };
      if (p.num_comments < minComments) return { skip: "only " + p.num_comments + " comments" };
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

  // ---------- 1. Your 21 links ----------
  console.log("Step 1/3: your links");
  for (let i = 0; i < LINKS.length; i++) {
    try {
      const r = await fetch(LINKS[i], { credentials: "include" });
      const url = r.url.split("?")[0].replace(/\/$/, "");
      if (!url.includes("/comments/")) throw new Error("could not resolve link");
      const res = await downloadThread(url, "your link", false, 0);
      console.log(`[${threadNo}] OK  ${res.comments} comments  ${res.title.slice(0, 60)}`);
    } catch (e) {
      failed.push(LINKS[i]);
      console.log(`FAILED  ${LINKS[i]}  (${e.message})`);
    }
    await sleep(DELAY_MS);
  }

  // ---------- 2. Search for more threads ----------
  // Tries Reddit's search data feed first; if Reddit blocks it (403), reads the normal search page instead.
  console.log(`Step 2/3: running ${SEARCHES.length} searches`);
  const queue = [];
  const inQueue = (id) => seen.has(id) || queue.some((x) => x.id === id);
  let jsonBlocked = false;

  for (const [q, scope, mode] of SEARCHES) {
    const isTitle = mode === "title";
    const take = isTitle ? 3 : PER_SEARCH;
    const minC = isTitle ? 5 : MIN_COMMENTS;
    let added = 0;

    if (!jsonBlocked) {
      const url = scope === "ALL"
        ? `https://www.reddit.com/search.json?q=${encodeURIComponent(q)}&sort=relevance&t=all&limit=25&raw_json=1`
        : `https://www.reddit.com/r/${scope}/search.json?q=${encodeURIComponent(q)}&restrict_sr=1&sort=relevance&t=all&limit=25&raw_json=1`;
      try {
        const j = await getJSON(url);
        const picks = j.data.children
          .map((c) => c.data)
          .filter((d) => d.num_comments >= minC && d.created_utc >= minEpoch)
          .filter((d) => VN_WORDS.test(d.title + " " + (d.selftext || "") + " " + d.subreddit))
          .filter((d) => !inQueue(d.id))
          .sort((a, b) => (isTitle ? 0 : b.num_comments - a.num_comments))
          .slice(0, take);
        picks.forEach((d) => queue.push({ id: d.id, via: "search: " + q, check: false, minC,
                                           url: ("https://www.reddit.com" + d.permalink).replace(/\/$/, "") }));
        console.log(`  "${q}": +${picks.length} threads (queue ${queue.length})`);
        await sleep(DELAY_MS);
        continue;
      } catch (e) {
        if (e.message === "HTTP 403") {
          jsonBlocked = true;
          console.log("  Search data feed blocked by Reddit - switching to normal search pages.");
        } else {
          console.log(`  search FAILED "${q}" (${e.message})`);
          await sleep(DELAY_MS);
          continue;
        }
      }
    }

    // Normal search page. Multi-subreddit groups are searched across all of Reddit
    // with "Vietnam" added, which is more reliable than combined-subreddit search.
    let pageUrl;
    let query = q;
    if (scope === "ALL" || scope.includes("+")) {
      if (!VN_WORDS.test(query)) query += " Vietnam";
      pageUrl = `https://www.reddit.com/search/?q=${encodeURIComponent(query)}&type=posts&sort=relevance&t=all`;
    } else {
      pageUrl = `https://www.reddit.com/r/${scope}/search/?q=${encodeURIComponent(query)}&restrict_sr=1&type=posts&sort=relevance&t=all`;
    }
    try {
      const html = await getHTML(pageUrl);
      const picks = linksFromHTML(html).filter((d) => !inQueue(d.id)).slice(0, take + 4); // a few extra, some get filtered later
      picks.forEach((d) => queue.push({ id: d.id, via: "search: " + q, check: true, minC, url: d.url }));
      added = picks.length;
      console.log(`  "${q}": +${added} candidates (queue ${queue.length})`);
    } catch (e) {
      console.log(`  search FAILED "${q}" (${e.message})`);
    }
    await sleep(DELAY_MS);
  }

  // ---------- 2b. Top-up if searches found too few ----------
  for (const sub of TOPUP_SUBS) {
    if (queue.length >= MIN_NEW) break;
    for (const t of ["year", "all"]) {
      if (queue.length >= MIN_NEW) break;
      let picks = [];
      try {
        const j = await getJSON(`https://www.reddit.com/r/${sub}/top.json?t=${t}&limit=100&raw_json=1`);
        picks = j.data.children.map((c) => c.data)
          .filter((d) => d.num_comments >= MIN_COMMENTS && d.created_utc >= minEpoch && !inQueue(d.id))
          .sort((a, b) => b.num_comments - a.num_comments)
          .map((d) => ({ id: d.id, via: "top posts: r/" + sub, check: false, minC: MIN_COMMENTS,
                         url: ("https://www.reddit.com" + d.permalink).replace(/\/$/, "") }));
      } catch (e) {
        try {
          const html = await getHTML(`https://www.reddit.com/r/${sub}/top/?t=${t}`);
          picks = linksFromHTML(html).filter((d) => !inQueue(d.id))
            .map((d) => ({ id: d.id, via: "top posts: r/" + sub, check: true, minC: MIN_COMMENTS, url: d.url }));
        } catch (e2) {
          console.log(`  top-up FAILED r/${sub} (${e2.message})`);
        }
      }
      picks.forEach((p) => queue.push(p));
      console.log(`  top-up r/${sub} (${t}): +${picks.length} (queue ${queue.length})`);
      await sleep(DELAY_MS);
    }
  }

  // ---------- 3. Download searched threads ----------
  console.log(`Step 3/3: downloading up to ${MAX_THREADS - threadNo} more threads from ${queue.length} candidates`);
  for (const t of queue) {
    if (threadNo >= MAX_THREADS) break;
    try {
      const res = await downloadThread(t.url, t.via, t.check, t.minC);
      if (res.skip) { skipped++; console.log(`  skipped (${res.skip})`); }
      else console.log(`[${threadNo}] OK  ${res.comments} comments  ${res.title.slice(0, 60)}`);
    } catch (e) {
      failed.push(t.url);
      console.log(`FAILED  ${t.url}  (${e.message})`);
    }
    await sleep(DELAY_MS);
  }

  // ---------- Save CSV ----------
  const esc = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const csv = "﻿" + rows.map((r) => r.map(esc).join(",")).join("\r\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
  a.download = "vietnam_reddit_v5.csv";
  document.body.appendChild(a);
  a.click();
  a.remove();

  console.log(`Done: ${threadNo} threads (${skipped} skipped by filters), ${rows.length - 1} rows saved to vietnam_reddit_v5.csv. Failed: ${failed.length}`);
  if (failed.length) console.log("Failed links:\n" + failed.join("\n"));
})();
