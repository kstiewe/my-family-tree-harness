// Szukaj w Archiwach helpers. Run in a tab on www.szukajwarchiwach.gov.pl (same origin for fetch).
// The technique was verified 2026-11 (see szukajwarchiwach.md); these functions package it.
//   swaRotate('<url _max>', x, y, w, h)  // a margin note turned by 90° on a canvas
//
//   await swaScans('<unit id>', 1, 3)      // scans of thumbnail pages 1..3: number → full-resolution URL
//   swaStrip(['<url _max>', …], 300, 700)  // in a tab of photos.szukajwarchiwach.gov.pl: 3–4 scans in one view

window.swaScans = async (unitId, fromPage = 1, toPage = 1) => {
  const out = [];
  for (let page = fromPage; page <= toPage; page++) {
    const url = `/jednostka/-/jednostka/${unitId}?_Jednostka_delta=20&_Jednostka_resetCur=false` +
                `&_Jednostka_cur=${page}&_Jednostka_id_jednostki=${unitId}`;
    const doc = new DOMParser().parseFromString(await (await fetch(url)).text(), 'text/html');
    for (const el of doc.querySelectorAll('.jednostka-skan')) {
      const n = el.querySelector('.number-of-scan')?.innerText.trim();
      const img = el.querySelector('img')?.getAttribute('src') || '';
      out.push(`${n}\t${img.replace(/_mid(\b|$)/, '_max')}`);
    }
  }
  return out.join('\n');
};

// Replace the page with horizontal strips cut from several scans (e.g. the record headers),
// so one screenshot shows several records. `top` = offset of the strip, `height` = strip height.
window.swaStrip = (urls, top = 300, height = 180, width = 1000) => {
  document.body.innerHTML = '';
  document.body.style.margin = '0';
  for (const u of urls) {
    const box = document.createElement('div');
    box.style.cssText = `position:relative;overflow:hidden;width:${width}px;height:${height}px;border-bottom:2px solid red`;
    const img = document.createElement('img');
    img.src = u;
    img.style.cssText = `position:absolute;left:0;top:-${top}px;width:${width}px;max-width:none`;
    box.append(img);
    document.body.append(box);
  }
  return `${urls.length} strips`;
};

// Replace the page with one region of a scan, turned by 90° on a canvas — for notes written along the margin.
// `x, y, w, h` = the region in the image's own pixels (naturalWidth/naturalHeight), `dir` = -1 (counter-clockwise,
// for text running top to bottom) or 1 (clockwise). Find the region first with a scaled view of the whole scan.
window.swaRotate = (url, x, y, w, h, scale = 1.5, dir = -1) => {
  document.body.innerHTML = '';
  const img = new Image();
  img.onload = () => {
    const c = document.createElement('canvas');
    c.width = h * scale;
    c.height = w * scale;
    const g = c.getContext('2d');
    g.translate(dir < 0 ? 0 : c.width, dir < 0 ? c.height : 0);
    g.rotate(dir * Math.PI / 2);
    g.drawImage(img, x, y, w, h, 0, 0, w * scale, h * scale);
    document.body.append(c);
  };
  img.src = url;
  return 'drawing';
};
