BOARD_MULT_INFO = "boardMultiplierInfo"


def send_mult_info_event(gamestate, board_mult: int, mult_info: dict, base_win: float, updatedWin: float):
    multiplier_info = {"positions": []}
    for entry in mult_info:
        multiplier_info["positions"].append(
            {
                "reel": entry["reel"],
                "row": entry["row"] + 1 if gamestate.config.include_padding else entry["row"],
                "multiplier": entry["value"],
                "name": entry.get("name", "M"),
            }
        )

    win_info = {
        "tumbleWin": int(round(min(base_win, gamestate.config.wincap) * 100)),
        "boardMult": board_mult,
        "totalWin": int(round(min(updatedWin, gamestate.config.wincap) * 100)),
    }

    assert round(updatedWin, 1) == round(base_win * board_mult, 1)
    gamestate.book.add_event(
        {
            "index": len(gamestate.book.events),
            "type": BOARD_MULT_INFO,
            "multInfo": multiplier_info,
            "winInfo": win_info,
        }
    )
