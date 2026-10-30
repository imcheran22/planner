"""Budgets for 9 combos across 3 region mixes. ₹ for two. Rates 29 Oct 2026: ₹1 = 271.22 VND, $1 = ₹95.26.
Every line: (label, basis, ₹, kind) with kind in quote / listing / cap / proxy."""
import json, importlib.util, io, contextlib, os
HERE = os.path.dirname(os.path.abspath(__file__))
VND = 271.22; USD = 25836.19 / VND
v = lambda x: round(x / VND); u = lambda x: round(x * USD)
spec = importlib.util.spec_from_file_location('b', os.path.join(HERE, 'budget.py')); b = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(b)

VISA = ('E-visa + SIM', '₹2,846 pp, Reddit traveller actual', 5692, 'quote', 'visa')
FARE = ('Farewell dinner', '1,000,000 VND pp, Google price band', v(2000000), 'quote', 'eat')
def food(days, pq_nights=0):
    rows = [('Everyday food and coffee', f'Cap ₹2,770/day × {days} days', round(2770 * days), 'cap', 'eat')]
    if pq_nights: rows.append(('Phu Quoc food premium', f'Cap ₹1,000/day × {pq_nights} (Reddit: "food is overpriced compared to the mainland")', 1000 * pq_nights, 'cap', 'eat'))
    return rows
# --- shared activity lines
HOIAN = [('Hoi An Old Town', '120,000 VND × 2', v(240000), 'quote', 'do'), ('Lantern boat', '150,000 VND per boat', v(150000), 'quote', 'do'),
         ('Cooking class + basket boat', '$46 × 2, Cookly', u(92), 'quote', 'do')]
MYSON = [('My Son sunrise tour + ticket', '(600,000 + 150,000 VND) × 2', v(1500000), 'quote', 'do')]
BANA = [('Ba Na Hills ticket', '1,000,000 VND × 2', v(2000000), 'quote', 'do'), ('Ba Na coaster, 3 rides each', '250,000 VND × 2 (vlog, Feb 2026)', v(500000), 'quote', 'do'),
        ('Grab to and from Ba Na', '$15 each way (YouTube, Oct 2026)', u(30), 'quote', 'move')]
PQ = [('Hon Thom cable car (Sun World)', '850,000 VND × 2 (2026 price list)', v(1700000), 'quote', 'do'),
      ('VinWonders Phu Quoc (roller coasters)', '950,000 VND × 2 (official site 2026)', v(1900000), 'quote', 'do')]
CRUISE_LH = ('Lan Ha Bay overnight cruise, balcony cabin', '₹35,000 for two, Peony Deluxe Balcony quote (r/InternationalTravelIN, Sep 2026)', 35000, 'quote', 'stay')
HANOI_N = lambda n: (f'Hanoi Old Quarter hotel, {n} night{"s" if n > 1 else ""}', 'Cap ₹6,500/night (4★ boutique $40–130 in 2026 guides)', 6500 * n, 'cap', 'stay')
BLR_OPENJAW = ('Flights: Bengaluru → Hanoi (IndiGo via Kolkata) + Da Nang → Bengaluru (AirAsia via Bangkok)', '₹15,000 + ₹14,000 pp, a Bengaluru group\'s actual fares, Nov 2025 (r/InternationalTravelIN)', 58000, 'quote', 'fly')
HAN_DAD = ('Domestic flight Hanoi → Da Nang + bags', '₹3,000 pp actual (r/InternationalTravelIN, Nov 2025) + bag cap ₹1,000 pp', 8000, 'quote', 'fly')
GL_SEA = ('Golden Lotus Grand, sea view, per night', '₹12,184 Booking listing for 26 Jan', 12184, 'listing', 'stay')
COZY2 = ('Cozy An, Hoi An, 2 nights', '₹12,778 Booking listing for 22–24 Jan', 12778, 'listing', 'stay')
COZY2P = ('Cozy An, Hoi An, 2 nights', '₹12,778 (22–24 Jan listing used as proxy)', 12778, 'proxy', 'stay')

def from_v2(key, name):
    c = b.combos[key]; cat = {'E-visa + SIM': 'visa', 'Everyday food and coffee, 6.5 days': 'eat', 'Farewell dinner': 'eat'}
    rows = [(f'Flights: {c["flights"][0]}', '', c['flights'][1], 'quote', 'fly')]
    rows += [(h[0], h[1], h[2], 'proxy' if h[3] == 'assumed' else 'listing', 'stay') for h in c['hotels']]
    for r in b.common + c['extra']:
        k = cat.get(r[0], 'move' if any(w in r[0] for w in ['Grab', 'car', 'train']) else 'do')
        rows.append((r[0], r[1], r[2], r[3], k))
    return rows

C = {}
C['1a'] = from_v2('C', 'Da Nang first'); C['1b'] = from_v2('A', 'Classic'); C['1c'] = from_v2('D', 'Bengaluru lean')
C['2a'] = [BLR_OPENJAW, HAN_DAD, HANOI_N(1), CRUISE_LH, ('Hanoi ↔ Lan Ha port transfer', 'Cap ₹3,000 for two (check if the cruise includes it)', 3000, 'cap', 'move'),
           ('Hoi An TNT Villa, 2 nights', '₹8,338 (22–24 Jan listing used as proxy)', 8338, 'proxy', 'stay'),
           ('Golden Lotus Grand, city view, 1 night', '₹6,019 Booking listing (26 Jan)', 6019, 'listing', 'stay'),
           ('Golden Lotus Grand, sea view, 1 night', '₹12,184 (26 Jan listing as proxy for 27 Jan)', 12184, 'proxy', 'stay'),
           ('Grab: airports, Hoi An ↔ Da Nang, city', 'Cap', 5000, 'cap', 'move')] + HOIAN + BANA + [VISA] + food(6.5)
C['2b'] = [BLR_OPENJAW, HAN_DAD, HANOI_N(1), ('Ninh Binh (Tam Coc) hotel, 1 night', 'Cap ₹5,000 (not collected)', 5000, 'cap', 'stay'),
           ('Hanoi → Ninh Binh → Noi Bai airport, car', 'Cap ₹4,000 for two (not collected)', 4000, 'cap', 'move'),
           (GL_SEA[0].replace('per night', '2 nights'), '₹12,184 × 2 (26 Jan listing as proxy)', 24368, 'proxy', 'stay'), COZY2P,
           ('Trang An boat + Mua Cave', '₹1,167 pp actual (r/InternationalTravelIN, Nov 2025)', 2334, 'quote', 'do'), ('Bai Dinh Pagoda', '₹513 pp actual (r/InternationalTravelIN, Nov 2025)', 1026, 'quote', 'do'),
           ('Han River cruise, Sun 24 fire show', '$21.30 × 2', u(42.6), 'quote', 'do'), ('Grab: airports, Hoi An ↔ Da Nang, city', 'Cap', 5000, 'cap', 'move')] + HOIAN + BANA + [VISA] + food(6.5) + [FARE]
C['2c'] = [BLR_OPENJAW, HAN_DAD, ('Sapa hotel with valley view, 2 nights', 'Cap ₹5,500/night (not collected)', 11000, 'cap', 'stay'), HANOI_N(1), COZY2P,
           ('Golden Lotus Grand, sea view, 1 night', '₹12,184 Booking listing (26 Jan as proxy)', 12184, 'proxy', 'stay'),
           ('Limousine van Noi Bai → Sapa → Hanoi', '450,000 VND × 2 people × 2 trips (2026 guides: 320k–450k)', v(1800000), 'quote', 'move'),
           ('Fansipan cable car + Muong Hoa train', '(850,000 + 200,000 VND) × 2', v(2100000), 'quote', 'do'),
           ('Sapa alpine coaster', '₹584 pp actual (r/InternationalTravelIN, Nov 2025)', 1168, 'quote', 'do'), ('Rong May glass bridge', '₹1,708 pp actual (r/InternationalTravelIN, Nov 2025)', 3416, 'quote', 'do'),
           ('Grab: airports, Hoi An ↔ Da Nang, city', 'Cap', 5000, 'cap', 'move')] + HOIAN + [VISA] + food(6.5) + [FARE]
C['3a'] = [('Flights: Chennai ↔ Da Nang via Kuala Lumpur', '₹22,838 pp return, AirAsia on Kayak (not for your dates)', 45676, 'quote', 'fly'),
           ('Domestic flights Da Nang ↔ Phu Quoc + bags', 'Cap ₹4,500 pp per leg (Skyscanner from €44; Tamil vlog ₹3k–5k)', 18000, 'cap', 'fly'),
           COZY2, ('Phu Quoc sea-view hotel, 3 nights', 'Cap ₹11,000/night (Trip.com 4★ Long Beach $66–189)', 33000, 'cap', 'stay'),
           ('Golden Lotus Grand, city view, 1 night', '₹6,019 Booking listing (26 Jan as proxy)', 6019, 'proxy', 'stay'),
           ('Grab: airports, Phu Quoc, city', 'Cap', 6000, 'cap', 'move')] + HOIAN + MYSON + PQ + [VISA] + food(6.5, 3) + [FARE]
C['3b'] = [('Flights: Bengaluru ↔ Saigon nonstop (VietJet)', '$96–122 one way on VietJet fare page (undated) → ~$218 pp return', u(436), 'quote', 'fly'),
           ('Domestic flights Saigon ↔ Phu Quoc + bags', 'Cap ₹4,000 pp per leg (Tamil vlog ₹3k; VNA from 782k VND)', 16000, 'cap', 'fly'),
           ('Saigon hotel, 2 nights', 'Cap ₹5,500/night (not collected)', 11000, 'cap', 'stay'),
           ('Phu Quoc sea-view hotel, 4 nights', 'Cap ₹10,000/night (Trip.com 4★ Long Beach $66–189)', 40000, 'cap', 'stay'),
           ('Saigon cooking class', '$45 × 2 cap (Hanoi listings $39–57; Saigon not collected)', u(90), 'cap', 'do'),
           ('Cu Chi tunnels or Mekong day trip', 'Cap ₹6,000 for two (not collected)', 6000, 'cap', 'do'),
           ('Kiss of the Sea show, Sunset Town', '950,000 VND × 2 (2026 guides)', v(1900000), 'quote', 'do'),
           ('Grab: airports, Phu Quoc, city', 'Cap', 6000, 'cap', 'move')] + PQ + [VISA] + food(6.5, 4) + [FARE]
C['3c'] = [('Flights: Bengaluru → Hanoi (IndiGo via Kolkata) + Saigon → Bengaluru nonstop (VietJet)', '₹15,000 pp (T24) + $96 pp (VietJet fare page, undated)', 30000 + u(192), 'quote', 'fly'),
           ('Domestic flights Hanoi → Phu Quoc → Saigon + bags', '₹5,000 + ₹3,000 pp (Tamil vlog, Oct 2026) + bag cap ₹1,000 pp per leg', 20000, 'quote', 'fly'),
           HANOI_N(1), CRUISE_LH, ('Hanoi ↔ Lan Ha port transfer', 'Cap ₹3,000 for two', 3000, 'cap', 'move'),
           ('Phu Quoc sea-view hotel, 3 nights', 'Cap ₹10,000/night (Trip.com 4★ Long Beach $66–189)', 30000, 'cap', 'stay'),
           ('Hanoi cooking class', '$45 × 2 (2026 listings $39–57)', u(90), 'quote', 'do'),
           ('Grab: airports, Phu Quoc, city', 'Cap', 5000, 'cap', 'move')] + PQ + [VISA] + food(5.5, 3)

out = {}
for k, rows in C.items():
    cats = {}
    for r in rows: cats[r[4]] = cats.get(r[4], 0) + round(r[2])
    tot = sum(round(r[2]) for r in rows)
    out[k] = dict(total=tot, buffer=200000 - tot, cats=cats, lines=[dict(item=r[0], basis=r[1], inr=round(r[2]), kind=r[3], cat=r[4]) for r in rows])
    print(f'{k}: total {tot:,}  buffer {200000 - tot:,}', cats)
json.dump(out, open(os.path.join(HERE, 'budget_v3.json'), 'w'), ensure_ascii=False)
