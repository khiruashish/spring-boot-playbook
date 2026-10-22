import sys, time
from playwright.sync_api import sync_playwright
src, out = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1100, "height": 1400})
    pg.set_default_timeout(1_800_000)
    t = time.time()
    pg.goto("file://" + src, wait_until="load")
    pg.wait_for_function("window.__mermaidDone === true", timeout=1_800_000)
    print("mermaid done in %.0fs, failed=%s" % (time.time() - t, pg.evaluate("window.__mermaidFailed")))
    pg.emulate_media(media="print")
    pg.pdf(path=out, format="A4", print_background=True, outline=True, tagged=True,
           display_header_footer=True,
           header_template="<div></div>",
           footer_template='<div style="font-size:7pt;color:#57606a;width:100%;text-align:center;font-family:DejaVu Sans,sans-serif">Spring Boot 3 &amp; 4 Enterprise Handbook · <span class="pageNumber"></span> / <span class="totalPages"></span></div>',
           margin={"top": "16mm", "bottom": "18mm", "left": "15mm", "right": "15mm"})
    print("pdf in %.0fs" % (time.time() - t))
    b.close()
