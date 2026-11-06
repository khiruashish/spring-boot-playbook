import sys
from animlib import Anim

a = Anim("pb-prop", "Propagation in motion — <code>REQUIRED</code>, the rollback-only trap, <code>REQUIRES_NEW</code>, <code>NESTED</code>",
         "Transaction propagation",
         "ImportService.importAll() runs in transaction tx1 and calls RowImporter.importRow() through its proxy. "
         "Depending on propagation, the inner call joins tx1, marks it rollback-only, suspends it and starts tx2 on a "
         "second connection, or sets a savepoint. Chips show both transactions, the rollback-only flag, the outcome, "
         "and the two pooled connections.", 800, 380)

a.box("outer", 16, 92, 170, 84, "importAll()", ["ImportService", "@Transactional · tx1"], mono=True)
a.box("proxy", 222, 40, 338, 218, "RowImporter proxy", kind="shell")
a.box("interceptor", 238, 70, 112, 172, "Transaction", kind="band", extra=[("Interceptor", "t-b")])
a.box("target", 366, 70, 180, 172, kind="target")
a.text(380, 92, "RowImporter (target)", "t-b")
a.box("m", 380, 116, 152, 64, "importRow(row)", mono=True)
for sid, ann in (("req trap", "@Transactional (REQUIRED)"), ("new", "REQUIRES_NEW"), ("nested", "NESTED")):
    a.open(sid)
    a.text(456, 168, ann, "t-xs t-mono t-accent", "middle")
    a.close()

a.route("call", [(186, 128), (238, 128)])
a.route("ret", [(238, 146), (186, 146)])
a.route("in", [(350, 148), (380, 148)])

a.text(590, 58, "Connection pool (max 2)", "t-sm t-b")
CONN = {"idle": ("idle", "none"), "tx1": ("tx1", "active"), "held": ("tx1 · waiting", "suspended"), "tx2": ("tx2", "active")}
a.chip("conn1", 590, 70, 194, "Connection #1", CONN)
a.chip("conn2", 590, 110, 194, "Connection #2", CONN)
a.chip("sp", 590, 150, 194, "Savepoint", {"set": ("SP1", "suspended"), "rolled": ("ROLLED BACK", "rolledback")})

a.panel(16, 276, 768, 94, "Transactions")
a.chip("tx1", 150, 288, 304, "tx1 · importAll()")
a.chip("tx2", 470, 288, 304, "inner · importRow()",
       {"joined": ("JOINS tx1", "committed"), "savepoint": ("INSIDE tx1 · SP1", "suspended"),
        "tosp": ("UNDONE TO SP1", "rolledback"), "done": ("FINISHED", "none")})
a.chip("flag", 150, 328, 304, "rollback-only flag", {"no": ("not set", "none"), "yes": ("SET", "rolledback")})
a.chip("out", 470, 328, 304, "Outcome", {"ok": ("COMMITTED", "committed"),
                                         "boom": ("UnexpectedRollbackException", "rolledback")})

base = {"conn1": "tx1", "conn2": "idle", "flag": "no", "tx1": "active"}

a.scene("req", "1 · <code>REQUIRED</code> joins", [
    {"hl": "outer", "tx": {}, "text": "<code>importAll()</code> is <code>@Transactional</code>, so its own proxy already began <strong>tx1</strong> on connection #1. It loops over rows and calls <code>importer.importRow(row)</code>."},
    {"path": "call", "hl": "interceptor", "text": "The call reaches <code>RowImporter</code>'s proxy. <code>importRow()</code> uses the default propagation, <code>REQUIRED</code>."},
    {"path": "in", "hl": "interceptor m", "tx": {"tx2": "joined"}, "text": "A transaction is already bound to the thread, so <code>REQUIRED</code> <strong>joins</strong> it. No new transaction and no new connection: the row's <code>INSERT</code> runs in tx1."},
    {"path": "in:rev,ret", "hl": "outer", "tx": {"tx2": "done"}, "text": "<code>importRow()</code> returns. A joined call never commits by itself; only the boundary that started the transaction does."},
    {"hl": "outer", "tx": {"tx1": "committed", "conn1": "idle", "out": "ok"}, "text": "<code>importAll()</code> finishes and its proxy <strong>commits tx1 once</strong>, covering every row, then returns connection #1 to the pool."},
], base)

a.scene("trap", "2 · The rollback-only trap", [
    {"path": "call,in", "hl": "m", "tx": {"tx2": "joined"}, "text": "Same setup as §5.2, but this row is invalid. <code>importRow()</code> joins tx1 and throws a <code>RuntimeException</code>."},
    {"path": "in:rev", "token": "error", "hl": "interceptor", "warn": "interceptor", "tx": {"flag": "yes", "tx2": "done"}, "text": "The inner proxy didn't start tx1, so it can't roll it back. It marks the shared transaction <strong>rollback-only</strong> and rethrows."},
    {"path": "ret", "token": "error", "hl": "outer", "text": "<code>importAll()</code> catches the exception, counts the row as failed and carries on. The flag stays set: catching an exception doesn't clear it."},
    {"hl": "outer", "warn": "outer", "tx": {"tx1": "rolledback", "conn1": "idle", "out": "boom"}, "text": "At the end the outer proxy tries to commit. The transaction is rollback-only, so Spring rolls back <em>everything</em>, good rows included, and throws <code>UnexpectedRollbackException</code>."},
], base)

a.scene("new", "3 · <code>REQUIRES_NEW</code>", [
    {"path": "call", "hl": "outer interceptor", "text": "Fix A from §5.2: <code>importRow()</code> uses <code>REQUIRES_NEW</code>. <code>importAll()</code> calls it while tx1 is active."},
    {"path": "in", "hl": "interceptor m", "tx": {"tx1": "suspended", "tx2": "active", "conn1": "held", "conn2": "tx2"}, "text": "The interceptor <strong>suspends tx1</strong> (unbinds it from the thread) and <strong>begins tx2 on a second connection</strong>. tx1 keeps holding connection #1 while it waits."},
    {"path": "in:rev", "token": "error", "hl": "interceptor", "tx": {"tx2": "rolledback", "conn2": "idle"}, "text": "The bad row throws. Only <strong>tx2 rolls back</strong>, and connection #2 goes back to the pool. Good rows each committed in their own tx2."},
    {"path": "ret", "token": "error", "hl": "outer", "tx": {"tx1": "active", "conn1": "tx1"}, "text": "tx1 resumes. <code>importAll()</code> catches the exception, and this time tx1 was never marked rollback-only."},
    {"hl": "outer", "tx": {"tx1": "committed", "conn1": "idle", "out": "ok"}, "text": "tx1 commits normally. The cost is in the pool panel: every <code>REQUIRES_NEW</code> level holds a second connection, and under load a pool can deadlock itself."},
], base)

a.scene("nested", "4 · <code>NESTED</code>", [
    {"path": "call", "hl": "outer interceptor", "text": "With <code>NESTED</code>, <code>importRow()</code> stays inside tx1 but behind a savepoint."},
    {"path": "in", "hl": "interceptor m", "tx": {"tx2": "savepoint", "sp": "set"}, "text": "The interceptor runs <code>SAVEPOINT SP1</code> on connection #1. Same transaction, same connection: the pool isn't touched."},
    {"path": "in:rev", "token": "error", "hl": "interceptor", "tx": {"tx2": "tosp", "sp": "rolled"}, "text": "The row fails: <code>ROLLBACK TO SAVEPOINT SP1</code> undoes just this row's work, and tx1 is <strong>not</strong> marked rollback-only."},
    {"path": "ret", "token": "error", "hl": "outer", "tx": {"sp": "none"}, "text": "<code>importAll()</code> catches the exception and moves on to the next row."},
    {"hl": "outer", "tx": {"tx1": "committed", "conn1": "idle", "out": "ok"}, "text": "tx1 commits every good row in one transaction on one connection. The catch: savepoints roll back the JDBC connection, not JPA's persistence context, which is why <code>NESTED</code> is meant for JDBC code."},
], base)

a.write(sys.argv[1])
