/*
 * Step-through animations for the playbook.
 *
 * An animation is plain HTML (see docs/snippets/animations/): an inline <svg> plus one
 * <div class="pb-anim-script" data-scene="..."> per scene, each holding an <ol> of steps.
 * Without JavaScript (or in the PDF) the SVG shows as a static diagram and the steps read as numbered lists.
 * With JavaScript this file turns them into scene tabs, a caption, and play / step controls.
 *
 * Step attributes (all optional, on each <li>):
 *   data-path   comma list of route names to move the token along; "name:rev" runs a route backwards
 *   data-token  "error" paints the token red (an exception travelling back up the stack)
 *   data-hl / data-warn / data-dim   space list of data-node names to highlight / flag / fade
 *   data-tx     space list of "chipName:state" (none, active, suspended, committed, rolledback, ignored)
 * SVG elements with data-scenes="a b" are only shown in those scenes.
 */
(function () {
  "use strict";

  var TX_LABEL = {
    none: "—", active: "ACTIVE", suspended: "SUSPENDED",
    committed: "COMMITTED", rolledback: "ROLLED BACK", ignored: "NEVER STARTED"
  };
  var SEGMENT_MS = 700;
  var DWELL_MS = 2600;

  function words(s) { return (s || "").split(/[\s,]+/).filter(Boolean); }
  function reducedMotion() {
    return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
  }
  function button(cls, label, icon) {
    var b = el("button", "pb-anim-btn " + cls, icon);
    b.type = "button";
    b.setAttribute("aria-label", label);
    b.title = label;
    return b;
  }

  function init(root) {
    var svg = root.querySelector("svg");
    var token = svg && svg.querySelector(".pb-anim-token");
    var scripts = root.querySelectorAll(".pb-anim-script[data-scene]");
    if (!svg || !token || !scripts.length) return;

    var scenes = Array.prototype.map.call(scripts, function (s) {
      var t = s.querySelector(".pb-anim-scene-title");
      return {
        id: s.getAttribute("data-scene"),
        title: t ? t.textContent.trim() : s.getAttribute("data-scene"),
        steps: Array.prototype.slice.call(s.querySelectorAll("li"))
      };
    });
    var state = { scene: 0, step: 0, playing: false, gen: 0, timer: null };

    // ---------- UI ----------
    var ui = el("div", "pb-anim-ui");
    var tabs = el("div", "pb-anim-tabs");
    tabs.setAttribute("role", "group");
    tabs.setAttribute("aria-label", "Scenes");
    var tabButtons = scenes.map(function (sc, i) {
      var b = el("button", "pb-anim-tab", sc.title);
      b.type = "button";
      b.addEventListener("click", function () { stop(); selectScene(i, true); });
      tabs.appendChild(b);
      return b;
    });
    var caption = el("div", "pb-anim-caption");
    caption.setAttribute("aria-live", "polite");
    var bar = el("div", "pb-anim-controls");
    var restart = button("pb-anim-restart", "Restart scene", "↺");
    var prev = button("pb-anim-prev", "Previous step", "‹");
    var play = button("pb-anim-play", "Play", "▶");
    var next = button("pb-anim-next", "Next step", "›");
    var counter = el("span", "pb-anim-counter");
    var hint = el("span", "pb-anim-hint", "← → keys step");
    [restart, prev, play, next, counter, hint].forEach(function (c) { bar.appendChild(c); });
    ui.appendChild(tabs);
    ui.appendChild(caption);
    ui.appendChild(bar);
    root.querySelector(".pb-anim-stage").insertAdjacentElement("afterend", ui);
    root.classList.add("is-enhanced");
    root.tabIndex = -1;

    restart.addEventListener("click", function () { stop(); show(0, true); });
    prev.addEventListener("click", function () { stop(); if (state.step > 0) show(state.step - 1, false); });
    next.addEventListener("click", function () { stop(); advance(); });
    play.addEventListener("click", function () { state.playing ? stop() : start(); });
    root.addEventListener("keydown", function (e) {
      if (e.target.closest && e.target.closest(".pb-anim-tabs")) return;
      if (e.key === "ArrowRight") { e.preventDefault(); stop(); advance(); }
      if (e.key === "ArrowLeft") { e.preventDefault(); stop(); if (state.step > 0) show(state.step - 1, false); }
    });

    // ---------- rendering ----------
    function route(spec) {
      var parts = spec.split(":");
      var path = svg.querySelector('[data-path="' + parts[0] + '"]');
      return path ? { el: path, rev: parts[1] === "rev" } : null;
    }
    function routesOf(li) { return words(li.getAttribute("data-path")).map(route).filter(Boolean); }
    function endPoint(r) { return r.el.getPointAtLength(r.rev ? 0 : r.el.getTotalLength()); }
    function put(p) { token.setAttribute("cx", p.x); token.setAttribute("cy", p.y); }
    function hideToken() { put({ x: -40, y: -40 }); }

    function restingPoint(steps, i) {
      for (var k = i; k >= 0; k--) {
        var rs = routesOf(steps[k]);
        if (rs.length) return endPoint(rs[rs.length - 1]);
      }
      return null;
    }

    function animate(routes, done) {
      var gen = ++state.gen;
      var k = 0;
      function segment() {
        var r = routes[k];
        var len = r.el.getTotalLength();
        var t0 = null;
        function frame(ts) {
          if (gen !== state.gen) return;
          if (t0 === null) t0 = ts;
          var p = Math.min(1, (ts - t0) / SEGMENT_MS);
          var e = p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;
          put(r.el.getPointAtLength((r.rev ? 1 - e : e) * len));
          if (p < 1) requestAnimationFrame(frame);
          else if (++k < routes.length) segment();
          else if (done) done();
        }
        requestAnimationFrame(frame);
      }
      segment();
    }

    function setNodes(attr, cls, li) {
      svg.querySelectorAll("[data-node]." + cls).forEach(function (n) { n.classList.remove(cls); });
      words(li.getAttribute(attr)).forEach(function (name) {
        var n = svg.querySelector('[data-node="' + name + '"]');
        if (n) n.classList.add(cls);
      });
    }

    function show(i, withMotion, done) {
      var sc = scenes[state.scene];
      var li = sc.steps[i];
      state.step = i;
      state.gen++;

      setNodes("data-hl", "is-active", li);
      setNodes("data-warn", "is-warn", li);
      setNodes("data-dim", "is-dim", li);

      words(li.getAttribute("data-tx")).forEach(function (pair) {
        var kv = pair.split(":");
        var chip = svg.querySelector('[data-tx="' + kv[0] + '"]');
        if (!chip) return;
        chip.setAttribute("data-state", kv[1]);
        var status = chip.querySelector("[data-tx-status]");
        if (status) status.textContent = TX_LABEL[kv[1]] || kv[1];
      });

      svg.querySelectorAll("[data-path].is-live").forEach(function (p) { p.classList.remove("is-live"); });
      var routes = routesOf(li);
      routes.forEach(function (r) { r.el.classList.add("is-live"); });
      token.classList.toggle("is-error", li.getAttribute("data-token") === "error");

      caption.textContent = "";
      var num = el("span", "pb-anim-step-num", String(i + 1));
      caption.appendChild(num);
      var body = el("span", "pb-anim-step-text");
      Array.prototype.forEach.call(li.childNodes, function (n) { body.appendChild(n.cloneNode(true)); });
      caption.appendChild(body);

      counter.textContent = "Step " + (i + 1) + " / " + sc.steps.length;
      prev.disabled = i === 0;
      next.disabled = i === sc.steps.length - 1;

      if (routes.length && withMotion && !reducedMotion()) {
        put(routes[0].el.getPointAtLength(routes[0].rev ? routes[0].el.getTotalLength() : 0));
        animate(routes, done);
      } else {
        var rest = restingPoint(sc.steps, i);
        rest ? put(rest) : hideToken();
        if (done) done();
      }
    }

    function selectScene(i, withMotion) {
      state.scene = i;
      var id = scenes[i].id;
      tabButtons.forEach(function (b, k) { b.setAttribute("aria-pressed", String(k === i)); });
      svg.querySelectorAll("[data-scenes]").forEach(function (n) {
        n.style.display = words(n.getAttribute("data-scenes")).indexOf(id) >= 0 ? "" : "none";
      });
      show(0, withMotion);
    }

    function advance() {
      var last = scenes[state.scene].steps.length - 1;
      if (state.step < last) show(state.step + 1, true, schedule);
    }
    function schedule() {
      if (!state.playing) return;
      if (state.step >= scenes[state.scene].steps.length - 1) { stop(); return; }
      state.timer = setTimeout(function () { if (state.playing) advance(); }, DWELL_MS);
    }
    function start() {
      state.playing = true;
      play.textContent = "❚❚";
      play.setAttribute("aria-label", "Pause");
      play.title = "Pause";
      root.classList.add("is-playing");
      if (state.step >= scenes[state.scene].steps.length - 1) show(0, true, schedule);
      else advance();
    }
    function stop() {
      state.playing = false;
      clearTimeout(state.timer);
      play.textContent = "▶";
      play.setAttribute("aria-label", "Play");
      play.title = "Play";
      root.classList.remove("is-playing");
    }

    selectScene(0, false);
  }

  function initAll() {
    document.querySelectorAll("[data-pb-anim]:not(.is-enhanced)").forEach(init);
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(initAll);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAll);
  } else {
    initAll();
  }
})();
