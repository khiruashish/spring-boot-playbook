"""Tiny generator for playbook step-through animation snippets (docs/snippets/animations/*.html).

Output matches the hand-written format the engine (docs/javascripts/playbook-animations.js) reads.
Chip states carry forward between steps of a scene, so a spec only lists what changes.
"""
import html as _h

FILL = {"box": ("#ffffff", "#cbd5e1"), "band": ("#eef2ff", "#6366f1"), "target": ("#f8fafc", "#cbd5e1")}
ROUTE_ATTR = 'fill="none" stroke="#a5b4fc" stroke-width="2.5"'


def esc(s):
    return _h.escape(s, quote=True)


class Anim:
    def __init__(self, key, title_html, svg_title, desc, w, h, top=0):
        self.key, self.title_html, self.svg_title, self.desc, self.w, self.h = key, title_html, svg_title, desc, w, h
        self.top = top  # viewBox y offset: crop empty space above the drawing
        self.parts, self.geo, self.scenes, self.chips = [], {}, [], {}
        self.toggles = []  # nodes shown only when a step's (carried-forward) `show` set includes them

    # ---------- geometry ----------
    def r(self, n, dy=0): x, y, w, h = self.geo[n]; return (x + w, y + h / 2 + dy)
    def l(self, n, dy=0): x, y, w, h = self.geo[n]; return (x, y + h / 2 + dy)
    def t(self, n, dx=0): x, y, w, h = self.geo[n]; return (x + w / 2 + dx, y)
    def b(self, n, dx=0): x, y, w, h = self.geo[n]; return (x + w / 2 + dx, y + h)

    # ---------- shapes ----------
    def raw(self, s):
        self.parts.append(s)

    def open(self, scenes):
        self.parts.append(f'<g data-scenes="{scenes}">')

    def close(self):
        self.parts.append("</g>")

    def text(self, x, y, s, cls="t-sm t-b", anchor=None):
        a = f' text-anchor="{anchor}"' if anchor else ""
        self.parts.append(f'<text class="{cls}" x="{x:g}" y="{y:g}"{a}>{esc(s)}</text>')

    def box(self, node, x, y, w, h, title=None, sub=None, kind="box", mono=False, sub_cls="t-sub",
            sub_mono=False, center=True, rx=10, extra=None, title_cls=""):
        self.geo[node] = (x, y, w, h)
        out = [f'<g data-node="{node}">'] if node else ["<g>"]
        if kind == "shell":
            out.append(f'<rect class="pb-shell" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="16" '
                       f'fill="none" stroke="#818cf8" stroke-dasharray="7 5"/>')
        else:
            cls = {"box": "pb-box", "band": "pb-box pb-band", "target": "pb-box pb-target"}[kind]
            f, s = FILL[kind]
            out.append(f'<rect class="{cls}" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx}" '
                       f'fill="{f}" stroke="{s}"/>')
        lines = []
        if title:
            lines.append((title, "t-b" + (" t-mono" if mono else "") + (" " + title_cls if title_cls else "")))
        if sub:
            for sline in ([sub] if isinstance(sub, str) else sub):
                lines.append((sline, "t-xs " + sub_cls + (" t-mono" if sub_mono else "")))
        if extra:
            lines += extra
        if lines and kind != "shell":
            line_h = [17] + [15] * (len(lines) - 1)
            total = sum(line_h[1:])
            y0 = y + h / 2 - total / 2 + 4.5
            for i, (s, c) in enumerate(lines):
                yy = y0 + sum(line_h[1:i + 1])
                if center:
                    out.append(f'<text class="{c} t-c" x="{x + w / 2:g}" y="{yy:g}">{esc(s)}</text>')
                else:
                    out.append(f'<text class="{c}" x="{x + 14:g}" y="{yy:g}">{esc(s)}</text>')
        elif kind == "shell" and title:
            out.append(f'<text class="t-sm t-b t-accent" x="{x + 14:g}" y="{y + 18:g}">{esc(title)}</text>')
        out.append("</g>")
        self.parts.append("".join(out))
        return node

    def route(self, name, pts=None, d=None, ghost=False, arrow=True):
        if d is None:
            d = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
        cls = "pb-route pb-route--ghost" if ghost else "pb-route"
        dp = f' data-path="{name}"' if name else ""
        mk = f' marker-end="url(#{self.key}-arrow)"' if arrow and not ghost else ""
        stroke = 'fill="none" stroke="#f59e0b" stroke-width="2" stroke-dasharray="5 5"' if ghost else ROUTE_ATTR
        self.parts.append(f'<path class="{cls}"{dp} d="{d}" {stroke}{mk}/>')

    def panel(self, x, y, w, h, title=None):
        self.parts.append(f'<rect class="pb-box" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="14" '
                          f'fill="#f8fafc" stroke="#cbd5e1"/>')
        if title:
            self.text(x + 16, y + 22, title, "t-b")

    def chip(self, name, x, y, w, label, states=None, h=32):
        """states: {state: (LABEL, tone)} — tone is a built-in engine state used for colour."""
        attrs = ""
        for st, (lab, tone) in (states or {}).items():
            attrs += f' data-label-{st}="{esc(lab)}" data-tone-{st}="{tone}"'
        self.chips[name] = True
        self.parts.append(
            f'<g data-tx="{name}" data-state="none"{attrs}><rect class="pb-chip" x="{x:g}" y="{y:g}" width="{w:g}" '
            f'height="{h:g}" rx="{h / 2:g}" fill="#ffffff" stroke="#cbd5e1"/><text class="t-sm" x="{x + 14:g}" '
            f'y="{y + h / 2 + 4.5:g}">{esc(label)}</text><text class="t-b pb-tx-status" data-tx-status '
            f'x="{x + w - 14:g}" y="{y + h / 2 + 4.5:g}" text-anchor="end">—</text></g>')

    def link(self, node, pts=None, d=None):
        """A toggleable line (e.g. a partition assignment), shown only when listed in a step's `show`."""
        self.toggles.append(node)
        if d is None:
            d = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
        self.parts.append(f'<g data-node="{node}"><path class="pb-route pb-link" d="{d}" {ROUTE_ATTR}/></g>')

    # ---------- scenes ----------
    def scene(self, sid, title_html, steps, base=None, show=()):
        self.scenes.append((sid, title_html, steps, dict(base or {}), set(show)))

    def render(self):
        k = self.key
        svg = [f'<svg viewBox="0 {self.top} {self.w} {self.h - self.top}" role="img" aria-labelledby="{k}-title {k}-desc" '
               f'xmlns="http://www.w3.org/2000/svg">',
               f'<title id="{k}-title">{esc(self.svg_title)}</title>',
               f'<desc id="{k}-desc">{esc(self.desc)}</desc>',
               f'<defs><marker id="{k}-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
               f'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#818cf8"/></marker></defs>']
        svg += self.parts
        svg.append('<circle class="pb-anim-token" r="9" cx="-40" cy="-40" fill="#4f46e5" stroke="#ffffff" stroke-width="2.5"/>')
        svg.append("</svg>")
        out = ['<div class="pb-anim" data-pb-anim>',
               f'<div class="pb-anim-head"><span class="pb-anim-kicker">Animated walkthrough</span>'
               f'<span class="pb-anim-title">{self.title_html}</span></div>',
               '<div class="pb-anim-stage">', *svg, "</div>"]
        for sid, title_html, steps, base, show in self.scenes:
            state = {c: "none" for c in self.chips}
            shown = set(show)
            state.update(base)
            out.append(f'<div class="pb-anim-script" data-scene="{sid}">')
            out.append(f'<p class="pb-anim-scene-title"><strong>{title_html}</strong></p>')
            out.append("<ol>")
            for st in steps:
                state.update(st.get("tx", {}))
                if "show" in st:
                    shown = set(st["show"].split())
                st = dict(st)
                hidden = [t for t in self.toggles if t not in shown]
                if hidden:
                    st["hide"] = " ".join(filter(None, [st.get("hide", "")] + hidden))
                a = []
                for key in ("path", "par", "hl", "warn", "dim", "hide", "token"):
                    v = st.get(key)
                    if v:
                        a.append(f'data-{key}="{v}"')
                if self.chips:
                    a.append('data-tx="' + " ".join(f"{c}:{state[c]}" for c in self.chips) + '"')
                out.append(f'<li {" ".join(a)}>{st["text"]}</li>')
            out.append("</ol></div>")
        out.append("</div>")
        return "\n".join(out) + "\n"

    def write(self, path):
        html = self.render()
        assert "\n\n" not in html, "blank line would end the raw HTML block"
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return path
