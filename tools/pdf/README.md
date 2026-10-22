# PDF export

Builds the whole handbook as one PDF (A4, rendered diagrams, bookmarks, page numbers).

```bash
cd tools/pdf
pip install playwright markdown pymdown-extensions pyyaml pygments
python -m playwright install chromium
npm install mermaid            # provides node_modules/mermaid/dist/mermaid.min.js

python build_html.py                                  # -> build/handbook.html
python render.py "$PWD/build/handbook.html" "$PWD/build/handbook.pdf"
qpdf --object-streams=generate --compress-streams=y --recompress-flate \
     build/handbook.pdf build/handbook-compressed.pdf # optional, ~60% smaller
```

- Pages follow the `nav` order in `mkdocs.yml`.
- Collapsible blocks (`???`) are printed expanded; content tabs print every tab with its label.
- Internal links become in-document links; bookmarks come from headings.
- `render.py` reports how many Mermaid diagrams failed to render — keep it at 0 (a failure there also breaks the live site).
