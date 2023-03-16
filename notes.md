# Notes

**refs:**
 - https://github.com/ZhangZhuoSJTU/Web3Bugs
 - https://github.com/ZhangZhuoSJTU/Web3Bugs/blob/main/results/bugs.csv
 - https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable

 - slither:
    * https://secure-contracts.com/program-analysis/slither/exercise2.html
    * https://github.com/crytic/building-secure-contracts/tree/master/program-analysis/slither#docker
    * https://github.com/crytic/slither/wiki/Adding-a-new-detector
    * https://github.com/crytic/slither/blob/master/slither/detectors/examples/backdoor.py
    * https://github.com/crytic/slither/tree/master/examples/scripts


<br>

**'Contract'**
 - ref https://github.com/crytic/slither/blob/master/slither/core/declarations/contract.py

`inheritance` : Inheritance list. Order: the first elem is the first father to be executed

`immediate_inheritance` : List of contracts immediately inherited from (fathers). Order: order of declaration.

`inheritance_reverse`: Inheritance list. Order: the last elem is the first father to be executed



