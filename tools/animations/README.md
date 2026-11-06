# Animations

Step-through animations and simulators used in the handbook pages.

| Piece | Where |
|---|---|
| Engine (scene tabs, play/step, tokens, chips) | `docs/javascripts/playbook-animations.js` |
| Interactive simulators (circuit breaker) | `docs/javascripts/playbook-simulators.js` |
| Styles (light/dark, reduced motion) | `docs/stylesheets/playbook-animations.css` |
| Snippets included in pages | `docs/snippets/animations/*.html` (pulled in with `--8<--`) |
| Generator + specs for most snippets | `tools/animations/` (this folder) |

An animation is plain HTML: an inline SVG plus one `<ol>` of steps per scene. Without JavaScript, and in the
PDF, it reads as a static diagram followed by numbered steps. The step attributes are documented at the top of
`playbook-animations.js`.

## Editing a generated animation

Don't hand-edit generated snippets; edit the spec and rebuild:

```bash
python tools/animations/build.py                    # all specs
python tools/animations/build.py backpressure       # one spec
mkdocs build --strict
```

`transactional-proxy.html` and `bean-lifecycle.html` are hand-written and have no spec.

A spec uses `animlib.Anim`: boxes (`box`), routes the token can travel (`route`), toggleable lines (`link`),
status chips (`chip`), scene-only groups (`open(scenes)` / `close()`), then `scene(...)` with steps. Chip
states and `show` sets carry forward between steps, so a step lists only what changes.

## Checking layout

```bash
mkdocs serve
node tools/animations/check.js http://127.0.0.1:8000/part-2-production/21-caching/ stampede
```

It plays every step in light and dark mode and prints `LAYOUT ISSUES` (text outside its box, overlapping text,
chip collisions) and `ERRORS` (JavaScript errors). Both should be empty.
