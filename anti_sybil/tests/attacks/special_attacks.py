import anti_sybil.algorithms as algorithms
from anti_sybil.utils import Node
from anti_sybil.utils import *
import random


# the stupid sybil attack
def stupid_sybil(graph, options):
    honests = [n for n in graph.nodes if n.rank > 0]
    sybils = []
    attackers = sorted(honests, key=lambda n: n.rank, reverse=True)
    nodes_dic = {node.name: node for node in graph.nodes}
    for attacker in attackers:
        attacker.groups['stupid_sybil'] = 'NonSeed'
        for i in range(2):
            nodes_dic['s_{}'.format(i)] = Node(
                'stupid_sybil_{}'.format(i), 'Sybil', {'stupid_sybil': 'NonSeed'})
            graph.add_edge(attacker, nodes_dic['s_{}'.format(i)])
            sybils.append('s_{}'.format(i))
        reset_ranks(graph)
        ranker = algorithms.GroupSybilRank(graph)
        ranker.rank()
        border = max([nodes_dic[s].raw_rank for s in sybils])
        if border:
            break
        graph.remove_nodes_from([nodes_dic[s] for s in sybils])
        del attacker.groups['stupid_sybil']
    return graph


def many_small_groups_attack(graph, options):
    edges = []
    sybils = []
    attackers = sorted([n for n in graph.nodes if n.node_type == 'Seed'], key=lambda n: n.rank, reverse=False)[
        :options['num_attacker']]
    nodes_dic = {node.name: node for node in graph.nodes}

    for i in range(options['num_sybils']):
        groups = {'sg-{}'.format(i): 'NonSeed'}
        nodes_dic['s-{}'.format(i)] = Node(
            's-{}'.format(i), 'Sybil', groups=groups)
        sybils.append('s-{}'.format(i))
        for attacker in attackers:
            edges.append(
                (nodes_dic['s-{}'.format(i)], nodes_dic[attacker.name]))
            attacker.groups['sg-{}'.format(i)] = 'NonSeed'

    # connecting sybil nodes together
    for i in range(options['stitches']):
        edges.append((nodes_dic[random.choice(sybils)],
                      nodes_dic[random.choice(sybils)]))

    # updating graph
    graph.add_edges_from(edges)
    return graph
