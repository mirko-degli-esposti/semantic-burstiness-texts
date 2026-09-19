#!/usr/bin/env python3
"""
pg_select.py — candidati da pg_catalog.csv "coerenti" col corpus del paper.

Il CSV di PG non ha un conteggio download; il proxy di canonicità qui usato è
la presenza di almeno una "bookshelf" EDITORIALE (le vecchie liste curate a
mano, es. "Harvard Classics", "Best Books Ever Listings", "Banned Books"),
distinta dalle etichette "Category: ..." che sono auto-generate dai Subjects
e presenti su quasi ogni libro (non indicano qualità/canonicità).

Due passi:
  1) `shelves`  — tabula le bookshelf editoriali realmente presenti nel TUO
     catalogo (frequenze), per scegliere a occhio quali contano come "canone".
  2) `select`   — il filtro vero e proprio, con --require-curated-shelf e/o
     --shelf "nome parziale" (una o più; basta che una combaci).

Filtri di `select` (tutti modificabili da riga di comando):
  - Language == en, Type == Text
  - LoCC in una lista di classi (default: PR PS PQ PG PT Q B)
  - autore nato tra --born-min e --born-max (default 1750-1900)
  - titolo NON contiene parole da raccolta/apparato (Works, Volume, Poems, ...)
  - --require-curated-shelf: almeno una bookshelf non "Category: ..."
  - --shelf NOME [NOME ...]: almeno una bookshelf editoriale contiene NOME
    (case-insensitive, sottostringa); implica --require-curated-shelf
  - una sola voce per (autore, titolo normalizzato): tiene l'ID più basso
  - poi HEAD su pg<id>.txt: Content-Length -> parole stimate (bytes/5.9);
    tiene solo >= --min-words (default 55000)

Uso (dalla radice del repo, dopo `pg_fetch.py catalog`):
  python scripts/pg_select.py shelves --top 80
  python scripts/pg_select.py shelves --subject fiction --top 80   # stessi filtri di select

  python scripts/pg_select.py select --require-curated-shelf --max 300 \\
      -o data/pg/candidates_canon.csv
  python scripts/pg_select.py select --shelf "Harvard Classics" "Best Books Ever" \\
      -o data/pg/candidates_canon2.csv
  python scripts/pg_select.py select --author dickens --no-head   # solo filtro catalogo

Output CSV: pg_id,title,author,born,died,locc,subjects,curated_shelves,bytes,words_est
"""
import argparse
import csv
import random
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

CATALOG = Path("data/pg/pg_catalog.csv")
UA = {"User-Agent": "pg_select/1.1 (research corpus builder)"}
BYTES_PER_WORD = 5.9  # stima empirica sui 16 testi del corpus (5.7-6.1)

EXCLUDE_TITLE = re.compile(
    r"\b(works|volume|vol\.|poems|poetry|verse|letters|correspondence|plays|"
    r"drama|stories|tales|sketches|essays|index|selections?|anthology|"
    r"collection|reader|dictionary|encyclop|speeches|sermons|diary|journal|"
    r"memoirs?|magazine|review|part\s+[ivx\d]+|book\s+[ivx\d]+|chapters?)\b",
    re.I)

EXCLUDE_SUBJECT = re.compile(
    r"(juvenile|children|poetry|drama|short stories|periodicals|dictionar|"
    r"readers|textbooks|cookbooks|hymns|songs|comics)", re.I)


def norm_title(t):
    t = t.split("\n")[0].split(":")[0].split(";")[0]
    t = re.sub(r"[^a-z0-9 ]", " ", t.lower())
    t = re.sub(r"^(the|a|an)\s+", "", t)
    return re.sub(r"\s+", " ", t).strip()


def author_years(a):
    """'Dickens, Charles, 1812-1870; Illustrator, X' -> (1812, 1870) del primo autore."""
    first = a.split(";")[0]
    m = re.search(r"(\d{4})\??-(\d{4})?", first)
    if not m:
        return None, None
    return int(m.group(1)), (int(m.group(2)) if m.group(2) else None)


def locc_matches(locc_field, prefixes):
    """Un prefisso di 1 lettera (es. 'B', 'Q') deve corrispondere ESATTAMENTE
    al codice LoCC, altrimenti 'B' riammetterebbe anche 'BR','BX',... (religione)
    per via del semplice startswith. Un prefisso di 2+ lettere (es. 'BC','QH')
    continua a fare match per prefisso, com'era prima."""
    codes = [c.strip() for c in locc_field.split(";") if c.strip()]
    for c in codes:
        for p in prefixes:
            if (c == p) if len(p) == 1 else c.startswith(p):
                return True
    return False


def curated_shelves(raw):
    """Bookshelves non auto-generate: tutte tranne quelle che iniziano con 'Category:'."""
    tags = [t.strip() for t in raw.split(";") if t.strip()]
    return [t for t in tags if not t.lower().startswith("category:")]


def head_size(pgid):
    url = f"https://www.gutenberg.org/cache/epub/{pgid}/pg{pgid}.txt"
    req = urllib.request.Request(url, headers=UA, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return int(r.headers.get("Content-Length", 0))
    except (urllib.error.HTTPError, urllib.error.URLError):
        return 0


def load_catalog():
    if not CATALOG.exists():
        sys.exit("catalogo assente: lancia prima  python scripts/pg_fetch.py catalog")
    with CATALOG.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def base_filter(rows, args):
    """Filtri di catalogo comuni a `shelves` e `select` (lingua, tipo, LoCC, subject,
    autore, anni, titolo/subject da escludere). Non tocca ancora canonicità/dedup."""
    subj = re.compile(args.subject, re.I) if args.subject else None
    apat = re.compile(args.author, re.I) if args.author else None
    out = []
    for r in rows:
        if r["Type"] != "Text" or r["Language"] != "en":
            continue
        if args.locc and not locc_matches(r["LoCC"], args.locc):
            continue
        if subj and not subj.search(r["Subjects"]):
            continue
        if apat and not apat.search(r["Authors"]):
            continue
        if EXCLUDE_TITLE.search(r["Title"]) or EXCLUDE_SUBJECT.search(r["Subjects"]):
            continue
        born, died = author_years(r["Authors"])
        if args.born_min is not None and (born is None or born < args.born_min):
            continue
        if args.born_max is not None and (born is None or born > args.born_max):
            continue
        out.append(r)
    return out


def add_common_args(p):
    p.add_argument("--locc", nargs="*", default=["PR", "PS", "PQ", "PG", "PT", "Q", "B"],
                   help="classi LoCC ammesse (prefisso)")
    p.add_argument("--subject", help="regex che Subjects deve contenere (es. fiction)")
    p.add_argument("--author", help="regex su Authors")
    p.add_argument("--born-min", type=int, default=1750)
    p.add_argument("--born-max", type=int, default=1900)


def cmd_shelves(args):
    rows = base_filter(load_catalog(), args)
    cnt = Counter()
    for r in rows:
        cnt.update(curated_shelves(r["Bookshelves"]))
    tot_with_any = sum(1 for r in rows if curated_shelves(r["Bookshelves"]))
    print(f"{len(rows)} libri dopo i filtri di catalogo; "
          f"{tot_with_any} ({100*tot_with_any/max(len(rows),1):.1f}%) hanno "
          f"almeno una bookshelf editoriale\n", file=sys.stderr)
    for name, n in cnt.most_common(args.top):
        print(f"{n:>6}  {name}")


def cmd_select(args):
    rows = base_filter(load_catalog(), args)
    require_curated = args.require_curated_shelf or bool(args.shelf)
    shelf_pats = [re.compile(re.escape(s), re.I) for s in (args.shelf or [])]

    seen, cand = {}, []
    for r in rows:
        cur = curated_shelves(r["Bookshelves"])
        if require_curated and not cur:
            continue
        if shelf_pats and not any(p.search(s) for s in cur for p in shelf_pats):
            continue
        born, died = author_years(r["Authors"])
        key = (r["Authors"].split(";")[0].split(",")[0].lower(), norm_title(r["Title"]))
        pgid = int(r["Text#"])
        if key in seen and seen[key] <= pgid:
            continue
        seen[key] = pgid
        cand.append(dict(pg_id=pgid, title=r["Title"].replace("\n", " | "), _key=key,
                         author=r["Authors"].split(";")[0], born=born, died=died,
                         locc=r["LoCC"], subjects=r["Subjects"],
                         curated_shelves="; ".join(cur)))
    # rimuovi le edizioni duplicate rimaste con id più alto (stessa chiave di quando
    # è stata costruita: NON ricalcolarla da un titolo già trasformato altrove)
    cand = [c for c in cand if seen[c["_key"]] == c["pg_id"]]
    for c in cand:
        del c["_key"]
    cand.sort(key=lambda c: (c["author"], c["title"]))
    print(f"{len(cand)} candidati dopo i filtri (canonicità: "
          f"{'richiesta' if require_curated else 'non richiesta'})", file=sys.stderr)
    if args.max_per_author:
        per_author = Counter()
        capped = []
        for c in cand:
            if per_author[c["author"]] >= args.max_per_author:
                continue
            per_author[c["author"]] += 1
            capped.append(c)
        print(f"{len(cand) - len(capped)} rimossi da --max-per-author {args.max_per_author} "
              f"({len(cand)} -> {len(capped)})", file=sys.stderr)
        cand = capped
    if len(cand) > args.max:
        print(f"troppi: taglio ai primi {args.max} (ordine autore/titolo); "
              f"restringi con --subject/--locc/--author/--shelf", file=sys.stderr)
        cand = cand[:args.max]

    out = []
    for i, c in enumerate(cand, 1):
        if args.no_head:
            c["bytes"], c["words_est"] = "", ""
        else:
            b = head_size(c["pg_id"])
            c["bytes"], c["words_est"] = b, int(b / BYTES_PER_WORD)
            time.sleep(args.sleep)
            if c["words_est"] < args.min_words:
                continue
        out.append(c)
        print(f"[{i}/{len(cand)}] PG{c['pg_id']:>6} {c['words_est']!s:>7}  "
              f"{c['author'][:30]:<30} {c['title'][:60]}", file=sys.stderr)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["pg_id", "title", "author", "born", "died", "locc",
                                          "subjects", "curated_shelves", "bytes", "words_est"])
        w.writeheader()
        w.writerows(out)
    print(f"\n{len(out)} candidati scritti in {args.out}", file=sys.stderr)


def bucket_label(w, edges):
    for i in range(len(edges) - 1):
        if edges[i] <= w < edges[i + 1]:
            return i
    return len(edges) - 2


def cmd_sample(args):
    with open(args.input, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    exclude = set(args.exclude_ids or [])
    if args.exclude_csv:
        with open(args.exclude_csv, encoding="utf-8", newline="") as f:
            exclude |= {r["pg_id"].strip() for r in csv.DictReader(f) if r.get("pg_id", "").strip()}
    before = len(rows)
    rows = [r for r in rows if r["pg_id"].strip() not in exclude]
    print(f"{before - len(rows)} esclusi perché già nel corpus indicato da --exclude-csv/--exclude-ids "
          f"({before} -> {len(rows)})", file=sys.stderr)

    edges = args.edges
    names = args.bucket_names or [f"bucket{i}" for i in range(len(edges) - 1)]
    if len(names) != len(edges) - 1:
        sys.exit(f"--bucket-names deve avere {len(edges)-1} nomi per {len(edges)-1} fasce")
    buckets = [[] for _ in range(len(edges) - 1)]
    skipped_oor = 0
    for r in rows:
        w = int(r["words_est"]) if r.get("words_est") else None
        if w is None or w < edges[0] or w >= edges[-1]:
            skipped_oor += 1
            continue
        buckets[bucket_label(w, edges)].append(r)
    if skipped_oor:
        print(f"{skipped_oor} fuori dal range coperto da --edges (ignorati)", file=sys.stderr)

    rnd = random.Random(args.seed)
    for b in buckets:
        rnd.shuffle(b)

    n_buckets = len(buckets)
    per_bucket = args.n // n_buckets
    remainder = args.n - per_bucket * n_buckets
    quotas = [per_bucket + (1 if i < remainder else 0) for i in range(n_buckets)]

    chosen, used_authors = [], set()
    for bi, b in enumerate(buckets):
        picked = 0
        for r in b:
            if picked >= quotas[bi]:
                break
            if r["author"] in used_authors:
                continue
            used_authors.add(r["author"])
            r["length_bucket"] = names[bi]
            chosen.append(r)
            picked += 1
        if picked < quotas[bi]:
            print(f"  attenzione: fascia '{names[bi]}' ha solo {picked}/{quotas[bi]} "
                  f"candidati con autore non ripetuto", file=sys.stderr)

    if len(chosen) < args.n:
        pool = [r for b in buckets for r in b
                if r["author"] not in used_authors]
        rnd.shuffle(pool)
        for r in pool:
            if len(chosen) >= args.n:
                break
            used_authors.add(r["author"])
            r.setdefault("length_bucket", names[bucket_label(int(r["words_est"]), edges)])
            chosen.append(r)

    if len(chosen) < args.n:
        print(f"solo {len(chosen)}/{args.n} trovati (pool esaurito): allarga --edges o --n-", file=sys.stderr)

    cnt = Counter(c["length_bucket"] for c in chosen)
    print(f"\ncampione: {len(chosen)} testi, {len(used_authors)} autori distinti, seed={args.seed}",
          file=sys.stderr)
    for name in names:
        print(f"  {name:<10} {cnt.get(name, 0)}", file=sys.stderr)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(chosen[0].keys()) if chosen else \
        ["pg_id", "title", "author", "born", "died", "locc", "subjects",
         "curated_shelves", "bytes", "words_est", "length_bucket"]
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(chosen)
    print(f"scritto {args.out}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("shelves", help="tabula le bookshelf editoriali reali del catalogo")
    add_common_args(s)
    s.add_argument("--top", type=int, default=60)
    s.set_defaults(fn=cmd_shelves)

    g = sub.add_parser("select", help="filtra i candidati")
    add_common_args(g)
    g.add_argument("--require-curated-shelf", action="store_true",
                   help="tieni solo libri con >=1 bookshelf editoriale (non 'Category: ...')")
    g.add_argument("--shelf", nargs="*",
                   help="tieni solo libri con una bookshelf editoriale che contiene una di queste stringhe")
    g.add_argument("--max-per-author", type=int, default=None,
                   help="limita quante opere dello stesso autore tenere (ordine alfabetico di titolo)")
    g.add_argument("--min-words", type=int, default=55000)
    g.add_argument("--max", type=int, default=500, help="max candidati su cui fare HEAD")
    g.add_argument("--no-head", action="store_true", help="salta le HEAD (niente lunghezze)")
    g.add_argument("--sleep", type=float, default=0.3)
    g.add_argument("-o", "--out", default="data/pg/candidates.csv")
    g.set_defaults(fn=cmd_select)

    p = sub.add_parser("sample", help="campione stratificato per un giro pilota")
    p.add_argument("--input", default="data/pg/candidates.csv", help="csv prodotto da 'select'")
    p.add_argument("--exclude-csv", help="csv con colonna pg_id da escludere (es. il tuo corpus16_pg.csv)")
    p.add_argument("--exclude-ids", nargs="*", help="altri pg_id da escludere a mano")
    p.add_argument("-n", type=int, default=30)
    p.add_argument("--edges", nargs="*", type=float, default=[55000, 90000, 180000, 10**7],
                   help="bordi delle fasce di lunghezza in parole, es. 55000 90000 180000 10000000")
    p.add_argument("--bucket-names", nargs="*", default=["short", "medium", "long"])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("-o", "--out", default="data/pg/pilot30.csv")
    p.set_defaults(fn=cmd_sample)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
