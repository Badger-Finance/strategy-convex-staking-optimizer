import json
from dotmap import DotMap
from helpers.eth_registry import registry

curve = registry.curve
pools = registry.curve.pools
convex = registry.convex
whales = registry.whales

sett_config = DotMap(
    native=DotMap(
        # convexRenCrv=DotMap(
        #     strategyName="StrategyConvexStakingOptimizer",
        #     params=DotMap(
        #         want=pools.renCrv.token,
        #         pid=curve.pids.renCrv,
        #         lpComponent=registry.tokens.wbtc,
        #         performanceFeeStrategist=0,
        #         performanceFeeGovernance=2000,
        #         withdrawalFee=10,
        #         curvePool=DotMap(
        #             swap=registry.curve.pools.renCrv.swap,
        #             wbtcPosition=1,
        #             numElements=2,
        #         ),
        #         cvxHelperVault=convex.cvxHelperVault,
        #         cvxCrvHelperVault=convex.cvxCrvHelperVault,
        #     ),
        #     whale=whales.renCrv.whale,
        # ),
        # convexSbtcCrv=DotMap(
        #     strategyName="StrategyConvexStakingOptimizer",
        #     params=DotMap(
        #         want=pools.sbtcCrv.token,
        #         pid=curve.pids.sbtcCrv,
        #         lpComponent=registry.tokens.wbtc,
        #         performanceFeeStrategist=0,
        #         performanceFeeGovernance=2000,
        #         withdrawalFee=10,
        #         curvePool=DotMap(
        #             swap=registry.curve.pools.sbtcCrv.swap,
        #             wbtcPosition=1,
        #             numElements=3,
        #         ),
        #         cvxHelperVault=convex.cvxHelperVault,
        #         cvxCrvHelperVault=convex.cvxCrvHelperVault,
        #     ),
        #     whale=whales.sbtcCrv.whale,
        # ),
        # convexTbtcCrv=DotMap(
        #     strategyName="StrategyConvexStakingOptimizer",
        #     params=DotMap(
        #         want=pools.tbtcCrv.token,
        #         pid=curve.pids.tbtcCrv,
        #         lpComponent=registry.tokens.wbtc,
        #         performanceFeeStrategist=0,
        #         performanceFeeGovernance=2000,
        #         withdrawalFee=10,
        #         curvePool=DotMap(
        #             swap=registry.curve.pools.tbtcCrv.swap,
        #             wbtcPosition=2,
        #             numElements=4,
        #         ),
        #         cvxHelperVault=convex.cvxHelperVault,
        #         cvxCrvHelperVault=convex.cvxCrvHelperVault,
        #     ),
        #     whale=whales.tbtcCrv.whale,
        # ),
        # convexHbtcCrv=DotMap(
        #     strategyName="StrategyConvexStakingOptimizer",
        #     params=DotMap(
        #         want=pools.hbtcCrv.token,
        #         pid=curve.pids.hbtcCrv,
        #         lpComponent=registry.tokens.wbtc,
        #         performanceFeeStrategist=0,
        #         performanceFeeGovernance=2000,
        #         withdrawalFee=10,
        #         curvePool=DotMap(
        #             swap=registry.curve.pools.hbtcCrv.swap,
        #             wbtcPosition=1,
        #             numElements=2,
        #         ),
        #         cvxHelperVault=convex.cvxHelperVault,
        #         cvxCrvHelperVault=convex.cvxCrvHelperVault,
        #     ),
        #     whale=whales.hbtcCrv.whale,
        # ),
        # convexObtcCrv=DotMap(
        #     strategyName="StrategyConvexStakingOptimizer",
        #     params=DotMap(
        #         want=pools.obtcCrv.token,
        #         pid=curve.pids.obtcCrv,
        #         lpComponent=registry.tokens.wbtc,
        #         performanceFeeStrategist=0,
        #         performanceFeeGovernance=2000,
        #         withdrawalFee=10,
        #         curvePool=DotMap(
        #             swap=registry.curve.pools.obtcCrv.swap,
        #             wbtcPosition=2,
        #             numElements=4,
        #         ),
        #         cvxHelperVault=convex.cvxHelperVault,
        #         cvxCrvHelperVault=convex.cvxCrvHelperVault,
        #     ),
        #     whale=whales.obtcCrv.whale,
        # ),
        # convexPbtcCrv=DotMap(
        #     strategyName="StrategyConvexStakingOptimizer",
        #     params=DotMap(
        #         want=pools.pbtcCrv.token,
        #         pid=curve.pids.pbtcCrv,
        #         lpComponent=registry.tokens.wbtc,
        #         performanceFeeStrategist=0,
        #         performanceFeeGovernance=2000,
        #         withdrawalFee=10,
        #         curvePool=DotMap(
        #             swap=registry.curve.pools.pbtcCrv.swap,
        #             wbtcPosition=2,
        #             numElements=4,
        #         ),
        #         cvxHelperVault=convex.cvxHelperVault,
        #         cvxCrvHelperVault=convex.cvxCrvHelperVault,
        #     ),
        #     whale=whales.pbtcCrv.whale,
        # ),
        # convexBbtcCrv=DotMap(
        #     strategyName="StrategyConvexStakingOptimizer",
        #     params=DotMap(
        #         want=pools.bbtcCrv.token,
        #         pid=curve.pids.bbtcCrv,
        #         lpComponent=registry.tokens.wbtc,
        #         performanceFeeStrategist=0,
        #         performanceFeeGovernance=2000,
        #         withdrawalFee=10,
        #         curvePool=DotMap(
        #             swap=registry.curve.pools.bbtcCrv.swap,
        #             wbtcPosition=2,
        #             numElements=4,
        #         ),
        #         cvxHelperVault=convex.cvxHelperVault,
        #         cvxCrvHelperVault=convex.cvxCrvHelperVault,
        #     ),
        #     whale=whales.bbtcCrv.whale,
        # ),
        # convexTriCryptoDos=DotMap(
        #     strategyName="StrategyConvexStakingOptimizer",
        #     params=DotMap(
        #         want=pools.triCryptoDos.token,
        #         pid=curve.pids.triCryptoDos,
        #         lpComponent=registry.tokens.wbtc,
        #         performanceFeeStrategist=0,
        #         performanceFeeGovernance=2000,
        #         withdrawalFee=10,
        #         curvePool=DotMap(
        #             swap=registry.curve.pools.triCryptoDos.swap,
        #             wbtcPosition=1,
        #             numElements=3,
        #         ),
        #         cvxHelperVault=convex.cvxHelperVault,
        #         cvxCrvHelperVault=convex.cvxCrvHelperVault,
        #     ),
        #     whale=whales.triCrypto2.whale,
        # ),
        # convexIbbtcCrv=DotMap(
        #     strategyName="StrategyConvexStakingOptimizer",
        #     params=DotMap(
        #         want=pools.ibbtcCrv.token,
        #         pid=curve.pids.ibbtcCrv,
        #         lpComponent=registry.tokens.wbtc,
        #         performanceFeeStrategist=0,
        #         performanceFeeGovernance=2000,
        #         withdrawalFee=10,
        #         curvePool=DotMap(
        #             swap=registry.curve.pools.ibbtcCrv.swap,
        #             ibbtcPosition=0,
        #             numElements=4,
        #         ),
        #         cvxHelperVault=convex.cvxHelperVault,
        #         cvxCrvHelperVault=convex.cvxCrvHelperVault,
        #     ),
        # ),
        # convexCvxEthCrv=DotMap(
        #     strategyName="StrategyConvexStakingOptimizer",
        #     params=DotMap(
        #         want=pools.cvxEthCrv.token,
        #         pid=curve.pids.cvxEthCrv,
        #         lpComponent=registry.tokens.weth,
        #         performanceFeeStrategist=0,
        #         performanceFeeGovernance=2000,
        #         withdrawalFee=10,
        #         curvePool=DotMap(
        #             swap=registry.curve.pools.cvxEthCrv.swap,
        #             wethPosition=0,
        #             numElements=2,
        #         ),
        #         cvxHelperVault=convex.cvxHelperVault,
        #         cvxCrvHelperVault=convex.cvxCrvHelperVault,
        #     ),
        # ),
        convexCrvCvxCrv=DotMap(
            strategyName="StrategyConvexStakingOptimizer",
            params=DotMap(
                want=pools.crvCvxCrv.token,
                pid=curve.pids.crvCvxCrv,
                lpComponent=registry.tokens.crv,
                performanceFeeStrategist=0,
                performanceFeeGovernance=2000,
                withdrawalFee=10,
                curvePool=DotMap(
                    swap=registry.curve.pools.crvCvxCrv.swap,
                    crvPosition=0,
                    numElements=2,
                ),
                cvxHelperVault=convex.cvxHelperVault,
                cvxCrvHelperVault=convex.cvxCrvHelperVault,
            ),
        ),
    ),
    helper=DotMap(
        cvx=DotMap(
            strategyName="StrategyCvxHelper",
            params=DotMap(
                want=registry.tokens.cvx,
                performanceFeeStrategist=1000,
                performanceFeeGovernance=1000,
                withdrawalFee=20,
            ),
        ),
        cvxCrv=DotMap(
            strategyName="StrategyCvxCrvHelper",
            params=DotMap(
                want=registry.tokens.cvxCrv,
                performanceFeeStrategist=1000,
                performanceFeeGovernance=1000,
                withdrawalFee=20,
            ),
        ),
    ),
)

badger_config = DotMap(
    prod_json="deploy-final.json",
)

config = DotMap(
    badger=badger_config,
    sett=sett_config,
)
