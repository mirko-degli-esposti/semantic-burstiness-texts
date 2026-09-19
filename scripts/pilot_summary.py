#!/usr/bin/env python3
"""
pilot_summary.py — riassume results_pilot/corpus_burstiness.csv a un numero per
testo (N, M, alpha, alpha0, B_orig/B_surr medio, B_orig/B_fgn medio) a q=0.95,
unendolo a data/pg/pilot30.csv per titolo/autore/fascia di lunghezza, e stampa
le statistiche per fascia da confrontare col rapporto medio del corpus dei 16
(1.29 +/- 0.03, sd tra testi 0.13, range 1.17-1.39, Principia outlier 1.73).

Uso (dalla radice del repo):
  python scripts/pilot_summary.py
  python scripts/pilot_summary.py --q 0.99 --burst results_pilot/corpus_burstiness.csv
"""
import argparse
import csv
import statistics as st
from collections import defaultdict
from pathlib import Path


def pgid_from_file(fname):
    # "PG1257_text.txt" -> "1257"
    return fname[2:].split("_")[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--burst", default="results_pilot/corpus_burstiness.csv")
    ap.add_argument("--pilot-csv", default="data/pg/pilot30.csv")
    ap.add_argument("--q", type=float, default=0.95)
    ap.add_argument("-o", "--out", default="results_pilot/pilot_summary.csv")
    args = ap.parse_args()

    with open(args.pilot_csv, encoding="utf-8", newline="") as f:
        meta = {r["pg_id"]: r for r in csv.DictReader(f)}

    rows_by_file = defaultdict(list)
    with open(args.burst, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if abs(float(r["q"]) - args.q) < 1e-9:
                rows_by_file[r["file"]].append(r)

    if not rows_by_file:
        raise SystemExit(f"nessuna riga con q={args.q} in {args.burst} "
                          f"(controlla i valori di q realmente presenti)")

    out = []
    for fname, rows in rows_by_file.items():
        pgid = pgid_from_file(fname)
        r0 = rows[0]
        m = meta.get(pgid, {})
        if not m:
            print(f"attenzione: {fname} (pg_id={pgid}) non trovato in {args.pilot_csv}")
        ratios_surr = [float(r["orig_surr"]) for r in rows]
        ratios_fgn = [float(r["orig_fgn"]) for r in rows]
        out.append(dict(
            pg_id=pgid,
            title=m.get("title", ""),
            author=m.get("author", ""),
            length_bucket=m.get("length_bucket", ""),
            N_all=r0["N_all"], N_filt=r0["N_filt"], M=r0["M_filtered"],
            alpha=float(r0["alpha"]), alpha0=float(r0["alpha0"]),
            n_k=len(rows),
            B_orig_surr_mean=round(st.mean(ratios_surr), 4),
            B_orig_surr_sd=round(st.pstdev(ratios_surr), 4) if len(ratios_surr) > 1 else 0.0,
            B_orig_fgn_mean=round(st.mean(ratios_fgn), 4),
        ))

    order = {"short": 0, "medium": 1, "long": 2}
    out.sort(key=lambda r: (order.get(r["length_bucket"], 9), r["title"]))

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    vals = [r["B_orig_surr_mean"] for r in out]
    print(f"q={args.q}  n_testi={len(vals)}")
    print(f"tutto il pilota: media={st.mean(vals):.3f}  sd={st.pstdev(vals):.3f}  "
          f"min={min(vals):.3f}  max={max(vals):.3f}")
    print("(riferimento corpus 16: media 1.29 +/- 0.03, sd tra testi 0.13, range 1.17-1.39)\n")

    for bucket in ["short", "medium", "long"]:
        bv = [r["B_orig_surr_mean"] for r in out if r["length_bucket"] == bucket]
        if bv:
            print(f"  {bucket:<8} n={len(bv):>2}  media={st.mean(bv):.3f}  "
                  f"sd={st.pstdev(bv) if len(bv) > 1 else 0.0:.3f}  "
                  f"min={min(bv):.3f}  max={max(bv):.3f}")

    print(f"\nscritto {args.out}")
    print("\ntesti fuori dal range 1.1-1.5 (outlier candidati, guarda prima questi):")
    for r in out:
        if not (1.1 <= r["B_orig_surr_mean"] <= 1.5):
            print(f"  PG{r['pg_id']:<7} {r['B_orig_surr_mean']:.3f}  {r['title']}")


if __name__ == "__main__":
    main()
