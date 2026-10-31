"""Sri Lanka and Bali budgets, ₹ for two, 6 nights (22-28 Jan 2027).
Rates: $1 = ₹95.26 (29 Oct 2026, as Vietnam plan). IDR: 500,000 visa-on-arrival fee ≈ ₹2,950 (Pickyourtrail) → ₹1 ≈ 169.5 IDR.
LKR: 1,000 LKR ≈ $2.99 (Clock7, undated) → ₹1 ≈ 3.51 LKR. Kinds: listing / quote / cap."""
import json, os
USD = 95.26; IDR = 500000 / 2950; LKR = 1000 / (2.99 * USD)
u = lambda x: round(x * USD); i = lambda x: round(x / IDR); l = lambda x: round(x / LKR)
SL = [
 ('Flights Chennai ↔ Colombo (SriLankan)', '₹21,089 pp return, SriLankan listing for 22–26 Jan 2027 (cached)', 2 * 21089, 'listing', 'fly'),
 ('ETA (entry permit)', 'Free for Indians since 25 May 2026 (one site still says $25 on arrival)', 0, 'quote', 'visa'),
 ('SIM / eSIM', 'Cap', 1500, 'cap', 'visa'),
 ('Car with driver, 6 days', '$55/day (forum quote; listings $35–80/day)', u(55 * 6), 'quote', 'move'),
 ('Hotels Sigiriya, Kandy, Ella (1 night each)', 'Cap ₹6,000/night (not collected)', 18000, 'cap', 'stay'),
 ('Mirissa beach hotel, 2 nights', '~$105/night (Coastline Mirissa, a Dec date)', u(210), 'quote', 'stay'),
 ('Unawatuna beach hotel, 1 night', '~$100/night (Thaproban Pavilion, on the beach)', u(100), 'quote', 'stay'),
 ('Sigiriya Rock', '$20 × 2 (SAARC rate; others $35)', u(40), 'quote', 'do'),
 ('Temple of the Tooth, Kandy', 'Rs 1,500 × 2 (SAARC rate)', l(3000), 'quote', 'do'),
 ('Scenic train to Ella, first class', '~$24 × 2 (12Go, unverified; line partly closed after a 2025 cyclone)', u(48), 'quote', 'move'),
 ('Flying Ravana mega zipline, Ella', '$40 × 2 (reseller "from"; others $30–33)', u(80), 'quote', 'do'),
 ('Whale watching, Mirissa (Dec–Apr season)', '$50 × 2 (sources $25–50)', u(100), 'quote', 'do'),
 ('Sri Lankan cooking class', 'Cap ₹5,000 for two (not collected)', 5000, 'cap', 'do'),
 ('Other entries (Dambulla, Galle, Kandyan dance)', 'Cap', 4000, 'cap', 'do'),
 ('Everyday food', 'Cap ₹2,770/day × 6.5 (same as Vietnam)', 18000, 'cap', 'eat'),
 ('Nights out + farewell dinner', 'Cap (Mirissa cocktails ~$4, beer ~$2.50)', 7000, 'cap', 'eat'),
]
BA = [
 ('Flights Bengaluru ↔ Denpasar', '≈ ₹33,900 pp return (Skyscanner best-price snapshot AED 1,307; not for your dates). IndiGo nonstop one-way seen from $246.69 in Sep 2026', round(2 * 1307 / 3.6725 * USD), 'quote', 'fly'),
 ('Visa on arrival + Bali tourist levy', '(IDR 500,000 + 150,000) × 2', i(1300000), 'quote', 'visa'),
 ('SIM / eSIM', 'Cap', 1500, 'cap', 'visa'),
 ('Seminyak beach-view hotel, 2 nights', 'Cap ₹10,000/night (budget hotels $25–80; beachfront Legian Beach Hotel $295 in Mar)', 20000, 'cap', 'stay'),
 ('Ubud hotel or pool villa, 3 nights', 'Cap ₹6,000/night (not collected)', 18000, 'cap', 'stay'),
 ('Uluwatu cliff-view hotel, 1 night', 'Cap ₹9,000 (not collected)', 9000, 'cap', 'stay'),
 ('Driver days + airport transfers', 'Cap ₹4,000/day × 4 + ₹3,000 (not collected)', 19000, 'cap', 'move'),
 ('Waterbom Bali water park', '$38 × 2 (sources $24–38)', u(76), 'quote', 'do'),
 ('Ubud cooking class', '$46 × 2 (listings $34–46; IDR 400k–700k)', u(92), 'quote', 'do'),
 ('Uluwatu temple + Kecak fire dance', '(IDR 150,000 + 60,000) × 2', i(420000), 'quote', 'do'),
 ('Beach club minimum spend', 'IDR 1,000,000 (daybeds IDR 500k–2.5M)', i(1000000), 'quote', 'do'),
 ('Other entries (rice terraces, Monkey Forest, temples)', 'Cap', 3000, 'cap', 'do'),
 ('Everyday food', 'Cap ₹2,770/day × 6.5', 18000, 'cap', 'eat'),
 ('Farewell seafood dinner', 'Cap', 5000, 'cap', 'eat'),
]
out = {}
for name, rows in [('sl', SL), ('bali', BA)]:
    tot = sum(r[2] for r in rows); cats = {}
    for r in rows: cats[r[4]] = cats.get(r[4], 0) + r[2]
    out[name] = dict(total=tot, buffer=200000 - tot, cats=cats, lines=[dict(item=r[0], basis=r[1], inr=r[2], kind=r[3]) for r in rows])
    print(name, tot, 200000 - tot, cats)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'budget_sl_bali.json'), 'w'), ensure_ascii=False)
