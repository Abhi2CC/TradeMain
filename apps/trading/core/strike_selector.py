from math import floor
from config.settings import LOT_SIZES

def select_optimal_strike(available_strikes: list[int], option_type: str, allocated_funds: float, kite, index: str, tradingsymbol_resolver) -> dict | None:
    best = None
    lot_size = LOT_SIZES[index]
    for strike in available_strikes:
        tradingsymbol, token = tradingsymbol_resolver(index, strike, option_type)
        ltp_resp = kite.ltp(f'NFO:{tradingsymbol}')
        ltp = ltp_resp[f'NFO:{tradingsymbol}']['last_price']
        lots = floor(allocated_funds / (ltp * lot_size)) if ltp > 0 else 0
        if lots <= 0:
            continue
        c = {'strike': strike, 'ltp': ltp, 'lots': lots, 'total_cost': lots * ltp * lot_size, 'instrument_token': token, 'tradingsymbol': tradingsymbol}
        if best is None or c['lots'] > best['lots']:
            best = c
    return best
