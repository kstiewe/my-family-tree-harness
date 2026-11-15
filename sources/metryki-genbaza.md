# Metryki GenBaza

[metryki.genbaza.pl](https://metryki.genbaza.pl), now served as `genbaza.pl/metryki/…` (Fundacja Cyfrowa Genealogia): photos
of parish books and civil registers from Polish state archives, among them many from the former German eastern provinces,
taken by volunteers. It is an alternative to [Szukaj w Archiwach](szukajwarchiwach.md) with a different coverage: offices
and years that have no scans there are often here. Not the same as [Metryki](https://metryki.genealodzy.pl) (scans of
books, open without a login). (Checked 2026-11.)

## Access: the user signs in, the agent only reads

- Viewing the photos needs a free account, and the entrance shows a Cloudflare check with a box to tick. The agent never
  ticks the box and never types the user's login or password.
- In a browser the agent runs on its own, the check may not pass even when the user ticks the box: the page stays on
  "Przeprowadzanie weryfikacji zabezpieczeń". Do not try to work around it.
- What works best, when the user asks for it: the user's own browser, already signed in, driven through a browser
  extension the user has connected (e.g. Claude in Chrome). There the pages open without the check. The agent opens the
  folder and the photo in a tab of its own, reads them in the site's photo viewer and closes the tab at the end. Only
  reading: no downloads without asking, no changes to the account, one record at a time. A check, a login form or a 403
  page means: stop and tell the user.
- Without that, the user opens the photo and saves it (or a sharp screenshot of the record) into the workspace (e.g. a
  `research/scans/` folder, the file named after the photo number), or pastes it into the chat; the agent reads the image
  from there, transcribes it and records the file name in the source's `notes`.
- Read every photo of a record in one go: a marriage record usually takes two.
- The duplicate registers ("Neben-Register") often have no name index — only the cover, the title page and the records.
  Use the complete year list from PomGenBaza instead (see [pomgenbaza.md](pomgenbaza.md)).

## Finding a book and a photo

- Old links `https://metryki.genbaza.pl/genbaza,list,<folder id>,1` redirect to
  `https://genbaza.pl/metryki/<code>/<archive>/<fonds>`. The fonds page lists the book folders as `NNNN_<year>_<type>` with
  the number of photos (e.g. `0012_1880_sl 16`): `NNNN` is the unit, i.e. the last part of the archive signature; the
  type is `ur` (births), `sl` (marriages), `zg` (deaths), `_ind` (name indexes). Each book folder has its own address.
- The quickest way to the folder of a fonds is GenWiki: the pages whose titles start with "Metryki.GenBaza/" list, per
  archive and kind of record, every office or parish with a "Link" to its folder (the parent page "Metryki.GenBaza" lists
  the archives). Fonds folders are titled "<office>_<fonds number>", e.g. "Przykładowo_1234".
- A PomGenBaza "Nr zdjęcia" such as `10_1234_0_56_0007` reads: archive 10, fonds 1234, series 0, unit 56, photo 0007.
  Open the book folder `0056_…`; photo 0007 is number 8 in the viewer (the viewer counts from 1, the photos from 0000).
  Photo file names may carry the year (`…_0007_1888.JPG`).
- **Every book folder of a fonds at once**: in the signed-in tab, `fetch` the fonds page and read its links with
  `DOMParser` (`a[href*="/<fonds slug>/0"]`): one request gives the address code of each folder. Keep the codes of the
  family's offices in the workspace — they spare a page view per book later.
- In many civil registry fonds the units run year by year as births, marriages, deaths (unit = first unit + 3 × years
  since the first year, + 1 for marriages, + 2 for deaths), so the unit of another year can be predicted. A year with an
  extra book breaks the pattern: check against the folder list.

## Reading a photo

- The viewer address is `<book folder>/<number>#zoom=<z>&x=<x>&y=<y>`: x and y are the centre of the view as fractions
  of the photo (0–1). Zoom 0.5 shows a whole double page; 1.2–1.3 makes the handwriting readable in a window about 1500 px
  wide. Change the hash to move over the page and take region screenshots.
- Thumbnails are IIIF images (`…/full/!400,400/0/default.jpg`); larger sizes requested directly answer 403. Use the
  site's viewer, not a workaround.
- Record the viewer address (book folder and number) in the source's `url` and the photo number in `notes`.
