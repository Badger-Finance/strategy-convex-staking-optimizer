require("@nomiclabs/hardhat-etherscan");

task("accounts", "Prints the list of accounts", async (taskArgs, hre) => {
  const accounts = await hre.ethers.getSigners();

  for (const account of accounts) {
    console.log(account.address);
  }
});

const defaultNetwork = "localhost";

const mainnetGwei = 21;

const ALCHEMYAPI_TOKEN = process.env.INFURA_PROJECT_ID;
const ETHERSCAN_KEY = process.env.ETHERSCAN_KEY;

function mnemonic() {
  try {
    return fs.readFileSync("./mnemonic.txt").toString().trim();
  } catch (e) {
    if (defaultNetwork !== "localhost") {
      console.log(
        "☢️ WARNING: No mnemonic file created for a deploy account. Try `yarn run generate` and then `yarn run account`."
      );
    }
  }
  return "";
}

module.exports = {
  solidity: {
    compilers: [
      {
        version: "0.6.12",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      },
      {
        version: "0.6.8",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      },
      {
        version: "0.5.10",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      },
      {
        version: "0.4.24",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      },
    ],
  },
  defaultNetwork,
  networks: {
    localhost: {
      url: "http://localhost:8545",
    },
    hardhat: {
      hardfork: "london",
      // base fee of 0 allows use of 0 gas price when testing
      initialBaseFeePerGas: 0,
      // brownie expects calls and transactions to throw on revert
      throwOnTransactionFailures: true,
      throwOnCallFailures: true,
    },
    mainnet: {
      url: "https://eth-mainnet.alchemyapi.io/v2/" + ALCHEMYAPI_TOKEN,
      gasPrice: mainnetGwei * 1000000000,
      accounts: {
        mnemonic: mnemonic(),
      },
    },
  },
  etherscan: {
    apiKey: ETHERSCAN_KEY,
  },
};