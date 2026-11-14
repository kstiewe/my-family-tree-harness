// eCmentarze: graves of a surname as text rows. Run in a tab on www.ecmentarze.pl.
// The parsing rule was verified 2026-11 (see graves.md).
//
//   await ecGraves('Kowalski')          // all given names
//   await ecGraves('Kowalski', 'Jan')

window.ecGraves = async (surname, given = '', maxLen = 300) => {
  const url = `/wyszukaj-pochowanego/szukaj?name=${encodeURIComponent(given)}&surname=${encodeURIComponent(surname)}`;
  const doc = new DOMParser().parseFromString(await (await fetch(url)).text(), 'text/html');
  doc.querySelectorAll('script, ins').forEach(n => n.remove());
  const rows = [];
  for (const a of doc.querySelectorAll('a[href*="grave/detail/"]')) {
    let el = a;   // climb while the parent still contains only this one grave link
    while (el.parentElement && el.parentElement.querySelectorAll('a[href*="grave/detail/"]').length === 1) el = el.parentElement;
    const text = el.innerText.replace(/\s+/g, ' ').trim().slice(0, maxLen);
    if (!rows.some(r => r.startsWith(text))) rows.push(text + ' | ' + a.href);
  }
  return rows.join('\n') || 'no graves found';
};
