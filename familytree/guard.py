"""Privacy guard: stop family data from entering the public repository.

Run from git hooks (.githooks/, installed with `guard.py install`):
  pre-commit   every file in the index (content and path) and the author/committer identity
  commit-msg   the commit message
  pre-push     every commit being pushed: all files of its tree, its message, author and committer
Other commands:
  scan [PATH…] files of the working tree (default: everything git would track)
  audit        list every file that would be published and scan it (exit 1 on any finding)
  check        scan text from stdin — use it before writing anything into the repository
  terms        how many private terms of each kind were loaded (never the terms themselves)

Private terms are built from the workspace at run time and kept in memory only:
  surnames      persons.yaml (surname, married_surnames, surname-like variants), project.yaml surnames
  places        names and aliases from places.yaml, words of project.yaml `regions`
  ids           I/F/P/S ids of the private data, minus ids that the public example data also uses
  dates         full dates (YYYY-MM-DD or DD.MM.YYYY) of events of persons and families
  numbers       numbers of 5+ digits from the data, research notes and INSTRUCTIONS.md (archive unit ids …)
  urls          source URLs with a query or a long number; hosts of online family trees
  block         `block:` entries of <workspace>/privacy.yaml
Phrases listed under `allow:` in privacy.yaml are removed from the text before matching (the
allow list is private too: it would otherwise reveal which public words occur in the family data).

Matching ignores case and Polish diacritics; names and places also match inflected forms
(Kowalski → Kowalskiego, Kowalscy; Wola → Woli) through a stem prefix.

Without a workspace the guard fails closed. Contributors without family data and CI set
FAMILYTREE_GUARD_NO_PRIVATE=1 (or pass --no-private): only the generic checks run — no workspace
files (data/, output/, research/, INSTRUCTIONS.md, privacy.yaml, *.ged) outside examples/ and tests/,
and no Claude artifact links.
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .workspace import APP_ROOT, NOT_FOUND, Workspace, find_workspace

NO_PRIVATE_ENV = "FAMILYTREE_GUARD_NO_PRIVATE"
ZERO = "0" * 40

# Words that occur in place names and region descriptions but identify nothing on their own.
GENERIC_WORDS = set("""
nowy nowa nowe nowo stary stara stare staro wielki wielka wielkie wielko maly mala male malo gorny gorna gorne dolny
dolna dolne wyzszy nizszy srednia sredni polski polska polskie pomorski pomorska pomorskie kujawski kujawska swiety
swieta swiete sw kolonia wies wies parafia parafii gmina gminy gm powiat powiatu pow woj wojewodztwo okolice okolic
miasto osada folwark majatek dwor przedmiescie wybudowanie kosciol koscielny koscielna kat katolicka ewang
ewangelicka usc urzad stanu cywilnego rodzina rodziny linia trop kraj region abbau neu alt gross klein deutsch
polnisch kreis dorf gut vorwerk bei an der die und von zu am im lesne lesna lesny lesnej
""".split())
ADJ_SUFFIXES = ("skiego", "skiej", "skich", "ckiego", "ckiej", "ckich", "dzkiego", "dzkiej", "dzkich",
                "dzki", "dzka", "dzcy", "ski", "ska", "sky", "scy", "cki", "cka", "cky", "ccy")
GENERIC_PATHS = (re.compile(r"^(data|output|research)/"), re.compile(r"(^|/)INSTRUCTIONS\.md$"),
                 re.compile(r"(^|/)privacy\.ya?ml$"), re.compile(r"(^|/)\.workspace$"), re.compile(r"\.ged$", re.I),
                 re.compile(r"(^|/)(persons|families|places|sources)\.ya?ml$"))
PATH_EXEMPT = re.compile(r"^(examples|tests|familytree/skeleton)/")
ARTIFACT_URL = re.compile(r"claude\.ai/(?:code/)?artifacts?/[A-Za-z0-9_-]{6,}", re.I)
TOKEN = re.compile(r"[a-z0-9\u0400-\u04ff]+")      # Latin and Cyrillic letters, after fold()
DATE_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
DATE_PL = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b")


def fold(text: str) -> str:
    text = text.lower().replace("ł", "l")
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def stem(token: str, min_len: int = 4) -> tuple[str, str] | None:
    """('prefix', stem) for inflectable words, ('exact', token) for short ones, None for too short ones."""
    if len(token) < min_len or token.isdigit():
        return None
    if len(token) <= 4:
        return ("exact", token)
    if len(token) == 5:
        return ("prefix", token)
    for suf in ADJ_SUFFIXES:
        if token.endswith(suf) and len(token) - len(suf) >= 5:
            return ("prefix", token[: len(token) - len(suf)])
    if token.endswith(("ek", "ec")) and len(token) - 2 >= 4:
        return ("prefix", token[:-2])
    s = token
    for _ in range(2):
        if s[-1] in "aeiouy" and len(s) > 5:
            s = s[:-1]
    if s[-1] in "kgrtdl" and len(s) >= 7:      # consonant alternations: Przykładówka → w Przykładówce
        s = s[:-1]
    return ("prefix", s)


@dataclass
class Terms:
    prefix: dict[str, set[str]] = field(default_factory=dict)   # stem → kinds
    exact: dict[str, set[str]] = field(default_factory=dict)    # token → kinds
    phrases: dict[str, set[str]] = field(default_factory=dict)  # "token token" → kinds
    raw: dict[str, set[str]] = field(default_factory=dict)      # lower-case substrings (URLs, hosts) → kinds
    dates: set[tuple[int, int, int]] = field(default_factory=set)
    allow_phrases: list[str] = field(default_factory=list)
    allow_raw: list[str] = field(default_factory=list)
    private: bool = True

    def _add(self, table: dict, key: str, kind: str) -> None:
        table.setdefault(key, set()).add(kind)

    def add_word(self, word: str, kind: str, min_len: int = 4) -> None:
        tokens = [t for t in TOKEN.findall(fold(word))]
        if len(tokens) > 1:
            self._add(self.phrases, " ".join(tokens), kind)
        for t in tokens:
            if t in GENERIC_WORDS:
                continue
            s = stem(t, min_len)
            if s:
                self._add(self.prefix if s[0] == "prefix" else self.exact, s[1], kind)

    def stats(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for table in (self.prefix, self.exact, self.phrases, self.raw):
            for kinds in table.values():
                for k in kinds:
                    out[k] = out.get(k, 0) + 1
        out["dates"] = len(self.dates)
        return dict(sorted(out.items()))


def _yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None


def example_ids(repo: Path) -> set[str]:
    """IDs that the public example data uses, up to its next free ID per prefix (I0001 … I0022)."""
    top: dict[str, int] = {}
    for path in repo.glob("examples/*/data/*.yaml"):
        for rec in _yaml(path) or []:
            m = re.fullmatch(r"([IFPS])(\d{4,})", str(rec.get("id", ""))) if isinstance(rec, dict) else None
            if m:
                top[m[1]] = max(top.get(m[1], 0), int(m[2]))
    return {fold(f"{prefix}{n:04d}") for prefix, last in top.items() for n in range(1, last + 2)}


def load_terms(ws: Workspace, repo: Path = APP_ROOT) -> Terms:
    T = Terms()
    persons = _yaml(ws.data / "persons.yaml") or []
    families = _yaml(ws.data / "families.yaml") or []
    places = _yaml(ws.data / "places.yaml") or []
    sources = _yaml(ws.data / "sources.yaml") or []
    project = _yaml(ws.data / "project.yaml") or {}
    given_names = {fold(t) for p in persons if isinstance(p, dict) for t in TOKEN.findall(fold(str(p.get("given") or "")))}

    def surname_like(token: str, surnames: list[str]) -> bool:
        """Variants mix surname spellings with forms of given names (Joannes); keep the surname-like ones."""
        if token in given_names:
            return False
        if re.search(r"[\u0400-\u04ff]", token):           # Cyrillic forms: block, they are rare in public text
            return True
        return any(difflib.SequenceMatcher(None, token, t).ratio() >= 0.6
                   for s in surnames if s for t in TOKEN.findall(fold(s)))

    for p in persons:
        if not isinstance(p, dict):
            continue
        surnames = [p.get("surname") or ""] + list(p.get("married_surnames") or [])
        for s in surnames:
            if s:
                T.add_word(str(s), "surnames", min_len=3)
        for v in p.get("variants") or []:
            for token in TOKEN.findall(fold(str(v))):
                if surname_like(token, surnames):
                    T.add_word(token, "surnames", min_len=3)
        for key in ("birth", "baptism", "death", "burial"):
            _add_date(T, (p.get(key) or {}).get("date") if isinstance(p.get(key), dict) else None)
        for e in p.get("events") or []:
            if isinstance(e, dict):
                _add_date(T, e.get("date"))
    for s in project.get("surnames") or []:
        if isinstance(s, dict):
            for v in [s.get("surname")] + list(s.get("variants") or []):
                if v:
                    T.add_word(str(v), "surnames", min_len=3)
    for r in project.get("regions") or []:
        T.add_word(str(r), "places")
    for f in families:
        if isinstance(f, dict):
            for key in ("marriage", "divorce"):
                if isinstance(f.get(key), dict):
                    _add_date(T, f[key].get("date"))
    for pl in places:
        if isinstance(pl, dict):
            for name in [pl.get("name")] + list(pl.get("aliases") or []):
                if name:
                    T.add_word(str(name), "places")
    skip_ids = example_ids(repo)
    for recs in (persons, families, places, sources):
        for rec in recs:
            if isinstance(rec, dict) and rec.get("id") and fold(str(rec["id"])) not in skip_ids:
                T._add(T.exact, fold(str(rec["id"])), "ids")
    for s in sources:
        if not isinstance(s, dict) or not s.get("url"):
            continue
        url = re.sub(r"^https?://(www\.)?", "", str(s["url"]).strip().lower())
        host, _, rest = url.partition("/")
        if "?" in url or re.search(r"\d{4,}", rest):
            T._add(T.raw, url, "urls")
        if s.get("type") == "online_tree" and host:
            T._add(T.raw, host, "urls")
    texts = [ws.data / f for f in ("persons.yaml", "families.yaml", "places.yaml", "sources.yaml")]
    texts += list(ws.research.glob("*.md")) + [ws.instructions]
    for path in texts:
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for n in re.findall(r"(?<![\d.,])\d{5,}(?![\d])", content):
            T._add(T.exact, n, "numbers")
    priv = _yaml(ws.privacy) or {}
    for b in priv.get("block") or []:
        words = TOKEN.findall(fold(str(b)))
        if len(words) == 1:
            T.add_word(str(b), "block", min_len=3)
        elif words:
            T._add(T.phrases, " ".join(words), "block")
        if re.search(r"[./:@]", str(b)):
            T._add(T.raw, str(b).lower(), "block")
    for a in priv.get("allow") or []:
        T.allow_phrases.append(" ".join(TOKEN.findall(fold(str(a)))))
        T.allow_raw.append(str(a).lower())
    return T


def _add_date(T: Terms, raw) -> None:
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", str(raw or "").strip())
    if m:
        T.dates.add((int(m[1]), int(m[2]), int(m[3])))


@dataclass
class Finding:
    where: str
    line: int
    kind: str
    found: str

    def __str__(self) -> str:
        return f"{self.where}:{self.line}: {self.kind}: {self.found!r}"


def scan_text(T: Terms, text: str, where: str) -> list[Finding]:
    out: list[Finding] = []
    for no, line in enumerate(text.splitlines() or [text], 1):
        for m in ARTIFACT_URL.finditer(line):
            out.append(Finding(where, no, "artifact link", m.group(0)))
        if not T.private:
            continue
        low = line.lower()
        for a in T.allow_raw:
            low = low.replace(a, " ")
        for sub, kinds in T.raw.items():
            if sub in low:
                out.append(Finding(where, no, "/".join(sorted(kinds)), sub))
        folded = fold(line)
        tokens = TOKEN.findall(folded)
        joined = " " + " ".join(tokens) + " "
        for a in T.allow_phrases:
            if a:
                joined = joined.replace(" " + a + " ", " ")
        for ph, kinds in T.phrases.items():
            if " " + ph + " " in joined:
                out.append(Finding(where, no, "/".join(sorted(kinds)), ph))
        for tok in joined.split():
            if tok in T.exact:
                out.append(Finding(where, no, "/".join(sorted(T.exact[tok])), tok))
                continue
            for n in range(min(len(tok), 24), 3, -1):
                kinds = T.prefix.get(tok[:n])
                if kinds:
                    out.append(Finding(where, no, "/".join(sorted(kinds)), tok))
                    break
        for rx, order in ((DATE_ISO, (1, 2, 3)), (DATE_PL, (3, 2, 1))):
            for m in rx.finditer(line):
                try:
                    if tuple(int(m.group(i)) for i in order) in T.dates:
                        out.append(Finding(where, no, "dates", m.group(0)))
                except ValueError:
                    pass
    return out


def scan_path(path: str) -> list[Finding]:
    if PATH_EXEMPT.match(path):
        return []
    return [Finding(path, 0, "workspace file", path) for rx in GENERIC_PATHS if rx.search(path)][:1]


def scan_blob(T: Terms, path: str, data: bytes) -> list[Finding]:
    found = scan_path(path) + scan_text(T, path, f"{path} (file name)")
    return found + scan_text(T, data.decode("utf-8", "replace"), path)


# ------------------------------------------------------------------ git plumbing

REPO = APP_ROOT   # the repository the git commands work on (tests point it elsewhere)


def git(*args: str, input: bytes | None = None) -> bytes:
    return subprocess.run(["git", *args], cwd=REPO, input=input, capture_output=True, check=True).stdout


def blobs(entries: list[tuple[str, str]]) -> dict[str, bytes]:
    """Content of many blobs at once: [(sha, path)] → {sha: bytes}."""
    shas = sorted({sha for sha, _ in entries})
    if not shas:
        return {}
    out = git("cat-file", "--batch", input=("\n".join(shas) + "\n").encode())
    result, pos = {}, 0
    for sha in shas:
        header_end = out.index(b"\n", pos)
        _, _, size = out[pos:header_end].decode().split()
        start = header_end + 1
        result[sha] = out[start:start + int(size)]
        pos = start + int(size) + 1
    return result


def index_entries() -> list[tuple[str, str]]:
    out = []
    for line in git("ls-files", "-s", "-z").decode().split("\0"):
        if line:
            meta, path = line.split("\t", 1)
            out.append((meta.split()[1], path))
    return out


def tree_entries(commit: str) -> list[tuple[str, str]]:
    out = []
    for line in git("ls-tree", "-r", "-z", commit).decode().split("\0"):
        if line:
            meta, path = line.split("\t", 1)
            kind, sha = meta.split()[1:3]
            if kind == "blob":
                out.append((sha, path))
    return out


def ident(var: str) -> str:
    raw = git("var", var).decode().strip()
    return re.sub(r"\s+\d+\s+[+-]\d{4}$", "", raw)


# ------------------------------------------------------------------ commands

def load(args) -> Terms | None:
    if args.no_private or os.environ.get(NO_PRIVATE_ENV) == "1":
        return Terms(private=False)
    ws = find_workspace(args.workspace)
    if not ws:
        print("privacy guard: no workspace, so private terms cannot be checked — blocking.\n" + NOT_FOUND +
              f"\nWithout any family data set {NO_PRIVATE_ENV}=1 to run only the generic checks.", file=sys.stderr)
        return None
    return load_terms(ws)


def report(findings: list[Finding], what: str) -> int:
    if not findings:
        print(f"privacy guard: {what}: clean.", file=sys.stderr)
        return 0
    print(f"privacy guard: {what}: BLOCKED — {len(findings)} finding(s) that look like private family data:", file=sys.stderr)
    for f in findings[:200]:
        print(f"  {f}", file=sys.stderr)
    print("Rephrase with a fictional example, move the content to the private workspace, or — only for a phrase\n"
          "that is generic (e.g. an archive name) — add it to `allow:` in the workspace privacy.yaml.\n"
          "Never bypass this check with --no-verify.", file=sys.stderr)
    return 1


def worktree_files() -> list[str]:
    return [p for p in git("ls-files", "--cached", "--others", "--exclude-standard", "-z").decode().split("\0")
            if p and (REPO / p).is_file()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Privacy guard for the public repository.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--workspace", help="workspace directory (default: the usual search order)")
    ap.add_argument("--no-private", action="store_true", help="generic checks only (no workspace needed)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pre-commit")
    cm = sub.add_parser("commit-msg")
    cm.add_argument("file")
    pp = sub.add_parser("pre-push")
    pp.add_argument("remote", nargs="?")
    pp.add_argument("url", nargs="?")
    sc = sub.add_parser("scan")
    sc.add_argument("paths", nargs="*")
    sub.add_parser("audit")
    sub.add_parser("check")
    sub.add_parser("terms")
    sub.add_parser("install")
    a = ap.parse_args(argv)

    if a.cmd == "install":
        git("config", "core.hooksPath", ".githooks")
        print("Hooks installed: core.hooksPath = .githooks (pre-commit, commit-msg, pre-push).")
        return 0
    T = load(a)
    if T is None:
        return 1
    if a.cmd == "terms":
        print({"private": T.private, **T.stats()})
        return 0
    if a.cmd == "check":
        return report(scan_text(T, sys.stdin.read(), "stdin"), "text")
    if a.cmd == "commit-msg":
        return report(scan_text(T, Path(a.file).read_text(encoding="utf-8", errors="replace"), "commit message"), "commit message")
    if a.cmd == "pre-commit":
        entries = index_entries()
        data = blobs(entries)
        findings = [f for sha, path in entries for f in scan_blob(T, path, data[sha])]
        for var in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"):
            findings += scan_text(T, ident(var), var.lower())
        return report(findings, f"{len(entries)} files in the index")
    if a.cmd == "pre-push":
        findings: list[Finding] = []
        commits: list[str] = []
        for line in sys.stdin.read().splitlines():
            parts = line.split()
            if len(parts) != 4 or parts[1] == ZERO:
                continue
            local, remote = parts[1], parts[3]
            rng = [local, "--not", "--remotes"] if remote == ZERO else [f"{remote}..{local}"]
            commits += git("rev-list", *rng).decode().split()
        seen: set[str] = set()
        for c in dict.fromkeys(commits):
            meta = git("log", "-1", "--format=%an <%ae>%n%cn <%ce>%n%B", c).decode()
            findings += scan_text(T, meta, f"commit {c[:10]}")
            entries = [(sha, p) for sha, p in tree_entries(c) if (sha, p) not in seen]
            seen.update(entries)
            data = blobs(entries)
            findings += [f for sha, path in entries for f in scan_blob(T, path, data[sha])]
        return report(findings, f"{len(set(commits))} commit(s) to push")
    if a.cmd in ("scan", "audit"):
        paths = getattr(a, "paths", None) or worktree_files()
        if a.cmd == "audit":
            print(f"Files that would be published ({len(paths)}):")
            for p in paths:
                print(f"  {p}")
            print({"private_terms": T.private, **T.stats()})
        findings = []
        for p in paths:
            findings += scan_blob(T, p, (REPO / p).read_bytes() if not Path(p).is_absolute() else Path(p).read_bytes())
        return report(findings, f"{len(paths)} files")
    return 2


if __name__ == "__main__":
    sys.exit(main())
