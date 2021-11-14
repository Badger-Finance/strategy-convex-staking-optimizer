from brownie import (
    accounts,
    interface,
    Controller,
    SettV4,
    StrategyConvexStakingOptimizer,
    Wei,
)
from config import (
    BADGER_DEV_MULTISIG,
    BADGER_TREE,
)
from dotmap import DotMap
import pytest
from rich.console import Console
import time
from helpers.time import days
from helpers.test.test_utils import generate_curve_LP_assets

console = Console()


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def deploy(sett_config):
    """
    Deploys, vault, controller and strats and wires them up for you to test
    """
    deployer = accounts[0]

    strategist = deployer
    keeper = deployer
    guardian = deployer

    governance = accounts.at(BADGER_DEV_MULTISIG, force=True)

    controller = Controller.deploy({"from": deployer})
    controller.initialize(BADGER_DEV_MULTISIG, strategist, keeper, BADGER_DEV_MULTISIG)

    # Get Sett arguments:
    args = [
        sett_config.params.want,
        controller,
        BADGER_DEV_MULTISIG,
        keeper,
        guardian,
        False,
        "prefix",
        "PREFIX",
    ]

    sett = SettV4.deploy({"from": deployer})
    sett.initialize(*args)

    sett.unpause({"from": governance})
    controller.setVault(sett.token(), sett)

    # Get Strategy arguments:
    args = [
        BADGER_DEV_MULTISIG,
        strategist,
        controller,
        keeper,
        guardian,
        [
            sett_config.params.want,
            BADGER_TREE,
            sett_config.params.cvxCrvHelperVault,
        ],
        sett_config.params.pid,
        [
            sett_config.params.performanceFeeGovernance,
            sett_config.params.performanceFeeStrategist,
            sett_config.params.withdrawalFee,
        ],
    ]

    ## Start up Strategy
    strategy = StrategyConvexStakingOptimizer.deploy({"from": deployer})
    strategy.initialize(*args)


    ## Grant contract access from strategy to cvxCRV Helper Vault
    cvxCrvHelperVault = SettV4.at(strategy.cvxCrvHelperVault())
    cvxCrvHelperGov = accounts.at(cvxCrvHelperVault.governance(), force=True)
    cvxCrvHelperVault.approveContractAccess(strategy.address, {"from": cvxCrvHelperGov})

    ## Reset rewards if they are set to expire within the next 4 days or are expired already
    rewardsPool = interface.IBaseRewardsPool(strategy.baseRewardsPool())
    if rewardsPool.periodFinish() - int(time.time()) < days(4):
        booster = interface.IBooster(strategy.booster())
        booster.earmarkRewards(sett_config.params.pid, {"from": deployer})
        console.print("[green]BaseRewardsPool expired or expiring soon - it was reset![/green]")

    ## Set up tokens
    want = interface.IERC20(strategy.want())

    ## Wire up Controller to Strart
    ## In testing will pass, but on live it will fail
    controller.approveStrategy(want, strategy, {"from": governance})
    controller.setStrategy(want, strategy, {"from": deployer})

    # Generate test want for user
    generate_curve_LP_assets(deployer, Wei("10 ether"), sett_config)

    assert want.balanceOf(deployer.address) > 0

    return DotMap(
        deployer=deployer,
        controller=controller,
        sett=sett,
        strategy=strategy,
        want=want,
    )
