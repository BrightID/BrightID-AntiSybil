import collaborative_attacks as collaborative
from anti_sybil import algorithms
import matplotlib.pyplot as plt
from anti_sybil.utils import *
import lone_attacks as lone
import multiprocessing
import copy
import time
import os

manager = multiprocessing.Manager()

OUTPUT_FOLDER = './outputs/all_attacks/'

SYBIL_RANK = True
SYBIL_GROUP_RANK = True
INTRA_GROUP_WEIGHT = True
GROUP_MERGE = False

outputs = manager.list()
charts = manager.dict({'SR': manager.dict(), 'SGR': manager.dict(
), 'IGW': manager.dict(), 'GM': manager.dict()})

algorithm_options = {
    'accumulative': False,
    'nonlinear_distribution': False,
    'group_edge_weight': 20,
    'thresholds': [.36, .24, .18, .12, .06, .04, .02, .01, .005, .004, .003, .002, .0015, .001, .0005, 0]
}


def tests(graph, description, file_name, outputs, charts):
    if SYBIL_RANK:
        reset_ranks(graph)
        ranker = algorithms.SybilRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'SybilRank\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'SR_{}.html'.format(file_name)))
        charts['SR'][file_name] = successful_honests(graph)

    if SYBIL_GROUP_RANK:
        reset_ranks(graph)
        ranker = algorithms.SybilGroupRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'SybilGroupRank\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'SGR_{}.html'.format(file_name)))
        charts['SGR'][file_name] = successful_honests(graph)

    if INTRA_GROUP_WEIGHT:
        reset_ranks(graph)
        ranker = algorithms.GroupSybilRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'IntraGroupWeight\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'IGW_{}.html'.format(file_name)))
        charts['IGW'][file_name] = successful_honests(graph)

    if GROUP_MERGE:
        reset_ranks(graph)
        ranker = algorithms.GroupMergingRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'GroupMerge\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'GM_{}.html'.format(file_name)))
        charts['GM'][file_name] = successful_honests(graph)


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
    x_ax = [
        'lone_targeting_seeds', 'lone_targeting_top_nodes', 'lone_random', 'lone_group_target_attack', 'lone_seed_node_attack', 'lone_honest_node_attack',
        'one_group_targeting_seeds', 'one_group_targeting_top_nodes', 'one_group_random', 'one_group_group_target_attack', 'one_group_seed_node_attack', 'one_group_honest_node_attack',
        'some_groups_targeting_seeds', 'some_groups_targeting_top_nodes', 'some_groups_random', 'some_groups_seed_node_attack', 'some_groups_honest_node_attack'
    ]
    for i, chart in enumerate(charts):
        if not charts[chart]:
            continue
        ax.plot(
            x_ax,
            [charts[chart][p] for p in x_ax],
            'go--',
            color='C{}'.format(i),
            label='= {}'.format(chart),
        )
    ax.legend()
    plt.title('Attacks')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, 'algorithms.png'))


def main():
    global outputs, charts

    # making the graph and ranking nodes
    graph = graphs.generators.brightid_backup.generate({
        'file_path': os.path.join(OUTPUT_FOLDER, 'temp')
    })
    ranker = algorithms.SybilGroupRank(graph, algorithm_options)
    ranker.rank()

    inputs = []

    # one attacker targeting seeds
    _graph = lone.targeting_seeds(copy.deepcopy(graph), 5, 50)
    inputs.append([_graph, 'targeting seeds',
                   'lone_targeting_seeds', outputs, charts])

    # one attacker targeting top-ranked honests
    _graph = lone.targeting_honest(copy.deepcopy(graph), 5, 50, True)
    inputs.append([_graph, 'targeting top nodes',
                   'lone_targeting_top_nodes', outputs, charts])

    # one attacker targeting random honests
    _graph = lone.targeting_honest(copy.deepcopy(graph), 5, 50, False)
    inputs.append([_graph, 'random', 'lone_random', outputs, charts])

    # one attacker targeting a top-ranked honest (by creating groups)
    _graph = lone.group_attack(copy.deepcopy(graph), 50, 50, 200)
    inputs.append([_graph, 'group target attack',
                   'lone_group_target_attack', outputs, charts])

    # one seed as an attacker
    _graph = lone.collsion_attack(copy.deepcopy(graph), 'Seed', 50, 0)
    inputs.append([_graph, 'seed node attack',
                   'lone_seed_node_attack', outputs, charts])

    # one honest as an attacker
    _graph = lone.collsion_attack(copy.deepcopy(graph), 'Honest', 50, 0)
    inputs.append([_graph, 'honest node attack',
                   'lone_honest_node_attack', outputs, charts])

    # A team of attackers
    # a team of attackers targeting seeds
    _graph = collaborative.targeting_seeds(
        copy.deepcopy(graph), 3, 3, 9, True, 10)
    inputs.append([_graph, 'targeting seeds',
                   'one_group_targeting_seeds', outputs, charts])

    # a team of attackers targeting top-ranked honests
    _graph = collaborative.targeting_honest(
        copy.deepcopy(graph), 3, 3, 9, True, True, 0)
    inputs.append([_graph, 'targeting top nodes',
                   'one_group_targeting_top_nodes', outputs, charts])

    # a team of attackers targeting random honests
    _graph = collaborative.targeting_honest(
        copy.deepcopy(graph), 3, 3, 9, True, False, 0)
    inputs.append([_graph, 'random', 'one_group_random', outputs, charts])

    # a team of attackers targeting top-ranked honests (by creating groups)
    _graph = collaborative.group_attack(
        copy.deepcopy(graph), 5, 5, 10, 20, 100)
    inputs.append([_graph, 'group target attack',
                   'one_group_group_target_attack', outputs, charts])

    # a team of seeds as attackers
    _graph = collaborative.collsion_attack(
        copy.deepcopy(graph), 'Seed', 5, 10, True, 10)
    inputs.append([_graph, 'seed node attack',
                   'one_group_seed_node_attack', outputs, charts])

    # a team of honests as attackers
    _graph = collaborative.collsion_attack(
        copy.deepcopy(graph), 'Honest', 5, 10, True, 0)
    inputs.append([_graph, 'honest node attack',
                   'one_group_honest_node_attack', outputs, charts])

    # some teams of attackers
    # some teams of attackers targeting seeds
    _graph = collaborative.targeting_seeds(
        copy.deepcopy(graph), 3, 3, 9, False, 10)
    inputs.append([_graph, 'targeting seeds',
                   'some_groups_targeting_seeds', outputs, charts])

    # some teams of attackers targeting top-ranked honests
    _graph = collaborative.targeting_honest(
        copy.deepcopy(graph), 3, 3, 9, False, True, 0)
    inputs.append([_graph, 'targeting top nodes',
                   'some_groups_targeting_top_nodes', outputs, charts])

    # some teams of attackers targeting random honests
    _graph = collaborative.targeting_honest(
        copy.deepcopy(graph), 3, 3, 9, False, False, 0)
    inputs.append([_graph, 'random', 'some_groups_random', outputs, charts])

    # some teams of seeds as attackers
    _graph = collaborative.collsion_attack(
        copy.deepcopy(graph), 'Seed', 5, 10, False, 10)
    inputs.append([_graph, 'seed node attack',
                   'some_groups_seed_node_attack', outputs, charts])

    # some teams of honests as attackers
    _graph = collaborative.collsion_attack(
        copy.deepcopy(graph), 'Honest', 5, 10, False, 0)
    inputs.append([_graph, 'honest node attack',
                   'some_groups_honest_node_attack', outputs, charts])

    with multiprocessing.Pool() as pool:
        pool.starmap(tests, inputs)

    plot()
    write_output_file(outputs, os.path.join(OUTPUT_FOLDER, 'result.csv'))


if __name__ == '__main__':
    t1 = time.time()
    main()
    print('TIME:', int(time.time() - t1))
