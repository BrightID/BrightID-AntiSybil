# BrightID Anti-Sybil
This package provides a framework to evaluate the quality of different anti-sybil [algorithms](#algorithms), by simulating different [attacks](#attacks) to [BrightID's social graph](https://explorer.brightid.org).


![](https://explorer.brightid.org/charts/compare_graph.png)

*Comparing performance of different algorithms in detecting sybils in different attacks in a dense graph*

You can find more details about performance of different algorithms [here](https://github.com/BrightID/BrightID-AntiSybil/wiki/Compare-Yekta-with-other-anti-sybil-algorithms).

## Algorithms

- [SybilRank](https://github.com/BrightID/BrightID-AntiSybil/blob/master/anti_sybil/algorithms/sybil_rank.py) is a well-known sybil detection algorithm that is based on the assumption that sybils have limited social connections to real users. It relies on the observation that an early-terminated random walk starting from a non-Sybil node in a social network has a higher degree-normalized (divided by the degree) landing probability to land at a non-sybil node than a sybil node.

- [GroupSybilRank](https://github.com/BrightID/BrightID-AntiSybil/blob/master/anti_sybil/algorithms/group_sybil_rank.py) is an enhanced version of the SybilRank algorithm. In this algorithm, a graph is created in which the BrightID groups are nodes  and edges are weighted based on affinity between groups. Then original SybilRank algorithm will be applied to this graph of groups and users get scores from the best group they belong to. 

- [WeightedSybilRank](https://github.com/BrightID/BrightID-AntiSybil/blob/master/anti_sybil/algorithms/weighted_sybil_rank.py) is an enhanced version of the SybilRank algorithm that uses the number of common neighbors of the tow connected nodes as weight (trustworthy factor) of the edge.

- [LandingProbability](https://github.com/BrightID/BrightID-AntiSybil/blob/master/anti_sybil/algorithms/landing_probability.py) is the probability of landing of a random walk started from seed nodes on each node of the graph. The result is the same with SybilRank except nodes' ranks are not normalized by dividing them to nodes' degree.

- [NormalizedSybilRank](https://github.com/BrightID/BrightID-AntiSybil/blob/master/anti_sybil/algorithms/normalized_sybil_rank.py) is calculating SybilRank on a normalized graph. To normalize the graph:
  - Each node will be connected to 8 nearest neighbors that are in the same cluster
  - Prevent non-seed nodes from having connections to more than 4 seeds
  - Prevent seeds from having connections to more than 4 nodes in their own clusters and 2 in other clusters

- [ClusterRank](https://github.com/BrightID/BrightID-AntiSybil/blob/master/anti_sybil/algorithms/cluster_rank.py) ranks nodes from 1-5 based on the number of clusters that they have neighbors in.

- [SeednessScore](https://github.com/BrightID/BrightID-AntiSybil/blob/master/anti_sybil/algorithms/seedness_score.py) gives scores to nodes by clustering graph with different resolutions and dividing number of seeds to number of cluster members.

- [Yekta](https://github.com/BrightID/BrightID-AntiSybil/blob/master/anti_sybil/algorithms/yekta.py) rank nodes from 1-5 based on nodes normalized degree. The algorithm decrease the weight for inside edges for the clusters that their number of inside edges are more than average, and then calculate weighted degree for each node.


## Attacks

### Lone Attacks
One attacker attempting to propagate score to the Sybils to verify them by connecting to other nodes and creating groups.
We assumed that an attacker will have one account with a normal or above-average number of direct connections to honest users which they can use for interconnections to sybil accounts.

- One attacker attempts to connect to some of the seed nodes and create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/e73e1e633585896fd56e025bc5846decde20e793/anti_sybil/tests/attacks/lone_attacks.py#L9) - [graph](https://explorer.brightid.org/graphs/one_attacker_targeting_seeds.html)

- One attacker attempts to connect to some of the top-ranked honests and create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/e73e1e633585896fd56e025bc5846decde20e793/anti_sybil/tests/attacks/lone_attacks.py#L38) - [graph](https://explorer.brightid.org/graphs/one_attacker_targeting_top_nodes.html)

- One attacker attempts to connect to some of the honests and create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/e73e1e633585896fd56e025bc5846decde20e793/anti_sybil/tests/attacks/lone_attacks.py#L38) - [graph](https://explorer.brightid.org/graphs/one_attacker_targeting_random_nodes.html)

- One attacker attempts to connect to one of the top-ranked honests and create multiple (duplicate) groups of the sybils. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/e73e1e633585896fd56e025bc5846decde20e793/anti_sybil/tests/attacks/lone_attacks.py#L71) - [graph](https://explorer.brightid.org/graphs/one_attacker_group_target_attack.html)

- A seed node attempts to create some sybils nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/e73e1e633585896fd56e025bc5846decde20e793/anti_sybil/tests/attacks/lone_attacks.py#L105) - [graph](https://explorer.brightid.org/graphs/one_seed_as_attacker.html)

- An honest node attempts to create some sybils nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/e73e1e633585896fd56e025bc5846decde20e793/anti_sybil/tests/attacks/lone_attacks.py#L105) - [graph](https://explorer.brightid.org/graphs/one_honest_as_attacker.html)

### Collaborative Attacks
Multiple attackers attempting to propagate score to the Sybils to verify them by connecting to other nodes and creating groups.
Attackers are able to connect to each other and each others’ sybil accounts in any way.
We assumed that each attacker will have one account with a normal or above-average number of direct connections to honest users which they can use for interconnections to sybil accounts.
All these attacks can be performed by one or more groups of attackers who collaborate together.

- One or more groups of attackers attempt to connect to some of the seeds and create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/e73e1e633585896fd56e025bc5846decde20e793/anti_sybil/tests/attacks/collaborative_attacks.py#L8)
  - target new and low degree seeds: [graph for single group](https://explorer.brightid.org/graphs/one_group_targeting_seeds.html) - [graph for multiple groups](https://explorer.brightid.org/graphs/n_groups_targeting_seeds.html)
  - target active and high degree seeds: [graph for single group](https://explorer.brightid.org/graphs/one_group_targeting_high_degree_seeds.html) - [graph for multiple groups](https://explorer.brightid.org/graphs/n_groups_targeting_high_degree_seeds.html)

- One or more groups of attackers attempt to connect to some of the top-ranked honests and create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/e73e1e633585896fd56e025bc5846decde20e793/anti_sybil/tests/attacks/collaborative_attacks.py#L53) - [graph for single group](https://explorer.brightid.org/graphs/one_group_targeting_top_nodes.html) - [graph for multiple groups](https://explorer.brightid.org/graphs/n_groups_targeting_top_nodes.html)

- One or more groups of attackers attempt to connect to some honest and create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/e73e1e633585896fd56e025bc5846decde20e793/anti_sybil/tests/attacks/collaborative_attacks.py#L53) - [graph for single group](https://explorer.brightid.org/graphs/one_group_targeting_random_nodes.html) - [graph for multiple groups](https://explorer.brightid.org/graphs/n_groups_targeting_random_nodes.html)


- A group of attackers attempts to connect to some of the top-ranked honests  and create multiple (duplicate) groups of the sybils. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/e73e1e633585896fd56e025bc5846decde20e793/anti_sybil/tests/attacks/collaborative_attacks.py#L100) - [graph for signle group](https://explorer.brightid.org/graphs/one_group_group_target_attack.html)

- One or more groups of seed nodes attempt to create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/e73e1e633585896fd56e025bc5846decde20e793/anti_sybil/tests/attacks/collaborative_attacks.py#L142)
  - New and low degree seeds attack: [graph for single group](https://explorer.brightid.org/graphs/one_group_of_seeds_as_attacker.html) - [graph for multiple groups](https://explorer.brightid.org/graphs/n_groups_of_seeds_as_attacker.html)
  - Active and high degree seeds attack: [graph for single group](https://explorer.brightid.org/graphs/one_group_of_high_degree_seeds_as_attacker.html) - [graph for multiple groups](https://explorer.brightid.org/graphs/n_groups_of_high_degree_seeds_as_attacker.html)
  - Seeds disconnected from non-sybil nodes attack: [graph for single group](https://explorer.brightid.org/graphs/one_group_of_disconnected_seeds_as_attacker.html) - [graph for multiple groups](https://explorer.brightid.org/graphs/n_groups_of_disconnected_seeds_as_attacker.html)

- One or more groups of honest nodes attempt to create some sybil nodes. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/e73e1e633585896fd56e025bc5846decde20e793/anti_sybil/tests/attacks/collaborative_attacks.py#L142) - [graph for single group](https://explorer.brightid.org/graphs/one_group_of_honests_as_attacker.html) - [graph for multiple groups](https://explorer.brightid.org/graphs/n_groups_of_honests_as_attacker.html)

- A group of seed nodes attempt to create some sybil nodes by creating a group per sybil node and all seed nodes join that group. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/e73e1e633585896fd56e025bc5846decde20e793/anti_sybil/tests/attacks/collaborative_attacks.py#L232) - [graph](https://explorer.brightid.org/graphs/many_small_groups_attack.html)

- A group of seed nodes attempt to create multiple clusters and connect sybils in each cluster to random sybils in other clusters. [implementation](https://github.com/BrightID/BrightID-AntiSybil/blob/e73e1e633585896fd56e025bc5846decde20e793/anti_sybil/tests/attacks/collaborative_attacks.py#L185) - [graph](https://explorer.brightid.org/graphs/multi_cluster_attack.html)

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
![](https://explorer.brightid.org/charts/compare_graph.png)


## Old Version
The old version of BrightID Anti-Sybil algorithms, tests and documents can be found [here](https://github.com/BrightID/BrightID-AntiSybil/tree/py2).
