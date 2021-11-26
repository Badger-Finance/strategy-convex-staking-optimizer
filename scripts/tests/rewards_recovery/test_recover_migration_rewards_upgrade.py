import brownie
import pytest
import json
from brownie import (
    accounts,
    interface,
    chain,
    Wei,
    SettV4,
    Controller,
    RewardsRecoveryStrategy_distribution,
)
from config.badger_config import badger_config
from rich.console import Console


##### Variables to tweak ######

# V1.1
# new_logic = "0x0bB87f40D4eb6066a2311B7BE3B45A3D15771557"

# V1.2
# new_logic = "0xe73e74Fab5e1cfE7545421D7DC63da42fC62b0d3"

# V1.3
# new_logic = "0x424D836778309A88B7Dc46fa48e41d658Db270eb"

###############################


console = Console()

STRAT_KEYS = [
    "native.renCrv",
    "native.sbtcCrv",
    "native.tbtcCrv",
    "native.hbtcCrv",
    "native.pbtcCrv",
    "native.obtcCrv",
    "native.bbtcCrv",
    "native.tricrypto2",
]

OLD_STRATEGIES = {
    "native.renCrv": "0x6582a5b139fc1c6360846efdc4440d51aad4df7b",
    "native.sbtcCrv": "0xf1ded284e891943b3e9c657d7fc376b86164ffc2",
    "native.tbtcCrv": "0x522bb024c339a12be1a47229546f288c40b62d29",
    "native.hbtcCrv": "0xff26f400e57bf726822eacbb64fa1c52f1f27988",
    "native.pbtcCrv": "0x1C1fD689103bbFD701b3B7D41A3807F12814033D",
    "native.obtcCrv": "0x2bb864cdb4856ab2d148c5ca52dd7ccec126d138",
    "native.bbtcCrv": "0x4f3e7a4566320b2709fd1986f2e9f84053d3e2a0",
    "native.tricrypto2": "0x2eB6479c2f033360C0F4575A88e3b8909Cbc6a03",
}

new_logic = "0x0bB87f40D4eb6066a2311B7BE3B45A3D15771557"


@pytest.fixture()
def badger_deploy():
    with open(badger_config.prod_json) as f:
        return json.load(f)


@pytest.fixture()
def deployer(badger_deploy):
    return accounts.at(badger_deploy["deployer"], force=True)


@pytest.fixture()
def guardian(badger_deploy):
    return accounts.at(badger_deploy["guardian"], force=True)

@pytest.fixture()
def keeper():
    return accounts.at("0x711A339c002386f9db409cA55b6A35a604aB6cF6", force=True)


@pytest.fixture()
def governance_multi(badger_deploy):
    return accounts.at(badger_deploy["devMultisig"], force=True)


@pytest.fixture()
def timelock(badger_deploy):
    return accounts.at(badger_deploy["timelock"], force=True)


@pytest.fixture()
def devProxyAdmin(badger_deploy):
    return interface.IProxyAdmin(badger_deploy["devProxyAdmin"]) 


@pytest.fixture()
def bcvxCrv():
    return SettV4.at("0x2B5455aac8d64C14786c3a29858E43b5945819C0")


@pytest.fixture()
def bCvx():
    return SettV4.at("0x53c8e199eb2cb7c01543c137078a038937a68e40")

@pytest.fixture()
def bveCVX():
    return SettV4.at("0xfd05D3C7fe2924020620A8bE4961bBaA747e6305")

@pytest.fixture()
def cvxCrv():
    return interface.IERC20("0x62b9c7356a2dc64a1969e19c23e4f579f9810aa7")  

@pytest.fixture()
def cvx():
    return interface.IERC20("0x4e3fbd56cd56c3e72c1403e103b45db9da5b9d2b")  

@pytest.fixture()
def crv():
    return interface.IERC20("0xd533a949740bb3306d119cc777fa900ba034cd52") 



@pytest.fixture()
def exp_controller(badger_deploy):
    return Controller.at(badger_deploy["sett_system"]["controllers"]["experimental"])


@pytest.fixture()
def native_controller(badger_deploy):
    return Controller.at(badger_deploy["sett_system"]["controllers"]["native"])


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@pytest.mark.parametrize(
    "strategy_key",
    STRAT_KEYS,
)
def test_migrate_staking_optimizer(
    strategy_key,
    keeper,
    governance_multi,
    bcvxCrv,
    bCvx,
    bveCVX,
    cvx,
    cvxCrv,
    crv,
    timelock,
    devProxyAdmin,
    deployer,
):

    console.print(f"[yellow]Processing {strategy_key}...[/yellow]")

    # Get current strategy
    strategy = interface.IStrategyConvexStakingOptimizer(OLD_STRATEGIES[strategy_key])
    # Get want
    want = interface.IERC20(strategy.want())

    # Get reward pools
    baseRewardsPool = interface.IBaseRewardsPool(strategy.baseRewardsPool())
    cvxCrvRewardsPool = interface.IBaseRewardsPool(strategy.cvxCrvRewardsPool())
    cvxRewardsPool = interface.IBaseRewardsPool(strategy.cvxRewardsPool())

    badgerTree = strategy.badgerTree()

    console.print(f"[blue]Old Strategy: [/blue]{strategy.address}")
    console.print(f"[blue]Want: [/blue]{want.address}")
    console.print("baseRewardsPool earned:", baseRewardsPool.earned(strategy.address))
    console.print("cvxCrvRewardsPool earned:", cvxCrvRewardsPool.earned(strategy.address))
    console.print("cvxRewardsPool earned:", cvxRewardsPool.earned(strategy.address))
    console.print("strategy.balanceOf():", strategy.balanceOf())

    # Harvest should revert due to lack of rewards on cvx and cvxCrv reward pools
    with brownie.reverts("RewardPool : Cannot withdraw 0"):
        strategy.harvest({"from": keeper})

    # Deploy new logic
    new_logic = RewardsRecoveryStrategy_distribution.deploy({"from": deployer})

    # Upgrade logic
    devProxyAdmin.upgrade(strategy.address, new_logic, {"from": timelock})

    assert strategy.keeper() == keeper.address
    assert strategy.governance() == governance_multi.address
    assert strategy.cvxHelperVault() == bCvx.address
    assert strategy.cvxCrvHelperVault() == bcvxCrv.address
    assert strategy.crv() == crv.address
    assert strategy.cvx() == cvx.address
    assert strategy.cvxCrv() == cvxCrv.address
    assert strategy.badgerTree() == badgerTree
    assert strategy.performanceFeeGovernance() == 1000
    assert strategy.performanceFeeStrategist() == 0
    assert strategy.performanceFeeStrategist() == 0

    # New logic removed auto compounding completely - Set performance fee to 20%
    strategy.setPerformanceFeeGovernance(2000, {"from": governance_multi})
    assert strategy.performanceFeeGovernance() == 2000

    tree_bcvx_before = bCvx.balanceOf(badgerTree)
    tree_bcvxCrv_before = bcvxCrv.balanceOf(badgerTree)
    tree_bveCVX_before = bveCVX.balanceOf(badgerTree)
    strat_bcvx_before = bCvx.balanceOf(strategy.address)
    strat_bcvxCrv_before = bcvxCrv.balanceOf(strategy.address)
    strat_bveCVX_before = bveCVX.balanceOf(strategy.address)
    strat_cvx_before = cvx.balanceOf(strategy.address)
    strat_cvxCrv_before = cvxCrv.balanceOf(strategy.address)
    strat_crv_before = crv.balanceOf(strategy.address)
    strat_want_before = want.balanceOf(strategy.address)
    postion_before = strategy.balanceOf()

    gov_bcvx_before = bCvx.balanceOf(governance_multi)
    gov_bcvxCrv_before = bcvxCrv.balanceOf(governance_multi)
    gov_bveCVX_before = bveCVX.balanceOf(governance_multi)
    gov_want_before = want.balanceOf(governance_multi)

    strategy.harvest({"from": keeper})

    tree_bcvx_after = bCvx.balanceOf(badgerTree)
    tree_bcvxCrv_after = bcvxCrv.balanceOf(badgerTree)
    tree_bveCVX_after= bveCVX.balanceOf(badgerTree)
    strat_bcvx_after = bCvx.balanceOf(strategy.address)
    strat_bcvxCrv_after = bcvxCrv.balanceOf(strategy.address)
    strat_bveCVX_after = bveCVX.balanceOf(strategy.address)
    strat_cvx_after = cvx.balanceOf(strategy.address)
    strat_cvxCrv_after = cvxCrv.balanceOf(strategy.address)
    strat_crv_after = crv.balanceOf(strategy.address)
    strat_want_after = want.balanceOf(strategy.address)
    postion_after = strategy.balanceOf()

    gov_bcvx_after = bCvx.balanceOf(governance_multi)
    gov_bcvxCrv_after = bcvxCrv.balanceOf(governance_multi)
    gov_bveCVX_after = bveCVX.balanceOf(governance_multi)
    gov_want_after = want.balanceOf(governance_multi)


    console.print("\nPost Harvest Balances Diff\n")

    console.print("Tree bcvx:", (tree_bcvx_after-tree_bcvx_before)/1e18)
    console.print("Tree bcvxCrv:", (tree_bcvxCrv_after-tree_bcvxCrv_before)/1e18)
    console.print("Tree bveCVX:", (tree_bveCVX_after-tree_bveCVX_before)/1e18)

    console.print("\nStrat bcvx:", (strat_bcvx_after-strat_bcvx_before)/1e18)
    console.print("Strat bcvxCrv:", (strat_bcvxCrv_after-strat_bcvxCrv_before)/1e18)
    console.print("Strat bveCVX:", (strat_bveCVX_after-strat_bveCVX_before)/1e18)
    console.print("Strat cvx:", (strat_cvx_after-strat_cvx_before)/1e18)
    console.print("Strat cvxCrv:", (strat_cvxCrv_after-strat_cvxCrv_before)/1e18)
    console.print("Strat crv:", (strat_crv_after-strat_crv_before)/1e18)
    console.print("Strat want:", (strat_want_after-strat_want_before)/1e18)
    console.print("Strat Position:", (postion_after-postion_before)/1e18)

    console.print("\nGovernance bcvx:", (gov_bcvx_after-gov_bcvx_before)/1e18)
    console.print("Governance bcvxCrv:", (gov_bcvxCrv_after-gov_bcvxCrv_before)/1e18)
    console.print("Governance bveCVX:", (gov_bveCVX_after-gov_bveCVX_before)/1e18)
    console.print("Governance want:", (gov_want_after-gov_want_before)/1e18)

    console.print("\nbaseRewardsPool earned:", baseRewardsPool.earned(strategy.address))
