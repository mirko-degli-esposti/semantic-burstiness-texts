#!/usr/bin/env python3
"""
pg_fetch.py — catalogo + download selettivo da Project Gutenberg. Autonomo:
solo libreria standard, nessun clone di pgcorpus/gutenberg richiesto
(strip_headers e le liste di marcatori sono copiate verbatim da src/cleanup.py
di quel repo, a sua volta da c-w/gutenberg / J. Krugel).

Uso (dalla radice del tuo repo, o ovunque: i path sono relativi alla cwd):
  python scripts/pg_fetch.py check 2600 76404 --from data/corpus16_pg.csv
  python scripts/pg_fetch.py catalog                  # solo pg_catalog.csv (~20 MB)
  python scripts/pg_fetch.py search "war and peace" --author tolstoy
  python scripts/pg_fetch.py get --from data/corpus16_pg.csv
  python scripts/pg_fetch.py get 2600 4300

--from accetta un file con un ID per riga oppure un CSV con colonna pg_id.

Output:
  data/pg/raw/PG<id>_raw.txt    testo originale (txt, oppure html->testo)
  data/pg/text/PG<id>_text.txt  senza boilerplate Gutenberg (strip_headers)

Sorgente per ogni ID, in ordine: cache/epub/<id>/pg<id>.txt, files/<id>/<id>-0.txt,
poi cache/epub/<id>/pg<id>-images.html (alcuni ebook recenti, es. 76404, non hanno
la versione plain-text).
"""
import argparse
import csv
import html
import os
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

CATALOG_URL = "https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv"
CATALOG = Path("data/pg/pg_catalog.csv")
RAW_DIR = Path("data/pg/raw")
TEXT_DIR = Path("data/pg/text")
UA = {"User-Agent": "pg_fetch/1.1 (research corpus builder)"}


# ---------------------------------------------------------------------------
# strip_headers — copiato verbatim da pgcorpus/gutenberg src/cleanup.py
# ---------------------------------------------------------------------------
TEXT_START_MARKERS = frozenset((
    "*END*THE SMALL PRINT",
    "*** START OF THE PROJECT GUTENBERG",
    "*** START OF THIS PROJECT GUTENBERG",
    "This etext was prepared by",
    "E-text prepared by",
    "Produced by",
    "Distributed Proofreading Team",
    "Proofreading Team at http://www.pgdp.net",
    "http://gallica.bnf.fr)",
    "      http://archive.org/details/",
    "http://www.pgdp.net",
    "by The Internet Archive)",
    "by The Internet Archive/Canadian Libraries",
    "by The Internet Archive/American Libraries",
    "public domain material from the Internet Archive",
    "Internet Archive)",
    "Internet Archive/Canadian Libraries",
    "Internet Archive/American Libraries",
    "material from the Google Print project",
    "*END THE SMALL PRINT",
    "***START OF THE PROJECT GUTENBERG",
    "This etext was produced by",
    "*** START OF THE COPYRIGHTED",
    "The Project Gutenberg",
    "http://gutenberg.spiegel.de/ erreichbar.",
    "Project Runeberg publishes",
    "Beginning of this Project Gutenberg",
    "Project Gutenberg Online Distributed",
    "Gutenberg Online Distributed",
    "the Project Gutenberg Online Distributed",
    "Project Gutenberg TEI",
    "This eBook was prepared by",
    "http://gutenberg2000.de erreichbar.",
    "This Etext was prepared by",
    "This Project Gutenberg Etext was prepared by",
    "Gutenberg Distributed Proofreaders",
    "Project Gutenberg Distributed Proofreaders",
    "the Project Gutenberg Online Distributed Proofreading Team",
    "**The Project Gutenberg",
    "*SMALL PRINT!",
    "More information about this book is at the top of this file.",
    "tells you about restrictions in how the file may be used.",
    "l'authorization à les utilizer pour preparer ce texte.",
    "of the etext through OCR.",
    "*****These eBooks Were Prepared By Thousands of Volunteers!*****",
    "We need your donations more than ever!",
    " *** START OF THIS PROJECT GUTENBERG",
    "****     SMALL PRINT!",
    '["Small Print" V.',
    '      (http://www.ibiblio.org/gutenberg/',
    'and the Project Gutenberg Online Distributed Proofreading Team',
    'Mary Meehan, and the Project Gutenberg Online Distributed Proofreading',
    '                this Project Gutenberg edition.',
))


TEXT_END_MARKERS = frozenset((
    "*** END OF THE PROJECT GUTENBERG",
    "*** END OF THIS PROJECT GUTENBERG",
    "***END OF THE PROJECT GUTENBERG",
    "End of the Project Gutenberg",
    "End of The Project Gutenberg",
    "Ende dieses Project Gutenberg",
    "by Project Gutenberg",
    "End of Project Gutenberg",
    "End of this Project Gutenberg",
    "Ende dieses Projekt Gutenberg",
    "        ***END OF THE PROJECT GUTENBERG",
    "*** END OF THE COPYRIGHTED",
    "End of this is COPYRIGHTED",
    "Ende dieses Etextes ",
    "Ende dieses Project Gutenber",
    "Ende diese Project Gutenberg",
    "**This is a COPYRIGHTED Project Gutenberg Etext, Details Above**",
    "Fin de Project Gutenberg",
    "The Project Gutenberg Etext of ",
    "Ce document fut presente en lecture",
    "Ce document fut présenté en lecture",
    "More information about this book is at the top of this file.",
    "We need your donations more than ever!",
    "END OF PROJECT GUTENBERG",
    " End of the Project Gutenberg",
    " *** END OF THIS PROJECT GUTENBERG",
))


LEGALESE_START_MARKERS = frozenset(("<<THIS ELECTRONIC VERSION OF",))
LEGALESE_END_MARKERS = frozenset(("SERVICE THAT CHARGES FOR DOWNLOAD",))


def strip_headers(text):
    """
    Remove lines that are part of the Project Gutenberg header or footer.

    Note: this function is a port of the C++ utility by Johannes Krugel. The
    original version of the code can be found at:
    http://www14.in.tum.de/spp1307/src/strip_headers.cpp

    Args:
        text (unicode): The body of the text to clean up.

    Returns:
        unicode: The text with any non-text content removed.

    """
    lines = text.splitlines()
    sep = str(os.linesep)

    out = []
    i = 0
    footer_found = False
    ignore_section = False

    for line in lines:
        reset = False

        if i <= 600:
            # Check if the header ends here
            if any(line.startswith(token) for token in TEXT_START_MARKERS):
                reset = True

            # If it's the end of the header, delete the output produced so far.
            # May be done several times, if multiple lines occur indicating the
            # end of the header
            if reset:
                out = []
                continue

        if i >= 100:
            # Check if the footer begins here
            if any(line.startswith(token) for token in TEXT_END_MARKERS):
                footer_found = True

            # If it's the beginning of the footer, stop output
            if footer_found:
                break

        if any(line.startswith(token) for token in LEGALESE_START_MARKERS):
            ignore_section = True
            continue
        elif any(line.startswith(token) for token in LEGALESE_END_MARKERS):
            ignore_section = False
            continue

        if not ignore_section:
            out.append(line.rstrip(sep))
            i += 1

    return sep.join(out)


# ---------------------------------------------------------------------------
# HTML -> testo (fallback per ebook senza plain-text)
# ---------------------------------------------------------------------------
class _Text(HTMLParser):
    BLOCK = {"p", "div", "br", "h1", "h2", "h3", "h4", "h5", "h6", "li",
             "tr", "table", "pre", "blockquote", "hr", "section"}
    SKIP = {"script", "style", "head", "title"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
        elif tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self._skip -= 1
        elif tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.out.append(data)


def html_to_text(doc):
    p = _Text()
    p.feed(doc)
    txt = "".join(p.out)
    txt = re.sub(r"[ \t\r\f\v]+", " ", txt)
    txt = re.sub(r" *\n *", "\n", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip() + "\n"


# ---------------------------------------------------------------------------
# rete
# ---------------------------------------------------------------------------
def fetch(url, dest=None):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    if dest is not None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    return data


def candidate_urls(pgid):
    return [
        (f"https://www.gutenberg.org/cache/epub/{pgid}/pg{pgid}.txt", "txt"),
        (f"https://www.gutenberg.org/files/{pgid}/{pgid}-0.txt", "txt"),
        (f"https://www.gutenberg.org/cache/epub/{pgid}/pg{pgid}-images.html", "html"),
    ]


def download_text(pgid):
    """Ritorna (testo, url, kind). Prova txt, poi html."""
    last = None
    for url, kind in candidate_urls(pgid):
        try:
            data = fetch(url)
        except urllib.error.HTTPError as e:
            last = e
            continue
        raw = data.decode("utf-8", errors="replace")
        if kind == "html":
            raw = html_to_text(raw)
        return raw, url, kind
    raise RuntimeError(f"PG{pgid}: nessuna URL valida ({last})")


def read_ids(args):
    ids = [str(x).upper().removeprefix("PG") for x in args.ids]
    if args.from_file:
        p = Path(args.from_file)
        txt = p.read_text(encoding="utf-8")
        first = txt.splitlines()[0] if txt else ""
        if "," in first and "pg_id" in first:
            ids += [r["pg_id"].strip() for r in csv.DictReader(txt.splitlines())
                    if r.get("pg_id", "").strip()]
        else:
            ids += [l.strip().upper().removeprefix("PG") for l in txt.splitlines()
                    if l.strip() and not l.startswith("#")]
    return ids


# ---------------------------------------------------------------------------
# comandi
# ---------------------------------------------------------------------------
def cmd_check(args):
    """Solo HEAD sulle URL: dice quale sorgente esiste per ogni ID, senza scaricare."""
    for pgid in read_ids(args):
        found = None
        for url, kind in candidate_urls(pgid):
            req = urllib.request.Request(url, headers=UA, method="HEAD")
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    size = r.headers.get("Content-Length", "?")
                found = (kind, url, size)
                break
            except urllib.error.HTTPError:
                continue
        if found:
            print(f"PG{pgid:>6}: {found[0]:<4} {found[2]:>9} B  {found[1]}")
        else:
            print(f"PG{pgid:>6}: NESSUNA sorgente trovata")
        time.sleep(0.5)


def cmd_catalog(_args):
    print(f"scarico {CATALOG_URL} ...")
    data = fetch(CATALOG_URL, CATALOG)
    n = sum(1 for _ in csv.DictReader(data.decode("utf-8").splitlines()))
    print(f"ok: {CATALOG} ({len(data)/1e6:.1f} MB, {n} record)")


def load_catalog():
    if not CATALOG.exists():
        sys.exit("catalogo assente: lancia prima  pg_fetch.py catalog")
    with CATALOG.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def cmd_search(args):
    rows = load_catalog()
    pats = [re.compile(q, re.I) for q in args.query]
    apat = re.compile(args.author, re.I) if args.author else None
    hits = []
    for r in rows:
        if r["Type"] != "Text":
            continue
        if args.lang and r["Language"] != args.lang:
            continue
        if apat and not apat.search(r["Authors"]):
            continue
        if pats and not any(p.search(r["Title"]) for p in pats):
            continue
        hits.append(r)
    hits.sort(key=lambda r: (r["Authors"], r["Title"]))
    print(f"{len(hits)} risultati (Type=Text, lang={args.lang or 'any'})\n")
    for r in hits:
        title = r["Title"].replace("\n", " | ")
        print(f"PG{r['Text#']:>6}  {r['Language']}  {r['Authors'][:35]:<35}  {title[:80]}")


def cmd_get(args):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    for pgid in read_ids(args):
        raw_p = RAW_DIR / f"PG{pgid}_raw.txt"
        txt_p = TEXT_DIR / f"PG{pgid}_text.txt"
        if raw_p.exists() and not args.overwrite:
            raw, src = raw_p.read_text(encoding="utf-8"), "cache locale"
        else:
            try:
                raw, src, kind = download_text(pgid)
            except RuntimeError as e:
                print(e)
                continue
            raw_p.write_text(raw, encoding="utf-8")
            src = f"{kind}: {src}"
            time.sleep(args.sleep)
        clean = strip_headers(raw)
        txt_p.write_text(clean, encoding="utf-8")
        nw_raw, nw_clean = len(raw.split()), len(clean.split())
        flag = "" if 0.5 < 100*(1-nw_clean/max(nw_raw, 1)) < 15 else "  <-- controllare"
        print(f"PG{pgid:>6}: {nw_raw:>8} -> {nw_clean:>8} parole "
              f"({100*(1-nw_clean/max(nw_raw,1)):.1f}% rimosso)  [{src}]{flag}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_ids(p):
        p.add_argument("ids", nargs="*", help="ID Gutenberg (2600, PG2600, ...)")
        p.add_argument("--from", dest="from_file",
                       help="file con un ID per riga, o CSV con colonna pg_id")

    c = sub.add_parser("check", help="verifica quali URL esistono (HEAD)")
    add_ids(c); c.set_defaults(fn=cmd_check)
    sub.add_parser("catalog", help="scarica pg_catalog.csv").set_defaults(fn=cmd_catalog)
    s = sub.add_parser("search", help="cerca nel catalogo")
    s.add_argument("query", nargs="*", help="regex sul titolo (case-insensitive)")
    s.add_argument("--author", help="regex sul campo Authors")
    s.add_argument("--lang", default="en", help="codice lingua ('' per tutte)")
    s.set_defaults(fn=cmd_search)
    g = sub.add_parser("get", help="scarica e pulisce")
    add_ids(g)
    g.add_argument("--overwrite", action="store_true")
    g.add_argument("--sleep", type=float, default=2.0, help="pausa tra download (s)")
    g.set_defaults(fn=cmd_get)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
