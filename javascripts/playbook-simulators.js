/*
 * Interactive simulators for the playbook (live, unlike the step-through animations).
 *
 * <div class="pb-anim pb-sim" data-pb-sim="circuit-breaker"> … static fallback … </div>
 * Without JavaScript (and in the PDF) only the fallback text shows.
 */
(function () {
  "use strict";

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function button(label, cls) {
    var b = el("button", "pb-anim-btn pb-sim-btn " + (cls || ""), label);
    b.type = "button";
    return b;
  }
  function slider(label, min, max, step, value, suffix) {
    var wrap = el("label", "pb-sim-slider");
    var head = el("span", "pb-sim-slider-head");
    var name = el("span", "", label);
    var out = el("strong", "", value + suffix);
    head.appendChild(name);
    head.appendChild(out);
    var input = el("input");
    input.type = "range";
    input.min = min; input.max = max; input.step = step; input.value = value;
    input.addEventListener("input", function () { out.textContent = input.value + suffix; });
    wrap.appendChild(head);
    wrap.appendChild(input);
    return { wrap: wrap, input: input };
  }

  // ---------------------------------------------------------------------------------------------
  // Circuit breaker (Resilience4j semantics, count-based window, scaled down to watch in seconds)
  // ---------------------------------------------------------------------------------------------
  var CB = { window: 10, minCalls: 5, waitMs: 5000, permitted: 3, trafficMs: 380 };

  function circuitBreaker(root) {
    var s = {
      state: "CLOSED", outcomes: [], trial: [], openedAt: 0,
      reached: 0, rejected: 0, failed: 0, traffic: null, tick: null
    };

    var ui = el("div", "pb-sim-ui");
    var states = el("div", "pb-sim-states");
    states.setAttribute("aria-live", "polite");
    var pills = {};
    ["CLOSED", "OPEN", "HALF_OPEN"].forEach(function (name) {
      pills[name] = el("span", "pb-sim-state", name);
      states.appendChild(pills[name]);
    });

    var winBox = el("div", "pb-sim-panel");
    var winHead = el("div", "pb-sim-panel-head");
    var winTitle = el("span", "", "Sliding window · last " + CB.window + " calls");
    var winRate = el("strong", "pb-sim-rate", "");
    winHead.appendChild(winTitle);
    winHead.appendChild(winRate);
    var cells = el("div", "pb-sim-cells");
    var cellEls = [];
    for (var i = 0; i < CB.window; i++) { var c = el("span", "pb-sim-cell"); cells.appendChild(c); cellEls.push(c); }
    var phase = el("div", "pb-sim-phase");
    var bar = el("div", "pb-sim-bar");
    var barFill = el("span", "");
    bar.appendChild(barFill);
    winBox.appendChild(winHead);
    winBox.appendChild(cells);
    winBox.appendChild(phase);
    winBox.appendChild(bar);

    var stats = el("div", "pb-sim-stats");
    var stReached = el("span", ""), stRejected = el("span", ""), stFailed = el("span", "");
    [stReached, stFailed, stRejected].forEach(function (x) { stats.appendChild(x); });

    var controls = el("div", "pb-sim-controls");
    var dep = slider("Dependency failure rate", 0, 100, 10, 0, "%");
    var thr = slider("failureRateThreshold", 20, 80, 10, 50, "%");
    controls.appendChild(dep.wrap);
    controls.appendChild(thr.wrap);
    var buttons = el("div", "pb-sim-buttons");
    var one = button("Send 1 call");
    var ten = button("Send 10 calls");
    var traffic = button("▶ Start traffic", "pb-sim-primary");
    var down = button("Dependency goes down");
    var up = button("Dependency recovers");
    var reset = button("↺ Reset");
    [traffic, one, ten, down, up, reset].forEach(function (b) { buttons.appendChild(b); });

    var log = el("ol", "pb-sim-log");
    log.setAttribute("aria-live", "polite");
    log.setAttribute("aria-label", "State transitions");

    ui.appendChild(states);
    ui.appendChild(winBox);
    ui.appendChild(stats);
    ui.appendChild(controls);
    ui.appendChild(buttons);
    ui.appendChild(log);
    root.appendChild(ui);
    root.classList.add("is-enhanced");

    function rate(list) {
      if (!list.length) return 0;
      return Math.round(100 * list.filter(Boolean).length / list.length);
    }
    function note(text, kind) {
      var li = el("li", kind ? "is-" + kind : "", text);
      log.insertBefore(li, log.firstChild);
      while (log.children.length > 6) log.removeChild(log.lastChild);
    }
    function go(next, why) {
      note(s.state + " → " + next + ": " + why, next === "OPEN" ? "bad" : next === "CLOSED" ? "good" : "warn");
      s.state = next;
      s.outcomes = [];          // Resilience4j resets the metrics on every state transition
      s.trial = [];
      if (next === "OPEN") s.openedAt = Date.now();
    }

    function call() {
      var failPct = Number(dep.input.value), threshold = Number(thr.input.value);
      if (s.state === "OPEN" || (s.state === "HALF_OPEN" && s.trial.length >= CB.permitted)) {
        s.rejected++;            // CallNotPermittedException → fallback, no call made
        render();
        return;
      }
      var failed = Math.random() * 100 < failPct;
      s.reached++;
      if (failed) s.failed++;
      if (s.state === "CLOSED") {
        s.outcomes.push(failed);
        if (s.outcomes.length > CB.window) s.outcomes.shift();
        if (s.outcomes.length >= CB.minCalls && rate(s.outcomes) >= threshold) {
          go("OPEN", "failure rate " + rate(s.outcomes) + "% ≥ " + threshold + "%");
        }
      } else {
        s.trial.push(failed);
        if (s.trial.length === CB.permitted) {
          var r = rate(s.trial);
          if (r >= threshold) go("OPEN", "trial failure rate " + r + "% ≥ " + threshold + "%");
          else go("CLOSED", "trial failure rate " + r + "% < " + threshold + "%");
        }
      }
      render();
    }

    function render() {
      Object.keys(pills).forEach(function (k) { pills[k].classList.toggle("is-current", k === s.state); });
      root.setAttribute("data-cb-state", s.state);
      var list = s.state === "HALF_OPEN" ? s.trial : s.outcomes;
      var size = s.state === "HALF_OPEN" ? CB.permitted : CB.window;
      cellEls.forEach(function (c, k) {
        c.hidden = k >= size;
        c.className = "pb-sim-cell" + (k < list.length ? (list[k] ? " is-fail" : " is-ok") : "");
        c.textContent = k < list.length ? (list[k] ? "✗" : "✓") : "";
      });
      if (s.state === "CLOSED") {
        winTitle.textContent = "Sliding window · last " + CB.window + " calls";
        winRate.textContent = s.outcomes.length < CB.minCalls
          ? "needs " + CB.minCalls + " calls to judge (" + s.outcomes.length + " so far)"
          : "failure rate " + rate(s.outcomes) + "%";
        phase.textContent = "Calls pass through and are recorded. Opens when the failure rate reaches the threshold.";
      } else if (s.state === "OPEN") {
        winTitle.textContent = "OPEN · calls fail fast";
        winRate.textContent = "";
        phase.textContent = "Every call throws CallNotPermittedException in microseconds and goes to the fallback. The dependency gets room to recover.";
      } else {
        winTitle.textContent = "HALF_OPEN · " + CB.permitted + " trial calls";
        winRate.textContent = s.trial.length ? "trial failure rate " + rate(s.trial) + "%" : "";
        phase.textContent = "Only " + CB.permitted + " calls are let through. Their failure rate decides: below the threshold closes, at or above reopens.";
      }
      var left = s.state === "OPEN" ? Math.max(0, CB.waitMs - (Date.now() - s.openedAt)) : 0;
      bar.hidden = s.state !== "OPEN";
      barFill.style.width = (100 * (1 - left / CB.waitMs)) + "%";
      stReached.textContent = "Reached dependency: " + s.reached;
      stFailed.textContent = "Failed there: " + s.failed;
      stRejected.textContent = "Failed fast (fallback): " + s.rejected;
    }

    function setTraffic(on) {
      if (on && !s.traffic) s.traffic = setInterval(call, CB.trafficMs);
      if (!on && s.traffic) { clearInterval(s.traffic); s.traffic = null; }
      traffic.textContent = s.traffic ? "❚❚ Stop traffic" : "▶ Start traffic";
    }
    function setDep(v) { dep.input.value = v; dep.input.dispatchEvent(new Event("input")); }

    traffic.addEventListener("click", function () { setTraffic(!s.traffic); });
    one.addEventListener("click", call);
    ten.addEventListener("click", function () { for (var k = 0; k < 10; k++) call(); });
    down.addEventListener("click", function () { setDep(100); setTraffic(true); });
    up.addEventListener("click", function () { setDep(0); setTraffic(true); });
    reset.addEventListener("click", function () {
      setTraffic(false);
      s.state = "CLOSED"; s.outcomes = []; s.trial = []; s.reached = s.rejected = s.failed = 0;
      log.textContent = "";
      render();
    });

    // automaticTransitionFromOpenToHalfOpenEnabled: true
    s.tick = setInterval(function () {
      if (s.state === "OPEN" && Date.now() - s.openedAt >= CB.waitMs) go("HALF_OPEN", "waitDurationInOpenState elapsed");
      if (s.state === "OPEN" || !bar.hidden) render();
    }, 100);

    render();
  }

  var SIMS = { "circuit-breaker": circuitBreaker };

  function initAll() {
    document.querySelectorAll("[data-pb-sim]:not(.is-enhanced)").forEach(function (root) {
      var fn = SIMS[root.getAttribute("data-pb-sim")];
      if (fn) fn(root);
    });
  }
  if (window.document$ && typeof window.document$.subscribe === "function") window.document$.subscribe(initAll);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initAll);
  else initAll();
})();
