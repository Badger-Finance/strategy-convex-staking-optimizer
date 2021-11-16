from config.badger_config import sett_config

# Assert approximate integer
def approx(actual, expected, percentage_threshold):
    print(actual, expected, percentage_threshold)
    diff = int(abs(actual - expected))
    # 0 diff should automtically be a match
    if diff == 0:
        return True
    return diff < (actual * percentage_threshold // 100)


def val(amount=0, decimals=18, token=None):
    # return amount
    # return "{:,.0f}".format(amount)
    # If no token specified, use decimals
    if token:
        decimals = interface.IERC20(token).decimals()

    return "{:,.18f}".format(amount / 10 ** decimals)

def get_config(strategy_key):
    if strategy_key == "native.renCrv":
        return sett_config.native.convexRenCrv
    if strategy_key == "native.sbtcCrv":
        return sett_config.native.convexSbtcCrv
    if strategy_key == "native.tbtcCrv":
        return sett_config.native.convexTbtcCrv
    if strategy_key == "native.hbtcCrv":
        return sett_config.native.convexHbtcCrv
    if strategy_key == "native.pbtcCrv":
        return sett_config.native.convexPbtcCrv
    if strategy_key == "native.obtcCrv":
        return sett_config.native.convexObtcCrv
    if strategy_key == "native.bbtcCrv":
        return sett_config.native.convexBbtcCrv
    if strategy_key == "native.tricrypto2":
        return sett_config.native.convexTriCryptoDos
    if strategy_key == "native.ibbtcCrv":
        return sett_config.native.convexIbbtcCrv
