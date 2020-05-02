import os
import random
from anti_sybil import algorithms
from anti_sybil.graphs.node import Node
from anti_sybil.utils import *
import copy

OUTPUT_FOLDER = './outputs/single_attacker/'

SYBIL_RANK = True
SYBIL_GROUP_RANK = True
INTRA_GROUP_WEIGHT = True
GROUP_MERGE = False

outputs = []

algorithm_options = {
    'accumulative': False,
    'nonlinear_distribution': True,
    'group_edge_weight': 20,
    'thresholds': [.36, .24, .18, .12, .06, .04, .02, .01, .005, .004, .003, .002, .0015, .001, .0005, 0]
}


# The attacker connects to the n seeds
# Create m Sybil nodes
def targeting_seeds(graph, num_seeds, num_sybils, stitches=0):
    edges = []
    sybils = []
    seeds = [n.name for n in graph.nodes if n.node_type == 'Seed']
    nodes_dic = {node.name: node for node in graph.nodes}

    # making attacker node
    nodes_dic['attacker'] = Node(
        'attacker', 'Attacker', groups=set(['target_attack']))

    # connecting attackers to n seeds
    for i in range(num_seeds):
        edges.append(
            (nodes_dic['attacker'], nodes_dic[random.choice(seeds)]))

    # making sybils and connecting them to attackers
    for i in range(num_sybils):
        nodes_dic['s-{0}'.format(i)] = Node(
            's-{0}'.format(i), 'Sybil', groups=set(['target_attack']))
        sybils.append('s-{0}'.format(i))
        edges.append((nodes_dic['s-{0}'.format(i)], nodes_dic['attacker']))

    # connecting sybils together
    for i in range(stitches):
        edges.append((nodes_dic[random.choice(sybils)],
                      nodes_dic[random.choice(sybils)]))

    # updating graph
    graph.add_edges_from(edges)
    return graph


# The attacker connects to the honests
# Create m Sybil nodes
def targeting_honest(graph, num_honests, num_sybils, top=True, stitches=0):
    edges = []
    sybils = []
    honests = [n for n in graph.nodes if n.rank > 0]
    if top:
        honests = sorted(honests, key=lambda n: n.rank, reverse=True)
    else:
        random.shuffle(honests)
    nodes_dic = {node.name: node for node in graph.nodes}

    # making attacker node
    nodes_dic['attacker'] = Node(
        'attacker', 'Attacker', groups=set(['target_attack']))

    # connecting attackers to top ranked nodes
    for top in honests[:num_honests]:
        edges.append(
            (nodes_dic['attacker'], nodes_dic[top.name]))

    # making sybils and connecting them to attackers
    for i in range(num_sybils):
        nodes_dic['s-{0}'.format(i)] = Node(
            's-{0}'.format(i), 'Sybil', groups=set(['target_attack']))
        sybils.append('s-{0}'.format(i))
        edges.append((nodes_dic['s-{0}'.format(i)], nodes_dic['attacker']))

    # connecting sybils together
    for i in range(stitches):
        edges.append((nodes_dic[random.choice(sybils)],
                      nodes_dic[random.choice(sybils)]))

    # updating graph
    graph.add_edges_from(edges)
    return graph


# The attacker connects to one top honest and propagates the score by creating multiple groups
# Create m Sybil nodes
def group_attack(graph, num_sybils, num_groups, stitches):
    edges = []
    sybils = []
    target = sorted([n for n in graph.nodes],
                    key=lambda n: n.rank, reverse=True)[0]
    nodes_dic = {node.name: node for node in graph.nodes}

    # making attacker node
    nodes_dic['attacker'] = Node(
        'attacker', 'Attacker', groups=set(['target_attack']))

    # connecting attacker to a top ranked node
    edges.append((nodes_dic['attacker'], nodes_dic[target.name]))

    # making sybils and connecting them to attackers
    for i in range(num_sybils):
        nodes_dic['s-{0}'.format(i)] = Node(
            's-{0}'.format(i), 'Sybil', groups=set(['target_attack']))
        sybils.append('s-{0}'.format(i))
        edges.append((nodes_dic['s-{0}'.format(i)], nodes_dic['attacker']))

    # connecting sybils together
    for i in range(stitches):
        edges.append((nodes_dic[random.choice(sybils)],
                      nodes_dic[random.choice(sybils)]))

    # making sybils groups
    for i in range(num_groups):
        nodes_dic['attacker'].groups.add('target_attack_{}'.format(i))
        nodes_dic[random.choice(sybils)].groups.add(
            'target_attack_{}'.format(i))
        nodes_dic[random.choice(sybils)].groups.add(
            'target_attack_{}'.format(i))

    # updating graph
    graph.add_edges_from(edges)
    return graph


def tests(graph, description, file_name):
    global outputs

    if SYBIL_RANK:
        reset_ranks(graph)
        ranker = algorithms.SybilRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'SybilRank\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'SR_{}.html'.format(file_name)))

    if SYBIL_GROUP_RANK:
        reset_ranks(graph)
        ranker = algorithms.SybilGroupRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'SybilGroupRank\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'SGR_{}.html'.format(file_name)))

    if INTRA_GROUP_WEIGHT:
        reset_ranks(graph)
        ranker = algorithms.GroupSybilRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'IntraGroupWeight\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'IGW_{}.html'.format(file_name)))

    if GROUP_MERGE:
        reset_ranks(graph)
        ranker = algorithms.GroupMergingRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'GroupMerge\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'GM_{}.html'.format(file_name)))


def main():
    global outputs

    # making athe graph and ranking nodes
    graph = graphs.generators.brightid_backup.generate({
        'file_path': os.path.join(OUTPUT_FOLDER, 'temp')
    })
    ranker = algorithms.SybilGroupRank(graph, algorithm_options)
    ranker.rank()

    # targeting seeds
    _graph = targeting_seeds(copy.deepcopy(graph), 5, 50)
    tests(_graph, 'targeting seeds', 'targeting_seeds')

    # targeting top ranked nodes
    _graph = targeting_honest(copy.deepcopy(graph), 5, 50, True)
    tests(_graph, 'targeting top nodes', 'targeting_top_nodes')

    # random attack
    _graph = targeting_honest(copy.deepcopy(graph), 5, 50, False)
    tests(_graph, 'random', 'random')

    # group target attack
    _graph = group_attack(copy.deepcopy(graph), 50, 100, 200)
    tests(_graph, 'group target attack', 'group_target_attack')

    write_output_file(outputs, os.path.join(OUTPUT_FOLDER, 'result.csv'))


if __name__ == '__main__':
    main()
