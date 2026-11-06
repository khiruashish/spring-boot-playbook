import sys
from animlib import Anim

a = Anim("pb-bp", "Backpressure — demand flows up, data flows down",
         "Reactive backpressure",
         "A reactive pipeline from a source through an operator and WebFlux on Netty to a slow mobile client. Demand "
         "travels upstream as request(n) signals and items travel downstream only as requested. With a paged R2DBC "
         "export and limitRate, a full socket pauses the source. With a Redis pub/sub push source, "
         "onBackpressureDrop and sample discard positions nobody asked for.", 800, 300, top=40)

# routes first, so they run behind the boxes; tokens are drawn on top
a.route("d_all", [(616, 108), (156, 108)])
a.route("d_cn", [(616, 108), (536, 108)])
a.route("f_all", [(156, 168), (616, 168)])
a.route("f_sn", [(156, 168), (536, 168)])
a.route("f_so", [(156, 168), (271, 168)])

a.box("src", 16, 80, 140, 120)
a.box("op", 196, 80, 150, 120)
a.box("net", 386, 80, 150, 120, "WebFlux · Netty", ["TCP send buffer"])
a.box("cli", 616, 80, 168, 120, "mobile client", ["reads slowly on 3G"])
a.text(400, 70, "← demand flows upstream as request(n)", "t-xs t-warn", "middle")
a.text(400, 214, "data flows downstream as onNext →", "t-xs t-sub", "middle")
a.open("paged")
a.text(86, 136, "R2DBC query", "t-b", "middle")
a.text(86, 152, "paged export", "t-xs t-sub", "middle")
a.text(271, 136, "limitRate(100)", "t-b t-mono t-11", "middle")
a.text(271, 152, "prefetch in batches", "t-xs t-sub", "middle")
a.close()
a.open("live")
a.text(86, 136, "Redis pub/sub", "t-b", "middle")
a.text(86, 152, "rider positions", "t-xs t-sub", "middle")
a.text(271, 130, "onBackpressureDrop()", "t-b t-mono t-10", "middle")
a.text(271, 148, "sample(2s)", "t-b t-mono t-10", "middle")
a.close()

a.panel(16, 220, 768, 76)
a.chip("demand", 28, 229, 366, "Outstanding demand", {"n100": ("request(100)", "active"), "zero": ("0 · nobody asks", "suspended"),
                                                      "none": ("—", "none")})
a.chip("buffer", 406, 229, 366, "Send buffer", {"low": ("draining", "active"), "full": ("FULL", "rolledback")})
a.chip("source", 28, 259, 366, "Source", {"reading": ("reading", "active"), "paused": ("PAUSED · cursor idle", "suspended"),
                                          "push": ("pushing · can't pause", "rolledback")})
a.chip("dropped", 406, 259, 366, "Dropped (metered)", {"zero": ("0", "none"), "some": ("stale positions dropped", "committed")})

a.scene("paged", "1 · Demand drives the source", [
    {"par": "d_all:signal", "hl": "cli op src", "tx": {"demand": "n100", "buffer": "low", "source": "reading"}, "text": "The client subscribes and demand travels <strong>upstream</strong> as <code>request(n)</code>. Netty keeps asking while the socket can take data, and <code>limitRate(100)</code> turns that into requests for 100 rows at a time."},
    {"par": "f_all f_all f_all f_all", "hl": "cli", "text": "Rows flow down only as fast as they were requested. Nothing is pushed that nobody asked for."},
    {"hl": "cli", "warn": "cli", "tx": {"buffer": "full"}, "text": "The mobile client reads slowly, so the TCP send buffer fills up…"},
    {"par": "f_sn f_sn", "hl": "net", "warn": "net", "tx": {"demand": "zero"}, "text": "…and Netty stops requesting. Rows already requested arrive and wait, but no new demand goes upstream."},
    {"hl": "src", "tx": {"source": "paused"}, "text": "So the source simply <strong>pauses</strong>: the database cursor isn't read any further and memory stays flat. For a paged export, that's exactly what you want."},
    {"par": "d_all:signal f_all f_all", "hl": "cli src", "tx": {"buffer": "low", "demand": "n100", "source": "reading"}, "text": "When the client catches up, demand resumes and so does the source."},
])

a.scene("live", "2 · A push source (live feed)", [
    {"par": "f_sn f_sn f_sn f_sn f_sn", "hl": "src", "warn": "src", "tx": {"source": "push", "demand": "zero", "buffer": "full", "dropped": "zero"}, "text": "Rider positions come from Redis pub/sub: a <strong>push</strong> source that can't be paused. Positions keep arriving whether or not anyone asked."},
    {"hl": "net cli", "warn": "net", "text": "With a slow client and no strategy, they would pile up in a buffer per connection: a memory leak with extra steps."},
    {"par": "f_so:error f_so:error f_so:error", "hl": "op", "tx": {"dropped": "some"}, "text": "<code>onBackpressureDrop()</code> discards positions nobody has asked for (and counts them in a metric). For live data, only the newest value matters anyway."},
    {"par": "d_all:signal f_all", "hl": "op cli", "tx": {"buffer": "low", "demand": "n100"}, "text": "<code>sample(2s)</code> sends at most one position every two seconds, so the client always gets a recent position and nothing piles up. Financial events are different: never drop them; persist and let clients replay."},
])

a.write(sys.argv[1])
