from pathlib import Path
import random

REEL_PATH = Path("games/candy_carnage_1000/reels/BR0.csv")

REPLACEMENTS = {
    "H1": "L5",
    "H2": "L5",
    "H3": "L5",
    "H4": "L5",
    "L1": "L5",
    "L2": "L5",
    "L3": "L5",
}


def main():
    rows = [line.split(",") for line in REEL_PATH.read_text().strip().splitlines()]
    for row in rows:
        for idx, sym in enumerate(row):
            row[idx] = REPLACEMENTS.get(sym, sym)
    REEL_PATH.write_text("\n".join(",".join(r) for r in rows) + "\n")


if __name__ == "__main__":
    main()

