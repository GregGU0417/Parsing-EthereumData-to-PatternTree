# Parsing-EthereumData-to-PatternTree
This project parse transaction on Ethereum to a Pattern Tree, which is a data frame that could be used for future Data analytics and Visualization. The ultimate goal is to help trader on DeFi have better understanding on the transaction.
## What is Pattern Parsing Tree
### What is Pattern
- The pattern is a series of Transfer/Mint/Burn inside a transaction that has some unique meaning and can be mapped to some part of the transaction.
- Example Pattern:

- To see our patterns, sample transactions, and our notes, please visit: TBD (the website is under development)
- To access the  Pattern Database on MongoDB(like wanting to add notes or sample transactions to patterns), please contact Greg Gu (bowengu2@illinois.edu) 
## How Pattern is Mapped to Transaction
- We match the pattern with the subtree of the call stack tree of a transaction. If the union of events in the subtree is the same as the pattern, the pattern will be mapped to the subtree. To clarify, both the graph Isomorphism and 1-1 mapping on the token are required for pattern match. 
- The pattern is organized in a tree structure that keeps its contract-calling relationship. We name the result **Pattern Parsing Tree** or **Pattern Tree**.
## Why use Pattern Parsing Tree
- You can see the pattern parsing process as **Feature Engineering** in the original tree structure of Ethereum data. It can help professional Defi traders understand complex transactions.
- We find out that many of the patterns are connected with specific protocols (Ex: AAVE and Uniswap)
- We believe that many of the specific types of complex transactions on the blockchain, especially those related to MEV (Maximal Extractable Value), might be mapped to some structure of the Pattern Tree. For example, Arbitrage, Liquidation, Collectrual Swap, and Flashloan... We are searching for the relationships, and more results will be published soon.
- We also expect that the pattern tree can help us analyze the relationship between different transactions (ex: Sandwich Attack)

## What does the data input look like
- We use customized call stack API
- You get the data by using  the JSON_RPC API by making curl requests to an Ethereum node. Examples are provided below.
```
curl -X POST -H "Content-Type: application/json" --data '{"jsonrpc": "2.0", "method": "debug_eigenphiPlainTraceByNumber", "params": [14250000], "id":1 }' 127.0.0.1:8545
```
- The returning data is a list of **call frames**
- The Data field in each frame includes: frameId, type, label, from, to, contractCreated, value, input, error, childrenCount
- Example of single **call frame**:
```
{'frameId': '0',
  'type': 'CALL',
  'label': '',
  'from': '0x4e2a55d3553549ed7ec1a8c6834ac871b264bf2e',
  'to': '0x00000000006c3852cbef3e08e8df289169ede581',
  'contractCreated': '',
  'value': '0x0',
  'input': '',
  'error': '',
  'childrenCount': 3}
  ```

## Data Processing
### Parsing Event
- Parsing event with effective transfer/mint/burn that generates capital flow.
- Result:
  - list_of_parsing: a list that stores the event parsing result
```
'''
example 1: event without any effective transfer/mint/burn
'''
{'type': 'empty'}
```
```
'''
example 2: an event that transfers some tokens from one address to another
'''
{'type': 'transfer',
  'from': '0x2ae16e11573bdb2c2019a510ffe620621c18b6be',
  'to': '0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7',
  'token': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
  'amount': 10620000,
  'tokenID': 'empty'}
 ```
  - graph: the adjacent list that stores the tree structure of the transaction
 ```
'''
example
'''
{0: {1, 2, 5, 7}, 2: {3}, 3: {4}, 5: {6}}
```
- Note: We do not consider the mint/burn of platform tokens. In the case of Ethereum, we treat ETH and WETH equally
- Example: 
- TxHash: 0x2cf98dd2609ffe224ce81d4f60a759b36f868aca757592653d4abff2abdcd61a

### Tree Pruning
- Trim unnecessary branches
- If a subtree of a graph does not have any events that are effective transfer/mint/burn, then trim these branches
- The goal of Tree Pruning is to facilitate visualization and Data Analysis.
- Result:
  - `list_of_parsing`: a list that stores the event parsing result (same as above)
  - `simplify_tree`: the adjacent list that stores the tree structure of the Pruning Tree
  - Note: You can also use `get_effective_nodes(simplify_tree)` to get the list of nodes in the Pruning Tree
- Example : (same transaction as above)
- TxHash: 0x2cf98dd2609ffe224ce81d4f60a759b36f868aca757592653d4abff2abdcd61a

### Pattern matching
- We have around 600+ patterns in our database at this time. I will map the subtree of the pruning tree with a certain pattern in the list.
- The algorithm I use is multi-directed graph isomorphism on capital flow path and pattern, also 1-1 mapping on token matching. I am also using the amount check on the number of token transfer/mint/burn and NFT transfer /mint/burn to accelerate the process. If you have any better algorithms to solve the problem, please contact me(Greg Gu) at bowengu2@illinois.edu
- It is possible that the subtree does not match any of the existing lists. The pattern database needs expanding!
- Note: 
  - The subtree with a transaction that can not match any of the patterns will be marked as an "undiscovered pattern"
  - The pattern with  different token transfers that are on the same path can not be identified at this time. For example, Transfer T0 from 1 to 3, Transfer T2 from 1 to 3.
  - Subtrees that have transferred on their root node will not be identified at this time.  I am trying to filter some transfers that are not helpful for our analysis.

### Pattern Tree Generation
- The result of paring trees are :
- pattern_list: a list of dictionary
  - node : empty/some pattern/undiscovered pattern
  - degree : store the parsing tree structure
```
'''
example 
'''
[{'node': 'transfer_T0_1_2/burn_T3_2/transfer_T4_5_2/transfer_T4_2_1',
  'degree': '0-0'},
 {'node': 'transfer_T0_1_2/transfer_T3_2_1', 'degree': '0-1'},
 {'node': 'empty', 'degree': '0'}]
 ```
- Example result:
- TxHash: 0x2cf98dd2609ffe224ce81d4f60a759b36f868aca757592653d4abff2abdcd61a
 

