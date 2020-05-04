from anti_sybil.graphs.node import Node
from anti_sybil import algorithms
import matplotlib.pyplot as plt
from anti_sybil.utils import *
import random
import copy
import os

OUTPUT_FOLDER = './outputs/collaborative_attacks/'

SYBIL_RANK = True
SYBIL_GROUP_RANK = True
INTRA_GROUP_WEIGHT = True
GROUP_MERGE = False

outputs = []
charts = {'SR': [], 'SGR': [], 'IGW': [], 'GM': []}

algorithm_options = {
    'accumulative': False,
    'nonlinear_distribution': False,
    'group_edge_weight': 20,
    'thresholds': [.36, .24, .18, .12, .06, .04, .02, .01, .005, .004, .003, .002, .0015, .001, .0005, 0]
}


# the attackers connect to the seeds
def targeting_seeds(
        graph,
        num_attacker,
        num_seeds,
        num_sybils,
        one_group=True,
        stitches=0):
    edges = []
    sybils = []
    attackers = []
    seeds = [n.name for n in graph.nodes if n.node_type == 'Seed']
    nodes_dic = {node.name: node for node in graph.nodes}

    # making attacker nodes
    for i in range(num_attacker):
        groups = set(['collaborative_attack']) if one_group else set(
            ['collaborative_attack_{}'.format(i)])
        nodes_dic['attacker_{}'.format(i)] = Node(
            'attacker_{}'.format(i), 'Attacker', groups=groups)
        attackers.append('attacker_{}'.format(i))

    # connecting attacker nodes to the seed nodes
    for attacker in attackers:
        for seed in seeds[:num_seeds]:
            edges.append(
                (nodes_dic[attacker], nodes_dic[seed]))

    # making sybil nodes and connecting them to attacker nodes
    num_groups = 1 if one_group else num_attacker
    for i in range(num_groups):
        for j in range(num_sybils // num_groups):
            groups = set(['collaborative_attack']) if one_group else set(
                ['collaborative_attack_{}'.format(i)])
            nodes_dic['s-{0}-{1}'.format(i, j)] = Node(
                's-{0}-{1}'.format(i, j), 'Sybil', groups=groups)
            sybils.append('s-{0}-{1}'.format(i, j))
            if one_group:
                for attacker in attackers:
                    edges.append(
                        (nodes_dic['s-{0}-{1}'.format(i, j)], nodes_dic[attacker]))
            else:
                edges.append(
                    (nodes_dic['s-{0}-{1}'.format(i, j)], nodes_dic[attackers[i]]))

    # connecting sybil nodes together
    for i in range(stitches):
        edges.append((nodes_dic[random.choice(sybils)],
                      nodes_dic[random.choice(sybils)]))

    # updating graph
    graph.add_edges_from(edges)
    return graph


# the attackers connect to the honests
def targeting_honest(
        graph,
        num_attacker,
        num_honests,
        num_sybils,
        one_group=True,
        top=True,
        stitches=0):
    edges = []
    sybils = []
    attackers = []
    honests = [n for n in graph.nodes if n.rank > 0]
    if top:
        honests = sorted(honests, key=lambda n: n.rank, reverse=True)
    else:
        random.shuffle(honests)
    nodes_dic = {node.name: node for node in graph.nodes}

    # making attacker nodes
    for i in range(num_attacker):
        groups = set(['collaborative_attack']) if one_group else set(
            ['collaborative_attack_{}'.format(i)])
        nodes_dic['attacker_{}'.format(i)] = Node(
            'attacker_{}'.format(i), 'Attacker', groups=groups)
        attackers.append('attacker_{}'.format(i))

    # connecting attacker nodes to the honest nodes
    for attacker in attackers:
        for honest in honests[:num_honests]:
            edges.append(
                (nodes_dic[attacker], nodes_dic[honest.name]))

    # making sybil nodes and connecting them to attacker nodes
    num_groups = 1 if one_group else num_attacker
    for i in range(num_groups):
        for j in range(num_sybils // num_groups):
            groups = set(['collaborative_attack']) if one_group else set(
                ['collaborative_attack_{}'.format(i)])
            nodes_dic['s-{0}-{1}'.format(i, j)] = Node(
                's-{0}-{1}'.format(i, j), 'Sybil', groups=groups)
            sybils.append('s-{0}-{1}'.format(i, j))
            if one_group:
                for attacker in attackers:
                    edges.append(
                        (nodes_dic['s-{0}-{1}'.format(i, j)], nodes_dic[attacker]))
            else:
                edges.append(
                    (nodes_dic['s-{0}-{1}'.format(i, j)], nodes_dic[attackers[i]]))

    # connecting sybil nodes together
    for i in range(stitches):
        edges.append((nodes_dic[random.choice(sybils)],
                      nodes_dic[random.choice(sybils)]))

    # updating graph
    graph.add_edges_from(edges)
    return graph


# the attackers connect to the top-ranked honests and propagate the score by creating multiple groups
def group_attack(
        graph,
        num_attacker,
        num_honests,
        num_sybils,
        num_groups,
        stitches):
    edges = []
    sybils = []
    attackers = []
    honests = sorted([n for n in graph.nodes if n.rank > 0],
                     key=lambda n: n.rank, reverse=True)
    nodes_dic = {node.name: node for node in graph.nodes}

    # making attacker nodes
    for i in range(num_attacker):
        nodes_dic['attacker_{}'.format(i)] = Node('attacker_{}'.format(
            i), 'Attacker', groups=set(['collaborative_attack']))
        attackers.append('attacker_{}'.format(i))

    # connecting attacker nodes to the honest nodes
    for attacker in attackers:
        for honest in honests[:num_honests]:
            edges.append(
                (nodes_dic[attacker], nodes_dic[honest.name]))

    # making sybil nodes and connecting them to the attacker nodes
    for i in range(num_groups):
        nodes_dic['s-{0}'.format(i)] = Node(
            's-{0}'.format(i), 'Sybil', groups=set(['collaborative_attack']))
        sybils.append('s-{0}'.format(i))
        for attacker in attackers:
            edges.append(
                (nodes_dic['s-{0}'.format(i)], nodes_dic[attacker]))

    # making sybil groups
    for i in range(num_groups):
        for attacker in attackers:
            nodes_dic[attacker].groups.add('collaborative_attack_{}'.format(i))
        nodes_dic[random.choice(sybils)].groups.add(
            'collaborative_attack_{}'.format(i))
        nodes_dic[random.choice(sybils)].groups.add(
            'collaborative_attack_{}'.format(i))

    # connecting sybil nodes together
    for i in range(stitches):
        edges.append((nodes_dic[random.choice(sybils)],
                      nodes_dic[random.choice(sybils)]))

    # updating graph
    graph.add_edges_from(edges)
    return graph


# a group of seeds or honests as attackers
def collsion_attack(
        graph,
        attacker_type,
        num_attacker,
        num_sybils,
        one_group=True,
        stitches=0):
    edges = []
    sybils = []
    if attacker_type == 'Seed':
        attackers = sorted([n for n in graph.nodes if n.node_type == 'Seed'],
                           key=lambda n: n.rank, reverse=True)[:num_attacker]
    elif attacker_type == 'Honest':
        attackers = sorted([n for n in graph.nodes if n.node_type != 'Seed'],
                           key=lambda n: n.rank, reverse=True)[:num_attacker]
    nodes_dic = {node.name: node for node in graph.nodes}

    # making sybil nodes and connecting them to attacker nodes
    num_groups = 1 if one_group else num_attacker
    for i in range(num_groups):
        for j in range(num_sybils // num_groups):
            groups = set(['collaborative_attack']) if one_group else set(
                ['collaborative_attack_{}'.format(i)])
            nodes_dic['s-{0}-{1}'.format(i, j)] = Node(
                's-{0}-{1}'.format(i, j), 'Sybil', groups=groups)
            sybils.append('s-{0}-{1}'.format(i, j))
            if one_group:
                for attacker in attackers:
                    edges.append(
                        (nodes_dic['s-{0}-{1}'.format(i, j)], nodes_dic[attacker.name]))
            else:
                edges.append(
                    (nodes_dic['s-{0}-{1}'.format(i, j)], nodes_dic[attackers[i].name]))

    # connecting sybil nodes together
    for i in range(stitches):
        edges.append((nodes_dic[random.choice(sybils)],
                      nodes_dic[random.choice(sybils)]))

    # updating graph
    graph.add_edges_from(edges)
    return graph


def successful_honests(graph):
    honests = []
    sybils = []
    for node in graph.nodes:
        if node.node_type in ['Sybil', 'Non Bridge Sybil', 'Bridge Sybil']:
            sybils.append(node.rank)
        if node.node_type in ['Seed', 'Honest'] and node.rank:  # ?Attacker
            honests.append(node.rank)
    honests.sort()
    avg_sybils = sum(sybils) / len(sybils)
    return (1 - (bisect(honests, avg_sybils) / len(honests))) * 100


def plot():
    fig, ax = plt.subplots()
    for i, chart in enumerate(charts):
        if not charts[chart]:
            continue
        ax.plot(
            [p[0] for p in charts[chart]],
            [p[1] for p in charts[chart]],
            'go--',
            color='C{}'.format(i),
            label='= {}'.format(chart),
        )
    ax.legend()
    plt.title('Collaborative Attacks')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, 'algorithms.png'))


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
        charts['SR'].append([file_name, successful_honests(graph)])

    if SYBIL_GROUP_RANK:
        reset_ranks(graph)
        ranker = algorithms.SybilGroupRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'SybilGroupRank\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'SGR_{}.html'.format(file_name)))
        charts['SGR'].append([file_name, successful_honests(graph)])

    if INTRA_GROUP_WEIGHT:
        reset_ranks(graph)
        ranker = algorithms.GroupSybilRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'IntraGroupWeight\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'IGW_{}.html'.format(file_name)))
        charts['IGW'].append([file_name, successful_honests(graph)])

    if GROUP_MERGE:
        reset_ranks(graph)
        ranker = algorithms.GroupMergingRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'GroupMerge\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'GM_{}.html'.format(file_name)))
        charts['GM'].append([file_name, successful_honests(graph)])


def main():
    global outputs

    # making the graph and ranking nodes
    graph = graphs.generators.brightid_backup.generate({
        'file_path': os.path.join(OUTPUT_FOLDER, 'temp')
    })
    ranker = algorithms.SybilGroupRank(graph, algorithm_options)
    ranker.rank()

    # attackers targeting seeds
    _graph = targeting_seeds(copy.deepcopy(graph), 3, 3, 9, True, 10)
    tests(_graph, 'targeting seeds', 'targeting_seeds')

    # attackers targeting top-ranked honests
    _graph = targeting_honest(copy.deepcopy(graph), 3, 3, 9, False, True, 0)
    tests(_graph, 'targeting top nodes', 'targeting_top_nodes')

    # attackers targeting random honests
    _graph = targeting_honest(copy.deepcopy(graph), 3, 3, 9, False, False, 0)
    tests(_graph, 'random', 'random')

    # attackers targeting top-ranked honests (by creating groups)
    _graph = group_attack(copy.deepcopy(graph), 5, 5, 10, 20, 100)
    tests(_graph, 'group target attack', 'group_target_attack')

    # a group of seeds as attackers
    _graph = collsion_attack(copy.deepcopy(graph), 'Seed', 5, 10, True, 10)
    tests(_graph, 'seed node attack', 'seed_node_attack')

    # a group of honests as attackers
    _graph = collsion_attack(copy.deepcopy(graph), 'Honest', 5, 10, False, 0)
    tests(_graph, 'honest node attack', 'honest_node_attack')

    plot()
    write_output_file(outputs, os.path.join(OUTPUT_FOLDER, 'result.csv'))


if __name__ == '__main__':
    main()
