# smart contract auditor tool

SCA (smart contract auditor) tool - Tool for doing security checks on smart contracts

Functionalities supported:
 - show upgradeable contracts missing gap storage
 - show inheritance graph flows


### usage
 - tested on slither docker image ([link](https://github.com/crytic/building-secure-contracts/tree/master/program-analysis/slither#docker))

```
usage: main.py [-h] [-w] [-c] --path PATH
               [--inheritance_check INHERITANCE_CHECK [INHERITANCE_CHECK ...]]
               [--check_gap]

main.py: Tool for doing security checks on smart contracts

optional arguments:
  -h, --help            show this help message and exit
  -w                    Print compiler warnings (default False)
  -c                    Re/compile contracts
  --path PATH           Project's directory
  --inheritance_check INHERITANCE_CHECK [INHERITANCE_CHECK ...]
                        Print inheritance chains (expects two arguments)
  --check_gap           Check __gap missing on upgradeable contracts

```

<br>

 - example 1: find upgradeable contracts missing gap storage

```bash
python3 main.py --path ./2022-05-alchemix/ --check_gap

...

[!] Missing gap on upgradeable contracts:
 - AlchemicTokenV2Base (AccessControlUpgradeable, ERC20Upgradeable, ReentrancyGuardUpgradeable)
 - TransmuterV2 (AccessControlUpgradeable, ReentrancyGuardUpgradeable)
 - CrossChainCanonicalBase (ERC20PermitUpgradeable, OwnableUpgradeable, ReentrancyGuardUpgradeable)
 - CrossChainCanonicalAlchemicTokenV2 (AlchemicTokenV2Base, CrossChainCanonicalBase)
 - CrossChainCanonicalGALCX (CrossChainCanonicalBase)
[+] Done
```

<br>

 - example 2: show inheritance graph flows starting from `CrossChainCanonicalBase` to `OwnableUpgradeable`

```bash
python3 main.py --path ./2022-05-alchemix/ --inheritance_check CrossChainCanonicalBase OwnableUpgradeable

...


\-->Node:46("CrossChainCanonicalBase")
    \-->Node:2("OwnableUpgradeable")

[+] Done
```






