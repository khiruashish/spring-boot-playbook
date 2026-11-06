import sys
from animlib import Anim

a = Anim("pb-vt", "Virtual threads — six requests on two carrier threads, and what pinning does",
         "Virtual thread mounting",
         "Six virtual threads share two carrier threads from a ForkJoinPool. When a mounted virtual thread blocks on "
         "database or HTTP I/O it unmounts, freeing its carrier for another virtual thread, and later remounts on any "
         "free carrier. A native (JNI) call pins its virtual thread, blocking the carrier for the whole call.",
         800, 382, top=30)

VY = [62, 108, 154, 200, 246, 292]
a.text(16, 44, "Virtual threads (one per request)", "t-sm t-b")
for i, y in enumerate(VY):
    a.box(f"v{i + 1}", 16, y - 18, 150, 36, f"VT{i + 1} · request {i + 1}", title_cls="t-11")
a.box("pool", 286, 40, 210, 272, "Carrier pool · ForkJoinPool", kind="shell")
CY = [128, 236]
for j, y in enumerate(CY):
    a.box(f"c{j + 1}", 306, y - 36, 170, 72, f"carrier {j + 1}", ["platform (OS) thread"])
a.text(391, 300, "size = CPU cores (here 2)", "t-xs t-sub", "middle")
a.box("io", 620, 128, 164, 110, "Database / HTTP", ["blocking I/O"])
a.open("pin")
a.box("jni", 620, 260, 164, 52, "native library", ["JNI call"])
a.close()

for i, vy in enumerate(VY):
    for j, cy in enumerate(CY):
        a.link(f"m{i + 1}{j + 1}", [(166, vy), (306, cy)])
a.route("io1", [(476, 128), (548, 128), (548, 170), (620, 170)])
a.route("io2", [(476, 236), (548, 236), (548, 196), (620, 196)])
a.open("pin")
a.route("jni1", [(476, 140), (520, 140), (520, 286), (620, 286)])
a.close()

a.panel(16, 324, 768, 50)
a.chip("flight", 28, 333, 236, "In flight", {"n2": ("2 requests", "active"), "n4": ("4 requests", "active"),
                                             "n6": ("6 requests", "committed"), "n3": ("3 requests", "suspended")})
a.chip("carriers", 276, 333, 260, "Carriers", {"busy": ("2 of 2 running", "active"), "pinned": ("1 PINNED", "rolledback")})
a.chip("os", 548, 333, 224, "OS threads used", {"two": ("2", "committed")})

ALLV = "v1 v2 v3 v4 v5 v6 c1 c2"
a.scene("mount", "1 · Block, unmount, remount", [
    {"show": ALLV + " m11 m22", "hl": "v1 v2 c1 c2", "dim": "v3 v4 v5 v6", "tx": {"flight": "n2", "carriers": "busy", "os": "two"}, "text": "Six requests, six virtual threads, but only <strong>two carrier threads</strong>: a <code>ForkJoinPool</code> sized to the CPU count. VT1 and VT2 are mounted and running."},
    {"par": "io1 io2", "hl": "io", "dim": "v3 v4 v5 v6", "text": "Both make a blocking JDBC call. On a virtual thread, that doesn't block the carrier…"},
    {"show": ALLV + " m31 m42", "hl": "v3 v4 c1 c2", "dim": "v1 v2 v5 v6", "tx": {"flight": "n4"}, "text": "…the JVM <strong>unmounts</strong> VT1 and VT2 (their stacks are parked on the heap) and mounts VT3 and VT4 on the freed carriers."},
    {"par": "io1 io2", "show": ALLV + " m51 m62", "hl": "v5 v6 c1 c2", "dim": "v1 v2 v3 v4", "tx": {"flight": "n6"}, "text": "They block too and unmount, and VT5 and VT6 run. <strong>Six requests are in flight on two OS threads.</strong>"},
    {"par": "io1:rev io2:rev", "show": ALLV + " m12 m21", "hl": "v1 v2 c1 c2", "dim": "v3 v4 v5 v6", "text": "When VT1's and VT2's results arrive they <strong>remount on whichever carrier is free</strong>, not necessarily the one they started on, and carry on where they left off."},
    {"show": ALLV + " m12 m21", "hl": "io", "text": "So virtual threads make <em>blocking</em> code scale; they don't make CPU work faster. The database pool is still bounded, which is why §5.4 adds a bulkhead."},
])

a.scene("pin", "2 · A pinned carrier", [
    {"show": ALLV + " m11 m22", "hl": "v1 v2 c1 c2", "dim": "v3 v4 v5 v6", "tx": {"flight": "n2", "carriers": "busy", "os": "two"}, "text": "Same pool. This time VT1 calls into a native library through JNI, and the native code blocks."},
    {"par": "jni1", "show": ALLV + " m11 m22", "hl": "v1 jni", "warn": "c1", "dim": "v3 v4 v5 v6", "tx": {"carriers": "pinned"}, "text": "A virtual thread can't unmount while a native frame is on its stack: it is <strong>pinned</strong>, and carrier 1 is blocked for the whole call."},
    {"par": "io2", "show": ALLV + " m11 m32", "hl": "v3 c2", "warn": "c1", "dim": "v2 v4 v5 v6", "tx": {"flight": "n3"}, "text": "Carrier 2 still works normally: VT2 unmounts on its I/O and VT3 takes its place."},
    {"show": ALLV + " m11 m32", "hl": "v4 v5 v6", "warn": "c1", "dim": "v2", "text": "But half the pool is gone. Pin both carriers and <em>every</em> virtual thread in the application waits, including ones that have nothing to do with the native call."},
    {"show": ALLV + " m11 m32", "warn": "c1", "text": "On Java 21–23, <code>synchronized</code> around I/O pinned the same way; JDK 24 removed that (JEP 491). Find what's left with JFR <code>jdk.VirtualThreadPinned</code> events (§5.5)."},
], show=ALLV)

a.write(sys.argv[1])
