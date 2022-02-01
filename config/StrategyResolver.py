from helpers.StrategyCoreResolver import StrategyCoreResolver
from brownie import interface, SettV4
from rich.console import Console
from helpers.utils import val, approx
from tabulate import tabulate
from helpers.eth_registry import convex_registry

console = Console()


class StrategyResolver(StrategyCoreResolver):

    ## TODO: Confirm Deposit / Earn and Withdraw so we verify balances move as expected
    def hook_after_confirm_withdraw(self, before, after, params):
        if before.balances("want", "sett") < params["amount"] / before.get("sett.pricePerFullShare"):
        ## Want goes away from the booster as wrapped convexLpToken
            assert after.balances("convexLpToken", "baseRewardsPool") < before.balances(
                "convexLpToken", "baseRewardsPool"
            )

    def hook_after_earn(self, before, after, params):
        ## Want goes into booster, as wrapped convexLpToken
        assert after.balances("convexLpToken", "baseRewardsPool") > before.balances(
            "convexLpToken", "baseRewardsPool"
        )

    # ===== override default =====
    def confirm_harvest_events(self, before, after, tx):
        key = "TreeDistribution"
        assert key in tx.events
        assert len(tx.events[key]) >= 1
        for event in tx.events[key]:
            keys = [
                "token",
                "amount",
                "blockNumber",
                "timestamp",
            ]
            for key in keys:
                assert key in event

            console.print(
                "[blue]== Convex Strat harvest() TreeDistribution State ==[/blue]"
            )
            self.printState(event, keys)

        key = "PerformanceFeeGovernance"
        assert key in tx.events
        assert len(tx.events[key]) >= 1
        for event in tx.events[key]:
            keys = [
                "destination",
                "token",
                "amount",
                "blockNumber",
                "timestamp",
            ]
            for key in keys:
                assert key in event

            console.print(
                "[blue]== Convex Strat harvest() PerformanceFeeGovernance State ==[/blue]"
            )
            self.printState(event, keys)

        key = "Harvest"
        assert key in tx.events
        assert len(tx.events[key]) == 1
        event = tx.events[key][0]
        keys = [
            "harvested",
        ]
        for key in keys:
            assert key in event

        console.print("[blue]== Cvx Helper Strat harvest() State ==[/blue]")
        self.printState(event, keys)

        key = "PerformanceFeeStrategist"
        assert key not in tx.events
        # Strategist performance fee is set to 0

    def confirm_tend_events(self, before, after, tx):
        key = "Tend"
        assert key in tx.events
        assert len(tx.events[key]) == 1

        event = tx.events[key][0]
        keys = [
            "tended",
        ]
        for key in keys:
            assert key in event

        console.print("[blue]== Convex Strat tend() State ==[/blue]")
        self.printState(event, keys)

        key = "TendState"
        assert key in tx.events
        assert len(tx.events[key]) == 1

        event = tx.events[key][0]
        keys = [
            "crvTended",
            "cvxTended",
            "cvxCrvTended",
        ]
        for key in keys:
            assert key in event
        self.printState(event, keys)

    def printState(self, event, keys):
        table = []
        nonAmounts = ["token", "destination", "blockNumber", "timestamp"]
        for key in keys:
            if key in nonAmounts:
                table.append([key, event[key]])
            else:
                table.append([key, val(event[key])])

        print(tabulate(table, headers=["account", "value"]))

    # ===== Strategies must implement =====
    def confirm_harvest(self, before, after, tx):
        console.print("=== Compare Convex Harvest() ===")

        strategy = self.manager.strategy
        govPerformanceFee = strategy.performanceFeeGovernance() / 10000
        stratPerformanceFee = strategy.performanceFeeStrategist() / 10000

        totalPerformanceFee = govPerformanceFee + stratPerformanceFee

        # Harvest event emission not yet implemented
        self.confirm_harvest_events(before, after, tx)

        super().confirm_harvest(before, after, tx)

        ## === Check harvest performance == ##

        # Strategy want should increase
        assert after.get("strategy.balanceOf") == before.get("strategy.balanceOf")

        # PPFS should not decrease
        assert after.get("sett.pricePerFullShare") == before.get(
            "sett.pricePerFullShare"
        )


        # (100% - performanceFee) of collected cvxCrv is deposited on helper vaults
        cvx_crv_helper_vault_delta = after.balances(
            "cvxCrv", "cvxCrvHelperVault"
        ) - before.balances("cvxCrv", "cvxCrvHelperVault")
        cvx_crv_pool_delta = after.balances(
            "cvxCrv", "cvxCrvRewardsPool"
        ) - before.balances("cvxCrv", "cvxCrvRewardsPool")

        ## We earned at least (100% - performanceFee) of the delta (because we get some extra stuff)
        assert cvx_crv_helper_vault_delta > cvx_crv_pool_delta * (1 - totalPerformanceFee)

        ## bcvxCrv is sent to Tree, just check balance increased
        assert after.balances("bCvxCrv", "badgerTree") > before.balances(
            "bCvxCrv", "badgerTree"
        )

        ## bveCVX is sent to Tree, just check balance increased
        assert after.balances("bveCVX", "badgerTree") > before.balances(
            "bveCVX", "badgerTree"
        )

        # (100% - totalPerformanceFee) of cvxCrvHelperVault shares were distributed through the tree
        actual_tree_bcvx_crv_delta = after.balances(
            "bCvxCrv", "badgerTree"
        ) - before.balances("bCvxCrv", "badgerTree")

        actual_governance_bcvx_crv_delta = after.balances(
                "bCvxCrv", "governanceRewards"
        ) - before.balances("bCvxCrv", "governanceRewards")

        actual_strategist_bcvx_crv_delta = after.balances(
            "bCvxCrv", "strategist"
        ) - before.balances("bCvxCrv", "strategist")

        total_bcvx_crv_delta = (
            actual_tree_bcvx_crv_delta +
            actual_governance_bcvx_crv_delta +
            actual_strategist_bcvx_crv_delta
        )

        assert approx(
            actual_tree_bcvx_crv_delta,
            total_bcvx_crv_delta * (1 - totalPerformanceFee),
            1
        )

        # (100% - totalPerformanceFee) of bveCVX shares were distributed through the tree
        actual_tree_bveCVX_delta = after.balances(
            "bveCVX", "badgerTree"
        ) - before.balances("bveCVX", "badgerTree")

        actual_governance_bveCVX_delta = after.balances(
                "bveCVX", "governanceRewards"
        ) - before.balances("bveCVX", "governanceRewards")

        actual_strategist_bveCVX_delta = after.balances(
            "bveCVX", "strategist"
        ) - before.balances("bveCVX", "strategist")

        total_bveCVX_delta = (
            actual_tree_bveCVX_delta +
            actual_governance_bveCVX_delta +
            actual_strategist_bveCVX_delta
        )

        assert approx(
            actual_tree_bveCVX_delta,
            total_bveCVX_delta * (1 - totalPerformanceFee),
            1
        )


        ## === Check Proper Fees == ##

        ## bcvxCrv and bveCVX are sent to Governance if performanceFeeGovernance not 0
        if govPerformanceFee > 0:
            assert after.balances("bCvxCrv", "governanceRewards") > before.balances(
                "bCvxCrv", "governanceRewards"
            )
            assert after.balances("bveCVX", "governanceRewards") > before.balances(
                "bveCVX", "governanceRewards"
            )
            # govPerformanceFee % of Total bcvxCRV and bveCVX are charged
            assert approx(
                actual_governance_bcvx_crv_delta, 
                total_bcvx_crv_delta * govPerformanceFee,
                1
            )

            assert approx(
                actual_governance_bveCVX_delta, 
                total_bveCVX_delta * govPerformanceFee,
                1
            )
        else:
            assert after.balances("bCvxCrv", "governanceRewards") == before.balances(
                "bCvxCrv", "governanceRewards"
            )
            assert after.balances("bveCVX", "governanceRewards") == before.balances(
                "bveCVX", "governanceRewards"
            )

        ## bveCVX is sent to Strategist if performanceFeeStrategist not 0
        if stratPerformanceFee > 0:
            assert after.balances("bCvxCrv", "strategist") > before.balances(
                "bCvxCrv", "strategist"
            )
            assert after.balances("bveCVX", "strategist") > before.balances(
                "bveCVX", "strategist"
            )
            # stratPerformanceFee % of Total bcvxCRV and bveCVX are charged
            assert approx(
                actual_strategist_bcvx_crv_delta, 
                total_bcvx_crv_delta * stratPerformanceFee,
                1
            )

            assert approx(
                actual_strategist_bveCVX_delta, 
                total_bveCVX_delta * stratPerformanceFee,
                1
            )
        else:
            assert after.balances("bCvxCrv", "strategist") == before.balances(
                "bCvxCrv", "strategist"
            )
            assert after.balances("bveCVX", "strategist") == before.balances(
                "bveCVX", "strategist"
            )


        # 0% of want should be transferred to governance (No autocompounding)
        actual_governance_change = after.balances(
            "want", "governanceRewards"
        ) - before.balances("want", "governanceRewards")
        assert actual_governance_change == 0


        # 0% of want should be transferred to strategist (No autocompounding)
        actual_strategist_change = after.balances(
            "want", "strategist"
        ) - before.balances("want", "strategist")
        assert actual_strategist_change == 0



    def confirm_tend(self, before, after, tx):
        self.confirm_tend_events(before, after, tx)

        console.print("=== Compare Convex Tend() ===")
        self.manager.printCompare(before, after)

        # Expect decrease crv balance of rewardsPool and increase cvx cvxCrv
        event = tx.events["TendState"][0]
        if event["cvxTended"] > 0:
            assert after.balances("cvx", "cvxRewardsPool") > before.balances(
                "cvx", "cvxRewardsPool"
            )
            assert after.balances("cvx", "strategy") == before.balances(
                "cvx", "strategy"
            )
            assert before.balances("cvx", "strategy") == 0

        if event["cvxCrvTended"] > 0:
            assert after.balances("cvxCrv", "cvxCrvRewardsPool") > before.balances(
                "cvxCrv", "cvxCrvRewardsPool"
            )
            assert after.balances("cvxCrv", "strategy") == before.balances(
                "cvxCrv", "strategy"
            )
            assert before.balances("cvxCrv", "strategy") == 0

    def get_strategy_destinations(self):
        """
        Track balances for all strategy implementations
        (Strategy Must Implement)
        """

        strategy = self.manager.strategy
        return {}

    def add_entity_balances_for_tokens(self, calls, tokenKey, token, entities):
        entities["badgerTree"] = self.manager.strategy.badgerTree()
        entities["strategy"] = self.manager.strategy.address
        entities["cvxCrvRewardsPool"] = self.manager.strategy.cvxCrvRewardsPool()
        entities["cvxRewardsPool"] = self.manager.strategy.cvxRewardsPool()
        entities["baseRewardsPool"] = self.manager.strategy.baseRewardsPool()
        entities["cvxHelperVault"] = convex_registry.cvxHelperVault
        entities["cvxCrvHelperVault"] = convex_registry.cvxCrvHelperVault

        super().add_entity_balances_for_tokens(calls, tokenKey, token, entities)
        return calls

    def add_balances_snap(self, calls, entities):
        super().add_balances_snap(calls, entities)
        strategy = self.manager.strategy

        crv = interface.IERC20(strategy.crv())
        cvx = interface.IERC20(strategy.cvx())
        _3Crv = interface.IERC20("0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490")
        BOR = interface.IERC20("0x3c9d6c1c73b31c837832c72e04d3152f051fc1a9")
        PNT = interface.IERC20("0x89ab32156e46f46d02ade3fecbe5fc4243b9aaed")
        wbtc = interface.IERC20("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")
        usdc = interface.IERC20("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
        cvxCrv = interface.IERC20(strategy.cvxCrv())
        bveCVX = interface.IERC20(strategy.bveCVX())
        bCvxCrv = interface.IERC20(convex_registry.cvxCrvHelperVault)

        ## Get the booster for this strat
        booster = interface.IBooster(strategy.booster())
        ## So we can get the lpToken associated
        convexLpToken = interface.IERC20(booster.poolInfo(strategy.pid())["token"])

        calls = self.add_entity_balances_for_tokens(
            calls, "convexLpToken", convexLpToken, entities
        )
        calls = self.add_entity_balances_for_tokens(calls, "crv", crv, entities)
        calls = self.add_entity_balances_for_tokens(calls, "cvx", cvx, entities)
        calls = self.add_entity_balances_for_tokens(calls, "3Crv", _3Crv, entities)
        calls = self.add_entity_balances_for_tokens(calls, "BOR", BOR, entities)
        calls = self.add_entity_balances_for_tokens(calls, "PNT", PNT, entities)
        calls = self.add_entity_balances_for_tokens(calls, "WBTC", wbtc, entities)
        calls = self.add_entity_balances_for_tokens(calls, "USDC", usdc, entities)
        calls = self.add_entity_balances_for_tokens(calls, "cvxCrv", cvxCrv, entities)
        calls = self.add_entity_balances_for_tokens(calls, "bveCVX", bveCVX, entities)
        calls = self.add_entity_balances_for_tokens(calls, "bCvxCrv", bCvxCrv, entities)

        return calls
