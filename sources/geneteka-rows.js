// Geneteka results page → text rows with remarks ("Uwagi"), storage info and scan links.
// Paste into the browser's JavaScript console (or an agent's javascript tool) on a results page.
// Built from selectors verified in 2026-11 (see geneteka.md); adjust if the page changes.
(() => {
  const table = document.querySelector('table.tablesearch');
  if (!table) return 'no results table on this page';
  const info = document.querySelector('.dataTables_info')?.innerText || '';
  const rows = [...table.querySelectorAll('tbody tr')].map(row => {
    const cells = [...row.cells].map(c => c.innerText.trim()).filter(Boolean);
    const titles = [...row.querySelectorAll('img[title]')]
      .map(img => img.title.replace(/\s+/g, ' ').trim())
      .filter(t => /^(Uwagi|Miejsce)/.test(t));
    const scan = row.querySelector('img[src*="/s.png"]')?.closest('a')?.href || '';
    return [...cells, ...titles, scan].filter(Boolean).join(' | ');
  });
  return [info, ...rows].join('\n');
})()
