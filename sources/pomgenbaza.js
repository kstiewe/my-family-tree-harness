// PomGenBaza helpers: pgSearch verified 2026-11, pgParishes new (verify). Paste into the JavaScript console on the search page
// https://www.ptg.gda.pl/language/pl/pomgenbaza/przeszukiwanie-rejestrow-metrykalnych/
//
//   await pgSearch('', 'Kowal', 1880, 1912, {motherMaidenName: 'Nowa'})   // children of a couple
//   await pgSearch('Jan', 'Kowal', 1870, 1890, {parish: '<parish id>'})    // one parish
//   pgParishes()                                                            // all parish ids
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
