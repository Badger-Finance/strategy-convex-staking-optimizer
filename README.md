# Badger Strategy V1 Brownie Mix

- Video Introduction: https://youtu.be/FVbhgPYW_D0

- Example Project: https://github.com/Badger-Finance/wBTC-AAVE-Rewards-Farm-Badger-V1-Strategy
- Full Project Walkthrough: https://www.youtube.com/watch?v=lTb0RFJJx2k
- 1-1 Mentoring (Valid throughout HackMoney and Gitcoin Round 10): https://calendly.com/alex-entreprenerd/badger-hackmoney-1-1

## What you'll find here

- Basic Solidity Smart Contract for creating your own Badger Strategy ([`contracts/StrategyConvexStakingOptimizer.sol`](contracts/StrategyConvexStakingOptimizer.sol))

- Interfaces for some of the most used DeFi protocols on ethereum mainnet. ([`interfaces`](interfaces))
- Dependencies for OpenZeppelin and other libraries. ([`deps`](deps))

- Sample test suite that runs on mainnet fork. ([`tests`](tests))

This mix is configured for use with [Ganache](https://github.com/trufflesuite/ganache-cli) on a [forked mainnet](https://eth-brownie.readthedocs.io/en/stable/network-management.html#using-a-forked-development-network).

## Installation and Setup

1. Use this code by clicking on Use This Template

2. Download the code with `git clone URL_FROM_GITHUB`

3. [Install Brownie](https://eth-brownie.readthedocs.io/en/stable/install.html) & [Ganache-CLI](https://github.com/trufflesuite/ganache-cli), if you haven't already.

4. Copy the `.env.example` file, and rename it to `.env`

5. Sign up for [Alchemy](https://www.alchemy.com/) and generate an API key. Store it in the `ALCHEMYAPI_TOKEN` environment variable.

6. Sign up for [Etherscan](www.etherscan.io) and generate an API key. This is required for fetching source codes of the mainnet contracts we will be interacting with. Store the API key in the `ETHERSCAN_TOKEN` environment variable.

7. Install the dependencies in the package

```
## Javascript dependencies
npm i

## Python Dependencies
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Basic Use

To deploy the demo Badger Strategy in a development environment:

1. Open the Brownie console. This automatically launches Ganache on a forked mainnet.

```bash
  brownie console
```

2. Run Scripts for Deployment

```
  brownie run scripts/1_production_deploy.py
```

Deployment will set up a Vault, Controller and deploy your strategy

## Adding Configuration

To ship a valid strategy, that will be evaluated to deploy on mainnet, with potentially $100M + in TVL, you need to:

1. Add custom config in `/config/__init__.py`
2. Write the Strategy Code in StrategyConvexStakingOptimizer.sol
3. Customize the StrategyResolver in `/config/StrategyResolver.py` so that snapshot testing can verify that operations happened correctly
4. Write any extra test to confirm that the strategy is working properly

## Add a custom want configuration

Most strategies have a:

- **want** the token you want to increase the balance of
- **lpComponent** the token representing how much you deposited in the yield source
- **reward** the token you are farming, that you'll swap into **want**

Set these up in `/config/__init__.py` this mix will automatically be set up for testing and deploying after you do so

## Implementing Strategy Logic

[`contracts/StrategyConvexStakingOptimizer.sol`](contracts/StrategyConvexStakingOptimizer.sol) is where you implement your own logic for your strategy. In particular:

- Customize the `initialize` Method
- Set a name in `StrategyConvexStakingOptimizer.getName()`
- Set a version in `StrategyConvexStakingOptimizer.version()`
- Write a way to calculate the want invested in `StrategyConvexStakingOptimizer.balanceOfPool()`
- Write a method that returns true if the Strategy should be tended in `StrategyConvexStakingOptimizer.isTendable()`
- Set a version in `StrategyConvexStakingOptimizer.version()`
- Invest your want tokens via `Strategy._deposit()`.
- Take profits and repay debt via `Strategy.harvest()`.
- Unwind enough of your position to payback withdrawals via `Strategy._withdrawSome()`.
- Unwind all of your positions via `Strategy._withdrawAll()`.
- Rebalance the Strategy positions via `Strategy.tend()`.
- Make a list of all position tokens that should be protected against movements via `Strategy.protectedTokens()`.

## Specifying checks for ordinary operations in config/StrategyResolver

In order to snapshot certain balances, we use the Snapshot manager.
This class helps with verifying that ordinary procedures (deposit, withdraw, harvest), happened correctly.

See `/helpers/StrategyCoreResolver.py` for the base resolver that all strategies use
Edit `/config/StrategyResolver.py` to specify and verify how an ordinary harvest should behave

### StrategyResolver

- Add Contract to check balances for in `get_strategy_destinations` (e.g. deposit pool, gauge, lpTokens)
- Write `confirm_harvest` to verify that the harvest was profitable
- Write `confirm_tend` to verify that tending will properly rebalance the strategy
- Specify custom checks for ordinary deposits, withdrawals and calls to `earn` by setting up `hook_after_confirm_withdraw`, `hook_after_confirm_deposit`, `hook_after_earn`

## Add your custom testing

Check the various tests under `/tests`
The file `/tests/test_custom` is already set up for you to write custom tests there
See example tests in `/tests/examples`
All of the tests need to pass!
If a test doesn't pass, you better have a great reason for it!

## Testing

To run the tests:

```
brownie test
```

## Debugging Failed Transactions

Use the `--interactive` flag to open a console immediatly after each failing test:

```
brownie test --interactive
```

Within the console, transaction data is available in the [`history`](https://eth-brownie.readthedocs.io/en/stable/api-network.html#txhistory) container:

```python
>>> history
[<Transaction '0x50f41e2a3c3f44e5d57ae294a8f872f7b97de0cb79b2a4f43cf9f2b6bac61fb4'>,
 <Transaction '0xb05a87885790b579982983e7079d811c1e269b2c678d99ecb0a3a5104a666138'>]
```

Examine the [`TransactionReceipt`](https://eth-brownie.readthedocs.io/en/stable/api-network.html#transactionreceipt) for the failed test to determine what went wrong. For example, to view a traceback:

```python
>>> tx = history[-1]
>>> tx.traceback()
```

To view a tree map of how the transaction executed:

```python
>>> tx.call_trace()
```

See the [Brownie documentation](https://eth-brownie.readthedocs.io/en/stable/core-transactions.html) for more detailed information on debugging failed transactions.

## Deployment

When you are finished testing and ready to deploy to the mainnet:

1. [Import a keystore](https://eth-brownie.readthedocs.io/en/stable/account-management.html#importing-from-a-private-key) into Brownie for the account you wish to deploy from.
2. Run [`scripts/production_deploy.py`](scripts/production_deploy.py) with the following command:

```bash
$ brownie run scripts/production_deploy.py --network mainnet
```

You will be prompted to enter your desired deployer account and keystore password, and then the contracts will be deployed.

3. This script will deploy a Controller, a SettV4 and your strategy under upgradable proxies. It will also set your deployer account as the governance for the three of them so that you can configure them and control them during testing stage. The script will also set the rest of the permissioned actors based on the latest entries from the Badger Registry.

## Production Parameters Verification

When you are done testing your contracts in production and they are ready for incorporation to the Badger ecosystem, the `production_setup` script can be ran to ensure that all parameters are set in compliance to Badger's production entities and contracts. You can run this script by doing the following:

1. Open the [`scripts/production_setup.py`](scripts/production_setup.py) file and change the addresses for your strategy and vault mainnet addresses on lines 29 and 30.
2. [Import a keystore](https://eth-brownie.readthedocs.io/en/stable/account-management.html#importing-from-a-private-key) into Brownie for the account currently set as `governance` for your contracts.
3. Run [`scripts/production_setup.py`](scripts/production_setup.py) with the following command:

```bash
$ brownie run scripts/production_setup.py --network mainnet
```

You will be prompted to enter your governance account and keystore password, and then the the parameter verification and setup process will be executed.

4. This script will compare all existing parameters against the latest production parameters stored on the Badger Registry. In case of a mismatch, the script will execute a transaction to change the parameter to the proper one. Notice that, as a final step, the script will change the governance address to Badger's Governance Multisig; this will effectively relinquish the contract control from your account to the Badger Governance. Additionally, the script performs a final check of all parameters against the registry parameters.

## Known issues

### No access to archive state errors

If you are using Ganache to fork a network, then you may have issues with the blockchain archive state every 30 minutes. This is due to your node provider (i.e. Infura) only allowing free users access to 30 minutes of archive state. To solve this, upgrade to a paid plan, or simply restart your ganache instance and redploy your contracts.

# Resources

- Example Strategy https://github.com/Badger-Finance/wBTC-AAVE-Rewards-Farm-Badger-V1-Strategy
- Badger [Discord channel](https://discord.gg/badgerdao)
- Alex The Entreprenerd on [Twitter](https://twitter.com/GalloDaSballo)
