from brownie import SettV4, Controller, interface, accounts

# Quick test to ensure that migration of test assets and re-use of test contract will work
def main(): 
    vault = SettV4.at("0xD3eC271d07f2f9a4eB5dfD314f84f8a94ba96145")
    ctl = Controller.at("0xe505F7C2FFcce7Ae4b076456BC02A70D8fe8d4d2")
    old_strat = interface.IStrategyConvexStakingOptimizer("0xe66dB6Eb807e6DAE8BD48793E9ad0140a2DEE22A")
    new_strat = interface.IStrategyConvexStakingOptimizer("0x61e16b46F74aEd8f9c2Ec6CB2dCb2258Bdfc7071")


    dev = accounts.at("0xeE8b29AA52dD5fF2559da2C50b1887ADee257556", force=True)
    gov = accounts.at(old_strat.governance(), force=True)

    want = interface.IERC20(vault.token())

    #actions
    print("Total Balance", vault.balance())
    print("Test Vault balance", want.balanceOf(vault.address))
    print("Old newStrat balance", old_strat.balanceOf())
    print("New newStrat balance", new_strat.balanceOf())
    old_strat.setController(ctl.address, {"from":gov })

    ctl.approveStrategy(vault.token(), new_strat.address, {"from": dev})
    ctl.setStrategy(vault.token(), new_strat.address, {"from": dev})
    print("Total Balance", vault.balance())
    print("Test Vault balance", want.balanceOf(vault.address))
    print("Old newStrat balance", old_strat.balanceOf())
    print("New newStrat balance", new_strat.balanceOf())

    vault.earn({"from": dev})
    print("Total Balance", vault.balance())
    print("Test Vault balance", want.balanceOf(vault.address))
    print("Old newStrat balance", old_strat.balanceOf())
    print("New newStrat balance", new_strat.balanceOf())

