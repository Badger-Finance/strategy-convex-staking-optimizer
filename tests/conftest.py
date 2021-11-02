from brownie import (
    accounts,
    interface,
    Controller,
    SettV4,
    StrategyConvexStakingOptimizer,
)
from config import (
    BADGER_DEV_MULTISIG,
    BADGER_TREE,
)
from dotmap import DotMap
import pytest
from rich.console import Console

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
            sett_config.params.cvxHelperVault,
            sett_config.params.cvxCrvHelperVault,
        ],
        sett_config.params.pid,
        [
            sett_config.params.performanceFeeGovernance,
            sett_config.params.performanceFeeStrategist,
            sett_config.params.withdrawalFee,
        ],
        (
            sett_config.params.curvePool.swap,
            sett_config.params.curvePool.wbtcPosition,
            sett_config.params.curvePool.numElements,
        ),
    ]

    ## Start up Strategy
    strategy = StrategyConvexStakingOptimizer.deploy({"from": deployer})
    strategy.initialize(*args)


    ## Grant contract access from strategy to Helper Vaults
    cvxHelperVault = SettV4.at(strategy.cvxHelperVault())
    cvxCrvHelperVault = SettV4.at(strategy.cvxCrvHelperVault())

    cvxHelperGov = accounts.at(cvxHelperVault.governance(), force=True)
    cvxCrvHelperGov = accounts.at(cvxCrvHelperVault.governance(), force=True)

    cvxHelperVault.approveContractAccess(strategy.address, {"from": cvxHelperGov})
    cvxCrvHelperVault.approveContractAccess(strategy.address, {"from": cvxCrvHelperGov})

    ## Set up tokens
    want = interface.IERC20(strategy.want())

    ## Wire up Controller to Strart
    ## In testing will pass, but on live it will fail
    controller.approveStrategy(want, strategy, {"from": governance})
    controller.setStrategy(want, strategy, {"from": deployer})

    # Transfer test assets to deployer
    whale = accounts.at(
        sett_config.whale, force=True
    )
    want.transfer(
        deployer.address, want.balanceOf(whale.address), {"from": whale}
    )  # Transfer 80% of whale's want balance

    assert want.balanceOf(deployer.address) > 0

    return DotMap(
        deployer=deployer,
        controller=controller,
        sett=sett,
        strategy=strategy,
        want=want,
    )
