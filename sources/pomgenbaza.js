// PomGenBaza helpers: pgSearch and pgQ verified 2026-11, pgParishes verified 2026-11. Paste into the JavaScript console on the search page
// https://www.ptg.gda.pl/language/pl/pomgenbaza/przeszukiwanie-rejestrow-metrykalnych/
//
//   await pgSearch('', 'Kowal', 1880, 1912, {motherMaidenName: 'Nowa'})   // children of a couple
//   await pgSearch('Jan', 'Kowal', 1870, 1890, {parish: '<parish id>'})    // one parish
//   pgParishes()                                                            // all parish ids
//   await pgQ('', 'Kowal', 1905, 1940, {spouseFirstName: 'Teof'}, {types: ['marriages']})  // one tab only
//   await pgQ('', 'Kowal', 1880, 1990, {}, {types: ['deaths'], re: 'Jan|Wzorcowo'})       // filter rows
//
// Every name field matches a prefix. Each tab shows at most 50 rows; the bracket gives the total.

window.pgSearch = async (first, last, from, to, extra = {}) => {
  const f = id => document.getElementById(id);
  f('textInput_firstName').value = first; f('textInput_lastName').value = last;
  f('textInput_yearFrom').value = from; f('textInput_yearTo').value = to;
  const { parish, ...fields } = extra;
  for (const [k, v] of Object.entries({ spouseFirstName: '', spouseLastName: '', fatherFirstName: '',
       motherFirstName: '', motherMaidenName: '', ...fields })) f('textInput_' + k).value = v;
  if (f('selectParish')) f('selectParish').value = parish ?? '0';
  const K = ['births', 'marriages', 'deaths'];
  K.forEach(k => f('divAjaxFindInner_' + k).innerHTML = '');
  document.querySelector('#ptg_search_form input[type=submit]').click();
  for (let i = 0; i < 30; i++) {
    await new Promise(r => setTimeout(r, 500));
    if (K.every(k => f('divAjaxFindInner_' + k).innerText.length > 0)) break;
  }
  await new Promise(r => setTimeout(r, 800));
  return K.map(k => {
    const rows = [...f('divAjaxFindInner_' + k).querySelectorAll('tr')].slice(1)
      .map(r => [...r.cells].map(c => c.innerText.trim()).join(' | '));
    return k.toUpperCase() + ' [' + f('btn_findTab_' + k).value + '] ' + rows.length + ':\n' + rows.join('\n');
  }).join('\n');
};

window.pgParishes = (filter = '') => [...document.querySelectorAll('#selectParish option')]
  .filter(o => o.value !== '0' && o.text.toLowerCase().includes(filter.toLowerCase()))
  .map(o => o.value + '\t' + o.text.trim()).join('\n');

// pgQ: like pgSearch, but returns only the tabs in opt.types and only rows matching opt.re (a regex
// string), at most opt.max rows per tab — keeps the output small. Verified 2026-11.
window.pgQ = async (first, last, from, to, extra = {}, opt = {}) => {
  await window.pgSearch(first, last, from, to, extra);
  const f = id => document.getElementById(id);
  const types = opt.types || ['births', 'marriages', 'deaths'];
  const re = opt.re ? new RegExp(opt.re, 'i') : null;
  return types.map(k => {
    let rows = [...f('divAjaxFindInner_' + k).querySelectorAll('tr')].slice(1)
      .map(r => [...r.cells].map(c => c.innerText.trim()).join('|'));
    const n = rows.length;
    if (re) rows = rows.filter(x => re.test(x));
    return k.toUpperCase() + ' [' + f('btn_findTab_' + k).value + '] shown ' + n + ', matching ' + rows.length + ':\n' +
      rows.slice(0, opt.max || 40).join('\n');
  }).join('\n');
};
