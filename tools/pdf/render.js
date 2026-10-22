window.__mermaidDone = false;
document.querySelectorAll('.tabbed-set').forEach(set => {
  const labels = Array.from(set.querySelectorAll(':scope > .tabbed-labels > label'));
  const blocks = Array.from(set.querySelectorAll(':scope > .tabbed-content > .tabbed-block'));
  blocks.forEach((b, i) => {
    if (labels[i]) { const h = document.createElement('div'); h.className = 'tab-title';
      h.textContent = labels[i].textContent.trim(); b.prepend(h); }
  });
});
mermaid.initialize({ startOnLoad: false, theme: 'neutral', securityLevel: 'loose',
  flowchart: { useMaxWidth: true, htmlLabels: true }, sequence: { useMaxWidth: true } });
(async () => {
  const nodes = Array.from(document.querySelectorAll('pre.mermaid'));
  let failed = 0; window.__mermaidErrors = [];
  for (const n of nodes) {
    const src = n.textContent;
    try { await mermaid.run({ nodes: [n] }); }
    catch (e) { failed++; n.classList.add('mermaid-failed'); n.textContent = src;
      window.__mermaidErrors.push(String(e).slice(0, 200) + ' || ' + src.slice(0, 120)); }
  }
  window.__mermaidFailed = failed; window.__mermaidDone = true;
})();
