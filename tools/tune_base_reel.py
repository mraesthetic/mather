from pathlib import Path
from collections import defaultdict

BR0_PATH = Path("games/candy_carnage_1000/reels/BR0.csv")
SCATTERS = {"S", "BS"}
PREMIUMS = {"H1", "H2", "H3", "H4"}
MID_LOWS = ["L3", "L4"]
BLOCKER = "PAD"


def load_reel():
    return [line.split(",") for line in BR0_PATH.read_text().strip().splitlines()]


def write_reel(rows):
    BR0_PATH.write_text("\n".join(",".join(r) for r in rows) + "\n")


def insert_blockers(rows, interval=7, offset=2):
    cols = len(rows[0])
    for col in range(cols):
        for r in range(offset, len(rows), interval):
            if rows[r][col] not in SCATTERS:
                rows[r][col] = "L5"


def thin_premium_stacks(rows, run_length=3):
    cols = len(rows[0])
    for col in range(cols):
        streak = 0
        for r in range(len(rows)):
            if rows[r][col] in PREMIUMS:
                streak += 1
                if streak >= run_length:
                    rows[r][col] = MID_LOWS[(r + col) % len(MID_LOWS)]
                    streak = 0
            else:
                streak = 0


def main():
    rows = load_reel()
    insert_blockers(rows, interval=7, offset=2)
    thin_premium_stacks(rows, run_length=2)
    write_reel(rows)


if __name__ == "__main__":
    main()

