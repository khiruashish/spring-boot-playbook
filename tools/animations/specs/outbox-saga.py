import sys
from animlib import Anim

a = Anim("pb-obx", "Keeping data and events consistent — dual write, outbox + CDC, saga compensation",
         "Outbox, CDC and saga",
         "Scene 1: order-service commits an order and separately sends to Kafka, so the event can be lost or "
         "become a phantom. Scene 2: the order and an outbox row commit in one transaction; PostgreSQL's write-ahead "
         "log feeds Debezium through a replication slot, which publishes to Kafka for idempotent consumers. "
         "Scene 3: an orchestrated checkout saga reserves stock, the payment is declined, and a compensating "
         "ReleaseStock command cancels the order.", 800, 330)

a.box("svc", 16, 66, 150, 124)
a.text(91, 106, "order-service", "t-b", "middle")
a.open("dual outbox")
a.text(91, 128, "place(order)", "t-xs t-sub t-mono", "middle")
a.text(91, 144, "@Transactional", "t-xs t-accent t-mono", "middle")
a.close()
a.open("saga")
a.text(91, 128, "checkout saga", "t-xs t-sub", "middle")
a.text(91, 144, "orchestrator", "t-xs t-sub", "middle")
a.close()

# ---- scenes 1-2: database pipeline ----
a.open("dual outbox")
a.box("db", 200, 40, 210, 196, kind="target")
a.text(214, 62, "PostgreSQL · orders DB", "t-b")
a.box("orders", 216, 76, 178, 40, "orders", ["ORD-1042"], mono=True)
a.box("kafka", 620, 66, 164, 70, "Kafka", ["grocery.order.placed.v1"], sub_mono=True)
a.box("cons", 620, 176, 164, 60, "Consumers", ["inventory · notifications"])
a.route("write", [(166, 96), (216, 96)])
a.route("consume", [(702, 136), (702, 176)])
a.close()
a.open("dual")
a.route("send", [(91, 66), (91, 24), (702, 24), (702, 66)])
a.close()
a.open("outbox")
a.box("outbox", 216, 128, 178, 40, "outbox", ["OrderPlaced event"], mono=True)
a.box("wal", 216, 182, 178, 42, "WAL", ["logical replication slot"], kind="band")
a.box("deb", 446, 180, 140, 56, "Debezium", ["outbox event router"])
a.route("wout", [(166, 148), (216, 148)])
a.route("wal", [(305, 168), (305, 182)])
a.route("slot", [(394, 206), (446, 206)])
a.route("pub", [(516, 180), (516, 101), (620, 101)])
a.close()

# ---- scene 3: saga ----
a.open("saga")
a.box("inv", 290, 50, 200, 60, "inventory-service", ["ReserveStock · ReleaseStock"])
a.box("pay", 290, 150, 200, 60, "payment-service", ["AuthorizePayment"])
a.route("cmd1", [(166, 92), (228, 92), (228, 80), (290, 80)])
a.route("cmd2", [(166, 164), (228, 164), (228, 180), (290, 180)])
a.text(528, 60, "Persisted saga state", "t-sm t-b")
a.chip("saga", 528, 72, 256, "Saga", {"started": ("STARTED", "active"), "reserved": ("STOCK_RESERVED", "active"),
                                      "comp": ("COMPENSATING", "suspended"), "compd": ("COMPENSATED", "committed")})
a.chip("stock", 528, 112, 256, "Stock", {"reserved": ("RESERVED", "active"), "released": ("RELEASED", "committed")})
a.chip("payment", 528, 152, 256, "Payment", {"declined": ("DECLINED", "rolledback")})
a.chip("order", 528, 192, 256, "Order", {"pending": ("PENDING", "suspended"), "cancelled": ("CANCELLED", "rolledback")})
a.close()

a.open("dual outbox")
a.panel(16, 252, 768, 50)
a.chip("row", 24, 261, 186, "Order row", {"open": ("IN TX", "suspended"), "ok": ("COMMITTED", "committed"),
                                          "rb": ("ROLLED BACK", "rolledback")})
a.chip("event", 216, 261, 186, "Event", {"pub": ("PUBLISHED", "committed"), "lost": ("LOST", "rolledback"),
                                         "phantom": ("PHANTOM", "rolledback")})
a.close()
a.open("outbox")
a.chip("orow", 408, 261, 186, "Outbox row", {"pending": ("PENDING", "suspended"), "done": ("CAPTURED", "committed")})
a.chip("walc", 600, 261, 178, "WAL kept", {"ok": ("released", "none"), "grow": ("GROWING", "rolledback")})
a.close()

a.scene("dual", "1 · The dual-write problem", [
    {"path": "write", "hl": "svc orders", "tx": {"row": "ok"}, "text": "<code>place()</code> saves the order and the transaction <strong>commits</strong>…"},
    {"path": "send", "token": "error", "hl": "kafka", "warn": "kafka", "tx": {"event": "lost"}, "text": "…then the asynchronous <code>kafka.send()</code> fails (broker down, timeout). The order exists, but nobody will ever hear about it: the event is <strong>lost</strong>."},
    {"path": "send", "hl": "kafka", "tx": {"row": "open", "event": "pub"}, "text": "Flip the timing: the event is sent while the transaction is still open…"},
    {"hl": "orders", "warn": "orders", "tx": {"row": "rb", "event": "phantom"}, "text": "…and then the commit fails. Consumers act on an order that doesn't exist: a <strong>phantom event</strong>. No ordering of the two calls fixes this; two systems can't share one atomic commit."},
])

a.scene("outbox", "2 · Outbox + CDC", [
    {"path": "write,wout", "hl": "svc orders outbox", "tx": {"row": "open", "orow": "pending", "walc": "ok"}, "text": "Instead, write the order <em>and</em> an <code>OrderPlaced</code> row into the <code>outbox</code> table: same database, same transaction."},
    {"hl": "orders outbox", "tx": {"row": "ok"}, "text": "One <code>COMMIT</code> makes both durable, or neither. Nothing talks to Kafka inside the transaction."},
    {"path": "wal", "hl": "wal", "text": "PostgreSQL records the commit in its <strong>write-ahead log</strong>. Debezium reads it through a logical replication slot."},
    {"path": "slot", "hl": "deb", "text": "Debezium's outbox event router takes the topic from <code>aggregate_type</code> and the key from <code>aggregate_id</code>, so events for one order stay in order."},
    {"path": "pub", "hl": "kafka", "tx": {"event": "pub", "orow": "done"}, "text": "It publishes to <code>grocery.order.placed.v1</code> and confirms its position, which lets PostgreSQL free that WAL."},
    {"path": "consume", "hl": "cons", "text": "Consumers get the event <strong>at least once</strong>, so they must be idempotent (§2.5): an inbox table, a conditional update or an upsert."},
    {"hl": "deb wal", "warn": "deb wal", "dim": "kafka cons", "tx": {"walc": "grow"}, "text": "The operational catch: if the connector stops, the slot keeps every WAL segment since its last confirmation and the disk fills up. Alert on replication slot lag."},
])

a.scene("saga", "3 · Saga with compensation", [
    {"path": "cmd1", "hl": "svc inv", "tx": {"saga": "started", "order": "pending"}, "text": "Checkout runs as an orchestrated saga. The coordinator persists <code>STARTED</code> and sends <code>ReserveStock</code> (through its outbox and Kafka, as in scene 2)."},
    {"path": "cmd1:rev", "hl": "svc", "tx": {"saga": "reserved", "stock": "reserved"}, "text": "<code>inventory-service</code> reserves the stock in its <em>own</em> local transaction and replies <code>StockReserved</code>. The coordinator persists <code>STOCK_RESERVED</code>."},
    {"path": "cmd2", "hl": "pay", "text": "Next command: <code>AuthorizePayment</code>."},
    {"path": "cmd2:rev", "token": "error", "hl": "svc", "warn": "pay", "tx": {"payment": "declined", "saga": "comp"}, "text": "The card is declined. There's no distributed rollback, because the reservation already committed in another database. The saga moves to <code>COMPENSATING</code>."},
    {"path": "cmd1", "hl": "inv", "text": "The coordinator sends <code>ReleaseStock</code>, a <strong>compensating action</strong>: a semantic undo, not a rollback."},
    {"path": "cmd1:rev", "hl": "svc", "tx": {"stock": "released", "saga": "compd", "order": "cancelled"}, "text": "Stock released, saga <code>COMPENSATED</code>, order <code>CANCELLED</code>. Every transition is persisted and idempotent; if compensation kept failing, the saga would go to <code>STUCK</code> for a human."},
])

a.write(sys.argv[1])
