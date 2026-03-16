import csv
from collections import Counter, defaultdict
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "bischemer_lexikon_master.csv"


def load_dictionary(path=DATA_PATH):
    pairs = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hd = row["hochdeutsch"].strip().lower()
            bi = row["bischemerisch"].strip().lower()
            if hd and bi:
                pairs.append((hd, bi))
    return pairs


def all_substrings(word, min_len=1, max_len=4):
    result = set()
    n = len(word)
    for length in range(min_len, max_len + 1):
        for i in range(n - length + 1):
            result.add((word[i:i + length], i, i + length))
    return result


def collect_candidate_rules(pairs, min_src_len=1, max_src_len=4, min_dst_len=0, max_dst_len=4):
    """
    Sucht nach Quellmustern im hochdeutschen Wort und schaut,
    welche Zielmuster im bischemerischen Wort statistisch häufig
    in denselben Wortpaaren auftauchen.
    """
    src_to_dst_counter = Counter()
    src_counter = Counter()
    examples = defaultdict(list)

    for hd, bi in pairs:
        hd_subs = all_substrings(hd, min_src_len, max_src_len)
        bi_subs = all_substrings(bi, max(1, min_dst_len), max_dst_len)

        # Leere Zielsequenzen zusätzlich erlauben, um Tilgungen wie "en -> ''" darzustellen
        bi_strings = {s for s, _, _ in bi_subs}
        bi_strings.add("")

        for src, _, _ in hd_subs:
            src_counter[src] += 1

            # Für dieses Wortpaar sammeln wir alle vorkommenden Ziel-Teilsequenzen
            # plus leere Sequenz als Option für Tilgung
            for dst in bi_strings:
                if len(dst) < min_dst_len or len(dst) > max_dst_len:
                    continue
                src_to_dst_counter[(src, dst)] += 1
                if len(examples[(src, dst)]) < 5:
                    examples[(src, dst)].append((hd, bi))

    return src_counter, src_to_dst_counter, examples


def score_rules(src_counter, src_to_dst_counter, examples, min_support=8, min_confidence=0.18):
    """
    Confidence = Anteil der Vorkommen eines Quellmusters, in denen das Zielmuster
    im entsprechenden Dialektwort ebenfalls vorkommt.
    """
    rules = []

    for (src, dst), support in src_to_dst_counter.items():
        total = src_counter[src]
        if total == 0:
            continue

        confidence = support / total

        # uninteressante Identität rausfiltern
        if src == dst:
            continue

        # triviale Ein-Zeichen-Regeln mit zu schwacher Basis vermeiden
        if support < min_support:
            continue

        if confidence < min_confidence:
            continue

        rules.append({
            "src": src,
            "dst": dst,
            "support": support,
            "total_src_occurrences": total,
            "confidence": round(confidence, 4),
            "examples": examples[(src, dst)],
        })

    # bevorzugt längere Muster, dann hohe confidence, dann hohe Unterstützung
    rules.sort(
        key=lambda r: (
            len(r["src"]),
            len(r["dst"]),
            r["confidence"],
            r["support"],
        ),
        reverse=True,
    )
    return rules


def deduplicate_rules(rules):
    """
    Reduziert redundante Regeln.
    Beispiel: Wenn 'ei -> aa' stark ist, soll 'e -> a' nicht alles überfluten.
    """
    selected = []
    seen = set()

    for rule in rules:
        key = (rule["src"], rule["dst"])
        if key in seen:
            continue

        # harte Heuristik gegen sehr redundante kurze Regeln
        redundant = False
        for s in selected:
            if (
                rule["src"] in s["src"]
                and rule["dst"] in s["dst"]
                and len(s["src"]) >= len(rule["src"])
                and s["confidence"] >= rule["confidence"]
            ):
                redundant = True
                break

        if not redundant:
            selected.append(rule)
            seen.add(key)

    return selected


def save_rules_csv(rules, out_path):
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "src",
            "dst",
            "support",
            "total_src_occurrences",
            "confidence",
            "examples",
        ])
        for r in rules:
            ex = " | ".join(f"{hd}->{bi}" for hd, bi in r["examples"])
            writer.writerow([
                r["src"],
                r["dst"],
                r["support"],
                r["total_src_occurrences"],
                r["confidence"],
                ex,
            ])


def save_rules_markdown(rules, out_path, top_n=150):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Automatisch erkannte Büschemerisch-Regeln\n\n")
        f.write("Diese Regeln wurden statistisch aus den Wortpaaren abgeleitet.\n\n")

        for idx, r in enumerate(rules[:top_n], start=1):
            f.write(f"## Regel {idx}: `{r['src']} → {r['dst']}`\n\n")
            f.write(f"- Support: {r['support']}\n")
            f.write(f"- Confidence: {r['confidence']}\n")
            if r["examples"]:
                f.write("- Beispiele:\n")
                for hd, bi in r["examples"]:
                    f.write(f"  - `{hd}` → `{bi}`\n")
            f.write("\n")


def mine_rules():
    pairs = load_dictionary()
    src_counter, src_to_dst_counter, examples = collect_candidate_rules(pairs)
    rules = score_rules(src_counter, src_to_dst_counter, examples)
    rules = deduplicate_rules(rules)
    return rules


if __name__ == "__main__":
    output_dir = Path(__file__).resolve().parent.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    rules = mine_rules()

    csv_path = output_dir / "phonetic_rules.csv"
    md_path = output_dir / "dialect_rules.md"

    save_rules_csv(rules, csv_path)
    save_rules_markdown(rules, md_path)

    print(f"{len(rules)} Regeln gespeichert.")
    print(f"CSV: {csv_path}")
    print(f"Markdown: {md_path}")

    for r in rules[:30]:
        print(r["src"], "->", r["dst"], "| support:", r["support"], "| conf:", r["confidence"])
