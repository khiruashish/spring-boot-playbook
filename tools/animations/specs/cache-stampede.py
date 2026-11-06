import sys
from animlib import Anim

a = Anim("pb-stp", "Cache stampede — a hot key expires, and two ways to stop the herd",
         "Cache stampede",
         "Five concurrent requests for the same price hit the cache. When the key expires they all miss together and "
         "run the same expensive database query. With @Cacheable(sync = true) a per-key lock lets one caller load "
         "while the others wait. Jittered TTLs spread the expiry of many keys so reloads arrive as a trickle.",
         800, 350, top=30)

YS = [64, 110, 156, 202, 248]
for i, y in enumerate(YS):
    a.box(f"r{i + 1}", 16, y - 17, 110, 34, f"request {i + 1}", title_cls="t-11")
a.box("cache", 176, 40, 150, 236, "price cache", ["@Cacheable", "TTL 120 s"], kind="band", sub_mono=True)
a.box("db", 640, 110, 144, 90, "pricing DB", ["expensive query", "~300 ms"])
for i, y in enumerate(YS):
    a.route(f"in{i + 1}", [(126, y), (176, y)])
a.open("herd jitter")
for i, y in enumerate(YS):
    a.route(f"miss{i + 1}", d=f"M326 {y} C 480 {y} 560 155 640 155")
a.close()
a.open("sync")
a.box("lock", 410, 110, 150, 90, "per-key lock", ["sync = true", "one loader per key"], kind="band", sub_mono=True)
for i, y in enumerate(YS):
    a.route(f"lock{i + 1}", d=f"M326 {y} C 370 {y} 380 155 410 155")
a.route("load", [(560, 155), (640, 155)])
a.close()

a.panel(16, 292, 768, 50)
a.chip("key", 28, 301, 250, "key ATTA-5KG", {"fresh": ("FRESH", "active"), "expired": ("EXPIRED", "suspended"),
                                             "loading": ("LOADING · 1 caller", "committed")})
a.chip("dbq", 290, 301, 230, "DB queries", {"zero": ("0", "none"), "one": ("1", "committed"), "five": ("5 at once", "rolledback"),
                                            "herd": ("10,000 in 1 s", "rolledback"), "trickle": ("~250 / s", "committed")})
a.chip("exp", 532, 301, 240, "Expiries", {"same": ("all in the same second", "rolledback"), "spread": ("spread over 40 s", "committed")})

R = "r1 r2 r3 r4 r5"
IN = " ".join(f"in{i}" for i in range(1, 6))
OUT = " ".join(f"in{i}:rev" for i in range(1, 6))
MISS = " ".join(f"miss{i}" for i in range(1, 6))

a.scene("herd", "1 · The stampede", [
    {"par": IN, "hl": R + " cache", "tx": {"key": "fresh", "dbq": "zero"}, "text": "Five concurrent requests ask for the price of <code>ATTA-5KG</code>. The key is fresh…"},
    {"par": OUT, "hl": R, "text": "…so all five are cache hits, answered in about a millisecond. The database isn't touched."},
    {"hl": "cache", "tx": {"key": "expired"}, "text": "The 120-second TTL runs out."},
    {"par": IN, "hl": "cache", "warn": "cache", "text": "The next five requests arrive in the same instant, and <strong>every one of them misses</strong>…"},
    {"par": MISS, "hl": "db", "warn": "db", "tx": {"dbq": "five"}, "text": "…so all five run the same expensive query. At hundreds of requests per second, one hot key expiring can flatten the database: the <strong>thundering herd</strong>."},
    {"par": " ".join(f"miss{i}:rev" for i in range(1, 6)), "hl": "cache", "tx": {"key": "fresh"}, "text": "Five identical results come back and the same key is written five times. Four of those queries were wasted."},
])

a.scene("sync", "2 · One loader per key", [
    {"par": IN, "hl": "cache", "tx": {"key": "expired", "dbq": "zero"}, "text": "Same expiry, but the method is now <code>@Cacheable(sync = true)</code>."},
    {"par": " ".join(f"lock{i}" for i in range(1, 6)), "hl": "lock", "tx": {"key": "loading"}, "text": "All five misses meet a <strong>per-key lock</strong>. The first caller loads the value; the other four wait for its result instead of querying."},
    {"path": "load", "hl": "db", "tx": {"dbq": "one"}, "text": "Exactly <strong>one query</strong> reaches the database."},
    {"path": "load:rev", "hl": "lock cache", "tx": {"key": "fresh"}, "text": "The loader stores the value in the cache and releases the lock…"},
    {"par": OUT, "hl": R, "text": "…and all five requests get the same value. Note that <code>sync = true</code> locks <em>inside one JVM</em> (Caffeine); across pods with Redis you need a locking cache writer, a distributed lock, or stale-while-revalidate."},
])

a.scene("jitter", "3 · Many keys, one TTL", [
    {"hl": "cache", "tx": {"key": "fresh", "dbq": "zero", "exp": "same"}, "text": "A different herd: after a deploy, warm-up writes 10,000 prices at once, all with exactly 120 s TTL."},
    {"par": MISS, "hl": "db", "warn": "db cache", "tx": {"key": "expired", "dbq": "herd"}, "text": "Two minutes later they all expire <strong>in the same second</strong>. It's a stampede across keys, not just on one."},
    {"hl": "cache", "tx": {"key": "fresh", "dbq": "zero", "exp": "spread"}, "text": "Fix: <strong>jitter</strong>. With TTL = 120 s ± 20 s (§5.4), expiries spread over 40 seconds…"},
    {"par": "miss2 miss4", "hl": "db", "tx": {"dbq": "trickle"}, "text": "…so the database sees a steady trickle of reloads instead of a spike."},
])

a.write(sys.argv[1])
