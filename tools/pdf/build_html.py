"""Combine the MkDocs handbook into one print-ready HTML file (nav order)."""
import html
import os
import re
import sys

import markdown
import yaml
from pygments.formatters import HtmlFormatter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DOCS = os.path.join(ROOT, "docs")
OUT = os.path.join(HERE, "build", "handbook.html")
MERMAID_JS = os.environ.get("MERMAID_JS", os.path.join(HERE, "node_modules", "mermaid", "dist", "mermaid.min.js"))


class Loader(yaml.SafeLoader):
    pass


Loader.add_multi_constructor("tag:yaml.org,2002:python/name:", lambda l, s, n: None)


def nav_files():
    cfg = yaml.load(open(os.path.join(ROOT, "mkdocs.yml")), Loader=Loader)
    out = []

    def walk(item, section=None):
        if isinstance(item, str):
            out.append((section, item))
        elif isinstance(item, dict):
            for k, v in item.items():
                if isinstance(v, str):
                    out.append((section, v))
                else:
                    for x in v:
                        walk(x, k)
        elif isinstance(item, list):
            for x in item:
                walk(x, section)

    walk(cfg["nav"])
    seen, ordered = set(), []
    for sec, f in out:
        if f not in seen and os.path.exists(os.path.join(DOCS, f)):
            seen.add(f)
            ordered.append((sec, f))
    return ordered


def doc_id(path):
    return "d-" + re.sub(r"[^a-z0-9]+", "-", path.lower().replace(".md", "")).strip("-")


def make_md():
    return markdown.Markdown(
        extensions=[
            "abbr", "admonition", "attr_list", "def_list", "footnotes", "md_in_html", "tables", "toc",
            "pymdownx.details", "pymdownx.inlinehilite", "pymdownx.keys", "pymdownx.mark",
            "pymdownx.caret", "pymdownx.tilde", "pymdownx.highlight", "pymdownx.superfences",
            "pymdownx.tabbed", "pymdownx.tasklist", "pymdownx.emoji",
        ],
        extension_configs={
            "pymdownx.highlight": {"use_pygments": True, "noclasses": False, "css_class": "highlight"},
            "pymdownx.superfences": {"custom_fences": [
                {"name": "mermaid", "class": "mermaid",
                 "format": lambda src, lang, css, opts, md, **kw: f'<pre class="mermaid">{html.escape(src)}</pre>'}
            ]},
            "pymdownx.tabbed": {"alternate_style": True},
        },
    )


def preprocess(text):
    # Expand collapsible blocks for print: ??? / ???+ -> !!!
    text = re.sub(r"^(\s*)\?\?\?\+?(\s)", r"\1!!!\2", text, flags=re.M)
    # Material icon shortcodes in footers -> arrows
    text = text.replace(":material-arrow-left:", "←").replace(":material-arrow-right:", "→")
    text = re.sub(r":material-[a-z0-9-]+:", "", text)
    return text


def rewrite(html_text, path, ids):
    did = ids[path]
    base_dir = os.path.dirname(path)

    # prefix element ids within the document
    html_text = re.sub(r'id="([^"]+)"', lambda m: f'id="{did}--{m.group(1)}"', html_text)

    def fix_href(m):
        href = m.group(1)
        if href.startswith(("http://", "https://", "mailto:")):
            return m.group(0)
        if href.startswith("#"):
            return f'href="#{did}--{href[1:]}"'
        target, _, frag = href.partition("#")
        if target.endswith(".md"):
            tpath = os.path.normpath(os.path.join(base_dir, target))
            if tpath in ids:
                return f'href="#{ids[tpath]}--{frag}"' if frag else f'href="#{ids[tpath]}"'
        return 'href="#"'

    return re.sub(r'href="([^"]*)"', fix_href, html_text)


def main():
    files = nav_files()
    ids = {f: doc_id(f) for _, f in files}
    parts, toc_rows, last_sec = [], [], None
    for sec, f in files:
        raw = open(os.path.join(DOCS, f), encoding="utf-8").read()
        md = make_md()
        body = rewrite(md.convert(preprocess(raw)), f, ids)
        title_m = re.search(r"^# (.+)$", raw, flags=re.M)
        title = title_m.group(1).strip() if title_m else f
        if sec != last_sec:
            toc_rows.append(f'<li class="toc-sec">{html.escape(sec or "")}</li>')
            parts.append(f'<section class="part-divider"><h1 class="part-title">{html.escape(sec or "")}</h1></section>')
            last_sec = sec
        toc_rows.append(f'<li><a href="#{ids[f]}">{html.escape(title)}</a></li>')
        parts.append(f'<section class="doc" id="{ids[f]}">{body}</section>')

    pyg = HtmlFormatter(style="friendly").get_style_defs(".highlight")
    css = open(os.path.join(HERE, "print.css")).read()
    mermaid = open(MERMAID_JS, encoding="utf-8").read()
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Spring Boot 3 &amp; 4 Enterprise Handbook</title>
<style>{pyg}</style><style>{css}</style></head><body>
<section class="cover">
  <div class="cover-inner">
    <div class="kicker">Enterprise Handbook</div>
    <h1 class="cover-title">Spring Boot 3 &amp; 4</h1>
    <p class="cover-sub">From first bean to platform architecture — beginner to 15+ years,<br>
    grounded in a multi-vendor grocery marketplace.</p>
    <p class="cover-meta">44 chapters · 8 appendices · 341 interview questions</p>
  </div>
</section>
<section class="toc"><h1 class="toc-title">Contents</h1><ol class="toc-list">{''.join(toc_rows)}</ol></section>
{''.join(parts)}
""" + "<script>" + mermaid + "</script><script>" + open(os.path.join(HERE, "render.js")).read() + "</script></body></html>"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(page)
    print("docs:", len(files), "bytes:", len(page))


if __name__ == "__main__":
    main()
