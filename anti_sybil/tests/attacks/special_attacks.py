import anti_sybil.algorithms as algorithms
from anti_sybil.utils import Node
from anti_sybil.utils import *
import random
import time


# the stupid sybil attack
def stupid_sybil(graph, options):
    sybils = []
    attackers = [n for n in graph if n.rank > 0]
    attackers.sort(key=lambda n: n.rank, reverse=True)
    for attacker in attackers:
        attacker.groups['stupid_sybil'] = 'NonSeed'
        for i in range(2):
            groups = {'stupid_sybil': 'NonSeed'}
            sybil = Node('stupid_sybil_{}'.format(i), 'Sybil', groups=groups, created_at=int(time.time() * 1000))
            sybils.append(sybil)
            graph.add_edge(attacker, sybil)
        reset_ranks(graph)
        ranker = algorithms.GroupSybilRank(graph)
        ranker.rank()
        border = max([s.rank for s in sybils])
        if border:
            break
        graph.remove_nodes_from(sybils)
        del attacker.groups['stupid_sybil']
    return graph


def many_small_groups_attack(graph, options):
    sybils = []
    attackers = [n for n in graph if n.node_type == 'Seed']
    attackers.sort(key=lambda n: n.rank, reverse=False)
    attackers = attackers[:options['num_attacker']]

    for i in range(options['num_sybils']):
        groups = {'sg-{}'.format(i): 'NonSeed'}
        sybil = Node('s-{}'.format(i), 'Sybil', groups=groups, created_at=int(time.time() * 1000))
        sybils.append(sybil)
        for attacker in attackers:
            graph.add_edge(sybil, attacker)
            attacker.groups.update(groups)

    # connecting the sybil nodes together
    for i in range(options['stitches']):
        s, t = random.sample(sybils, 2)
        graph.add_edge(s, t)

    return graph
