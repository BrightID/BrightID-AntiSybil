# BrightID Anti-Sybil
This package provides a framework to evaluate the quality of different anti-sybil [algorithms](#algorithms), by simulating different [attacks](#attacks) to [BrightID's social graph](https://explorer.brightid.org).


![](https://explorer.brightid.org/assets/1589538690.png)

*Comparing performance of different algorithms in detecting sybils in different attacks*


## Algorithms

- [SybilRank](https://github.com/BrightID/BrightID-AntiSybil/blob/master/anti_sybil/algorithms/sybil_rank.py) is a well-known sybil detection algorithm that is based on the assumption that sybils have limited social connections to real users. It relies on the observation that an early-terminated random walk starting from a non-Sybil node in a social network has a higher degree-normalized (divided by the degree) landing probability to land at a non-sybil node than a sybil node.

- [GroupSybilRank](https://github.com/BrightID/BrightID-AntiSybil/blob/master/anti_sybil/algorithms/group_sybil_rank.py) is an enhanced version of the SybilRank algorithm. In this algorithm, a graph is created in which the BrightID groups are nodes  and edges are weighted based on affinity between groups. Then original SybilRank algorithm will be applied to this graph of groups and users get scores from the best group they belong to. This algorithm achieved best results so far in identifying sybils based on modeled [attacks](#attacks) and is being used as official BrightID anti-sybil algorithm.
up edges.

- [WeightedSybilRank](https://github.com/BrightID/BrightID-AntiSybil/blob/master/anti_sybil/algorithms/weighted_sybil_rank.py) is an enhanced version of the SybilRank algorithm that uses the number of common neighbors of the tow connected nodes as weight (trustworthy factor) of the edge.

## Attacks

### Lone Attacks
One attacker attempting to propagate score to the Sybils to verify them by connecting to other nodes and creating groups.
We assumed that an attacker will have one account with a normal or above-average number of direct connections to honest users which they can use for interconnections to sybil accounts.

- One attacker attempts to connect to some of the seed nodes and create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/1ab4a45c55646ab53e358cc667a2ca82b6055de4/anti_sybil/tests/attacks/lone_attacks.py#L6) - [graph](https://explorer.brightid.org/graphs/one_attacker_targeting_seeds.html)

- One attacker attempts to connect to some of the top-ranked honests and create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/1ab4a45c55646ab53e358cc667a2ca82b6055de4/anti_sybil/tests/attacks/lone_attacks.py#L39) - [graph](https://explorer.brightid.org/graphs/one_attacker_targeting_top_nodes.html)

- One attacker attempts to connect to some of the honests and create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/1ab4a45c55646ab53e358cc667a2ca82b6055de4/anti_sybil/tests/attacks/lone_attacks.py#L39) - [graph](https://explorer.brightid.org/graphs/one_attacker_targeting_random_nodes.html)

- One attacker attempts to connect to one of the top-ranked honests and create multiple (duplicate) groups of the sybils. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/1ab4a45c55646ab53e358cc667a2ca82b6055de4/anti_sybil/tests/attacks/lone_attacks.py#L76) - [graph](https://explorer.brightid.org/graphs/one_attacker_group_target_attack.html)

- A seed node attempts to create some sybils nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/dbffa98fdbcfa8ac07309392b13ff22a8af09ad9/anti_sybil/tests/attacks/lone_attacks.py#L116) - [graph](https://explorer.brightid.org/graphs/one_seed_as_attacker.html)

- An honest node attempts to create some sybils nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/dbffa98fdbcfa8ac07309392b13ff22a8af09ad9/anti_sybil/tests/attacks/lone_attacks.py#L116) - [graph](https://explorer.brightid.org/graphs/one_honest_as_attacker.html)

### Collaborative Attacks
Multiple attackers attempting to propagate score to the Sybils to verify them by connecting to other nodes and creating groups.
Attackers are able to connect to each other and each others’ sybil accounts in any way.
We assumed that each attacker will have one account with a normal or above-average number of direct connections to honest users which they can use for interconnections to sybil accounts.
All these attacks can be performed by one or more groups of attackers who collaborate together.

- One or more groups of attackers attempt to connect to some of the seeds and create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/dbffa98fdbcfa8ac07309392b13ff22a8af09ad9/anti_sybil/tests/attacks/collaborative_attacks.py#L6) - [graph for single group](https://explorer.brightid.org/graphs/one_group_targeting_seeds.html) - [graph for multiple groups](https://explorer.brightid.org/graphs/n_groups_targeting_seeds.html)

- One or more groups of attackers attempt to connect to some of the top-ranked honests and create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/dbffa98fdbcfa8ac07309392b13ff22a8af09ad9/anti_sybil/tests/attacks/collaborative_attacks.py#L55) - [graph for single group](https://explorer.brightid.org/graphs/one_group_targeting_top_nodes.html) - [graph for multiple groups](https://explorer.brightid.org/graphs/n_groups_targeting_top_nodes.html)

- One or more groups of attackers attempt to connect to some honest and create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/dbffa98fdbcfa8ac07309392b13ff22a8af09ad9/anti_sybil/tests/attacks/collaborative_attacks.py#L55) - [graph for single group](https://explorer.brightid.org/graphs/one_group_targeting_random_nodes.html) - [graph for multiple groups](https://explorer.brightid.org/graphs/n_groups_targeting_random_nodes.html)


- A group of attackers attempts to connect to some of the top-ranked honests  and create multiple (duplicate) groups of the sybils. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/dbffa98fdbcfa8ac07309392b13ff22a8af09ad9/anti_sybil/tests/attacks/collaborative_attacks.py#L108) - [graph for signle group](https://explorer.brightid.org/graphs/one_group_group_target_attack.html)

- One or more groups of seed nodes attempt to create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/dbffa98fdbcfa8ac07309392b13ff22a8af09ad9/anti_sybil/tests/attacks/collaborative_attacks.py#L157) - [graph for single group](https://explorer.brightid.org/graphs/one_group_of_seeds_as_attacker.html) - [graph for multiple groups](https://explorer.brightid.org/graphs/n_groups_of_seeds_as_attacker.html)

- One or more groups of honest nodes attempt to create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/dbffa98fdbcfa8ac07309392b13ff22a8af09ad9/anti_sybil/tests/attacks/collaborative_attacks.py#L157) - [graph for single group](https://explorer.brightid.org/graphs/one_group_of_honests_as_attacker.html) - [graph for multiple groups](https://explorer.brightid.org/graphs/n_groups_of_honests_as_attacker.html)

### Manual attack
This is a way to manually add new nodes/edges/groups to the BrightID graph and see how different algorithms rank those nodes. You can use `MANUAL_ATTACK_OPTIONS` variable in the [config.py](https://github.com/BrightID/BrightID-AntiSybil/blob/master/anti_sybil/tests/attacks/config.py) file to define the manual attack. This example adds 3 sybil nodes, connect them to `xGUyVQLYV80pajm8QP-9cfHC7xri49V58k02kqTAiUI` as attacker and add them to a new group. [graph for this manual attack](https://explorer.brightid.org/graphs/manual_attack.html)

    MANUAL_ATTACK_OPTIONS = {
        'top': True,
        'connections': [
            ['xGUyVQLYV80pajm8QP-9cfHC7xri49V58k02kqTAiUI', 'sybil1'],
            ['xGUyVQLYV80pajm8QP-9cfHC7xri49V58k02kqTAiUI', 'sybil2'],
            ['xGUyVQLYV80pajm8QP-9cfHC7xri49V58k02kqTAiUI', 'sybil3'],
            ['sybil1', 'sybil2'],
            ['sybil1', 'sybil3'],
        ],
        'groups': {
            'new_group_1': [
                'sybil1',
                'sybil2',
                'sybil3'
            ]
        }
    }


## Install
    $ git clone https://github.com/BrightID/BrightID-AntiSybil.git
    $ cd BrightID-AntiSybil
    $ pip3 install .

## Running Tests

You can configure the algorithms and attacks you want to test by editing the [config.py](https://github.com/BrightID/BrightID-AntiSybil/blob/master/anti_sybil/tests/attacks/config.py) file in `anti_sybil/tests/attacks/config.py` and then run the tests by

    $ python3 anti_sybil/tests/attacks/run.py

The result will contain:
- An interactive graph ([example](https://explorer.brightid.org/graphs/n_groups_targeting_top_nodes.html)) per algorithm/attack that visualize the graph and scores each sybil/attacker/honest node achieved

![](https://explorer.brightid.org/assets/graph.gif)

- A CSV file ([example](https://explorer.brightid.org/assets/result.csv)) that has a column per algorithm/attack and provide following information for each algorithm/attack


|Results                   |GroupSybilRank one group group target attack|
|--------------------------|--------------------------------------------|
|No. Successful Honests    |416                                         |
|Successful Honests Percent|78.1954887218045                            |
|Sybils scored >= %        |0.080091533180778                           |
|Avg Honest - Avg Sybil    |17.4819290581162                            |
|Max Seed                  |100                                         |
|Avg Seed                  |59.6248484848485                            |
|Min Seed                  |31.88                                       |
|Max Honest                |100                                         |
|Avg Honest                |29.3145290581162                            |
|Min Honest                |0                                           |
|Max Attacker              |13.96                                       |
|Avg Attacker              |13.96                                       |
|Min Attacker              |13.96                                       |
|Max Sybil                 |13.96                                       |
|Avg Sybil                 |11.8326                                     |
|Min Sybil                 |5.87                                        |
|Border                    |14                                          |


- A chart to compare effectiveness of different anti-sybil algorithms to detect sybils in different attacks
![](https://explorer.brightid.org/assets/1589538690.png)


## Old Version
The old version of BrightID Anti-Sybil algorithms, tests and documents can be found [here](https://github.com/BrightID/BrightID-AntiSybil/tree/py2).
