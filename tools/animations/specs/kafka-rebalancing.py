import sys
from animlib import Anim

a = Anim("pb-kfk", "Consumer group rebalancing — cooperative sticky, eager, and a crash",
         "Kafka consumer group rebalancing",
         "Four partitions of grocery.order.placed.v1 are assigned to consumers in the inventory group. When a third "
         "consumer joins, cooperative sticky assignment moves only partition 3 after committing its offsets, while an "
         "eager rebalance revokes everything first. When a consumer crashes mid-batch, its partitions move after the "
         "session timeout and the new owner replays records after the last committed offset.", 800, 396, top=20)

a.box("coord", 262, 30, 196, 42, "Group coordinator", ["broker · __consumer_offsets"], title_cls="t-11")
a.box("topic", 16, 40, 200, 250, "grocery.order.placed.v1", kind="shell")
PY = [92, 146, 200, 254]
for i, y in enumerate(PY):
    a.box(f"p{i}", 36, y - 22, 160, 44, f"Partition {i}")
a.box("group", 470, 40, 314, 250, "consumer group: inventory", kind="shell")
CY = [102, 180, 258]
for j, (y, pod) in enumerate(zip(CY, "ABC")):
    a.box(f"c{j + 1}", 520, y - 28, 200, 56, f"consumer-{j + 1}", [f"pod {pod}"])
a.toggles.append("c3")

for i, py in enumerate(PY):
    for j, cy in enumerate(CY):
        a.link(f"a{i}{j + 1}", [(196, py), (520, cy)])

for j, cy in enumerate(CY):
    if j == 2:
        a.raw('<g data-node="c3lane">')
    a.route(f"c{j + 1}co", [(520, cy - 14), (496, cy - 14), (496, 86), (360, 86), (360, 72)])
    if j == 2:
        a.raw("</g>")
a.toggles.append("c3lane")

a.panel(16, 304, 768, 84)
a.chip("group", 28, 314, 360, "Group", {"stable": ("STABLE", "active"), "rebal": ("REBALANCING", "suspended"),
                                        "stw": ("ALL PARTITIONS REVOKED", "rolledback")})
a.chip("dups", 28, 350, 360, "Records processed twice", {"zero": ("NONE", "committed"), "some": ("20 (100–119)", "rolledback")})
a.chip("offs", 404, 314, 368, "Partition 3", {"lag": ("processed 120 · committed 100", "suspended"),
                                              "synced": ("committed 120", "committed"),
                                              "replay": ("resumes at 100", "rolledback")})

BASE = "c1 c2 a01 a11 a22 a32"

a.scene("sticky", "1 · Scale out (cooperative sticky)", [
    {"hl": "c1 c2", "tx": {"group": "stable"}, "text": "Two pods in the <code>inventory</code> group share four partitions. Each partition has exactly <strong>one owner</strong>, which is how per-key ordering survives."},
    {"path": "c3co", "show": BASE + " c3 c3lane", "hl": "c3 coord", "tx": {"group": "rebal"}, "text": "A third pod starts and <strong>joins the group</strong>. The coordinator triggers a rebalance."},
    {"path": "c2co", "show": BASE + " c3 c3lane", "hl": "c2 p3", "tx": {"offs": "synced"}, "text": "With <strong>cooperative sticky</strong> assignment, only partitions that must move are revoked. consumer-2 gives up partition 3, and Spring Kafka commits its processed offsets in the revoke callback first."},
    {"show": "c1 c2 c3 c3lane a01 a11 a22 a33", "hl": "c3 p3", "tx": {"group": "stable", "dups": "zero"}, "text": "consumer-3 picks up partition 3 at the committed offset. Partitions 0–2 <strong>never stopped</strong>, and nothing was read twice."},
], show=BASE)

a.scene("eager", "2 · Eager rebalance", [
    {"path": "c3co", "show": BASE + " c3 c3lane", "hl": "c3 coord", "tx": {"group": "rebal"}, "text": "The same scale-out, using the older <strong>eager</strong> protocol."},
    {"show": "c1 c2 c3 c3lane", "hl": "c1 c2", "warn": "c1 c2", "tx": {"group": "stw"}, "text": "Every consumer revokes <strong>all</strong> of its partitions and stops: a stop-the-world pause for the whole group, even though only one partition needed to move."},
    {"show": "c1 c2 c3 c3lane a01 a11 a22 a33", "hl": "c1 c2 c3", "tx": {"group": "stable"}, "text": "Partitions are reassigned and everyone resumes. During a rolling deploy this repeats for every pod, which is why cooperative sticky is the modern default and static membership (<code>group.instance.id</code>) helps restarts."},
], show=BASE)

a.scene("crash", "3 · Crash and replay", [
    {"hl": "c2 p3", "tx": {"group": "stable", "offs": "lag"}, "text": "consumer-2 is mid-batch on partition 3. It has processed up to offset 120 but last committed 100, because offsets are committed <em>after</em> processing."},
    {"warn": "c2", "dim": "c2", "text": "Pod B <strong>crashes</strong>. Nothing more gets committed, and the coordinator only notices when heartbeats stop and <code>session.timeout.ms</code> expires."},
    {"show": "c1 c2 a01 a11", "hl": "coord", "dim": "c2", "tx": {"group": "rebal"}, "text": "The coordinator removes consumer-2 from the group and rebalances its partitions."},
    {"show": "c1 a01 a11 a21 a31", "hl": "c1 p3", "tx": {"group": "stable", "offs": "replay", "dups": "some"}, "text": "consumer-1 resumes partition 3 from the last <strong>committed</strong> offset, 100. Records 100–119 are processed a second time."},
    {"show": "c1 a01 a11 a21 a31", "hl": "c1", "text": "That's at-least-once delivery working as designed. The defence is an <strong>idempotent consumer</strong> (§2.9): an inbox table or a conditional update makes the replay harmless."},
], show=BASE)

a.write(sys.argv[1])
