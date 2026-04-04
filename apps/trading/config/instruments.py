from datetime import date

def nearest_weekly_options(instruments: list[dict], index: str) -> list[dict]:
    relevant = [i for i in instruments if i.get('segment') == 'NFO-OPT' and i.get('name') == index]
    expiries = sorted({i['expiry'] for i in relevant if i.get('expiry')})
    if not expiries:
        return []
    nearest = expiries[0]
    return [i for i in relevant if i.get('expiry') == nearest]


def build_option_lookup(instruments: list[dict], index: str) -> dict[tuple[int, str], dict]:
    """Build {(strike, option_type): instrument} map for nearest weekly expiry."""
    lookup: dict[tuple[int, str], dict] = {}
    for ins in nearest_weekly_options(instruments, index):
        ts = str(ins.get("tradingsymbol", ""))
        option_type = "CE" if ts.endswith("CE") else ("PE" if ts.endswith("PE") else "")
        if not option_type:
            continue
        strike = int(ins.get("strike", 0))
        lookup[(strike, option_type)] = ins
    return lookup
