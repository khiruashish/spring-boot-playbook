// Steps through every scene of every animation on a page (light + dark), reports text that overflows its box,
// overlapping text, chip label collisions and JS errors, and saves screenshots.
//
//   mkdocs serve   (or serve a `mkdocs build` output)
//   node tools/animations/check.js http://127.0.0.1:8000/part-2-production/21-caching/ stampede [animIndex]
//
// Needs Playwright with Chromium. Screenshots go to $SHOTS (default ./animation-shots/).
const { chromium } = require('playwright');
const [url, prefix, idxArg] = process.argv.slice(2);
const OUT = (process.env.SHOTS || 'animation-shots') + '/';
require('fs').mkdirSync(OUT, { recursive: true });

const layoutProbe = (root) => {
  const issues = [];
  const svg = root.querySelector('svg');
  const visible = (el) => { for (let e = el; e && e !== svg; e = e.parentNode) { if (e.style && e.style.display === 'none') return false; } return true; };
  svg.querySelectorAll('[data-node]').forEach(g => {
    if (!visible(g)) return;
    const rect = g.querySelector(':scope > rect'); if (!rect || rect.classList.contains('pb-shell')) return;
    const r = rect.getBBox();
    g.querySelectorAll(':scope > text').forEach(t => {
      const b = t.getBBox();
      if (b.x < r.x - 1 || b.x + b.width > r.x + r.width + 1 || b.y < r.y - 1 || b.y + b.height > r.y + r.height + 1)
        issues.push(`text "${t.textContent}" overflows node ${g.dataset.node}`);
    });
  });
  const texts = [...svg.querySelectorAll('text')].filter(t => visible(t) && !t.closest('.is-hidden') && t.textContent.trim());
  for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++) {
    const p = texts[i].getBBox(), q = texts[j].getBBox();
    if (p.x < q.x + q.width - 1 && q.x < p.x + p.width - 1 && p.y < q.y + q.height - 2 && q.y < p.y + p.height - 2)
      issues.push(`text "${texts[i].textContent}" overlaps "${texts[j].textContent}"`);
  }
  svg.querySelectorAll('[data-tx]').forEach(g => {
    if (!visible(g)) return;
    const ts = g.querySelectorAll('text'); const r = g.querySelector('rect').getBBox();
    const a = ts[0].getBBox(), s = ts[1].getBBox();
    if (a.x + a.width + 6 > s.x) issues.push(`chip ${g.dataset.tx}: status "${ts[1].textContent}" collides with label`);
    if (s.x + s.width > r.x + r.width) issues.push(`chip ${g.dataset.tx}: status overflows`);
  });
  return issues;
};

(async () => {
  const b = await chromium.launch(); const errs = []; const issues = new Set();
  for (const scheme of ['light', 'dark']) {
    const p = await b.newPage({ viewport: { width: 1280, height: 900 }, colorScheme: scheme });
    p.on('pageerror', e => errs.push(scheme + ': ' + e.message));
    p.on('console', m => { if (m.type() === 'error' && !/ERR_TUNNEL|rate limit|404|Failed to load resource/.test(m.text())) errs.push(m.text()); });
    await p.goto(url);
    const anims = p.locator('.pb-anim');
    const n = await anims.count();
    const idxs = idxArg !== undefined ? [Number(idxArg)] : [...Array(n).keys()];
    for (const ai of idxs) {
      const a = anims.nth(ai); await a.scrollIntoViewIfNeeded();
      const tabs = a.locator('.pb-anim-tab'); const tc = await tabs.count();
      for (let t = 0; t < tc; t++) {
        await tabs.nth(t).click(); await p.waitForTimeout(300); let s = 0;
        while (true) {
          await p.waitForTimeout(2300);
          (await a.evaluate(layoutProbe)).forEach(i => issues.add(i));
          if (scheme === 'light') {
            const st = await a.evaluate(e => e.querySelector('.pb-anim-counter').textContent + ' | ' +
              [...e.querySelectorAll('svg [data-tx]')].filter(x => x.closest('[data-scenes]') === null || x.closest('[data-scenes]').style.display !== 'none').map(x => x.dataset.tx + '=' + x.querySelector('[data-tx-status]').textContent).join(' '));
            console.log(`a${ai} s${t}`, st);
            await a.screenshot({ path: `${OUT}${prefix}-a${ai}-s${t}-${s}.png` });
          } else if (s === 1) await a.screenshot({ path: `${OUT}${prefix}-dark-a${ai}-s${t}.png` });
          const nx = a.locator('.pb-anim-next'); if (await nx.isDisabled()) break;
          await nx.click(); s++;
        }
      }
    }
    await p.close();
  }
  const m = await b.newPage({ viewport: { width: 390, height: 844 } });
  await m.goto(url);
  console.log('mobile scrollWidth', await m.evaluate(() => document.documentElement.scrollWidth));
  console.log('LAYOUT ISSUES', [...issues]);
  console.log('ERRORS', errs);
  await b.close();
})();
