BOARD_MULT_INFO = "boardMultiplierInfo"


def send_mult_info_event(gamestate, board_mult: int, mult_info: dict, base_win: float, updatedWin: float):
    multiplier_info, winInfo = {}, {}
    multiplier_info["positions"] = []
    for m in range(len(mult_info)):
        position_payload = {
            "reel": mult_info[m]["reel"],
            "row": mult_info[m]["row"] + 1 if gamestate.config.include_padding else mult_info[m]["row"],
            "multiplier": mult_info[m]["value"],
            "name": mult_info[m].get("name", "M"),
        }
        multiplier_info["positions"].append(position_payload)

    winInfo["tumbleWin"] = int(round(min(base_win, gamestate.config.wincap) * 100))
    winInfo["boardMult"] = board_mult
    winInfo["totalWin"] = int(round(min(updatedWin, gamestate.config.wincap) * 100))

    assert round(updatedWin, 1) == round(base_win * board_mult, 1)
    event = {
        "index": len(gamestate.book.events),
        "type": BOARD_MULT_INFO,
        "multInfo": multiplier_info,
        "winInfo": winInfo,
    }
    gamestate.book.add_event(event)
