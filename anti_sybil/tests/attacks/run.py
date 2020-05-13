import matplotlib.pyplot as plt
import multiprocessing
import requests
import copy
import time
import os
import collaborative_attacks as collaborative
import lone_attacks as lone
from anti_sybil import algorithms
from anti_sybil.utils import *
from config import *

x_axis = []

manager = multiprocessing.Manager()
outputs = manager.list()
charts = manager.dict({'SR': manager.dict(), 'SGR1': manager.dict(), 'SGR2': manager.dict(
), 'SGR': manager.dict(), 'IGW': manager.dict(), 'GM': manager.dict(), 'WSR': manager.dict()})

algorithm_options = {
    'accumulative': ACCUMULATIVE,
    'nonlinear_distribution': NONLINEAR_DISTRIBUTION,
    'group_edge_weight': GROUP_EDGE_WEIGHT,
    'thresholds': THRESHOLDS
}


def generate_graph():
    rar_addr = os.path.join(INPUT_FOLDER, 'brightid.tar.gz')
    zip_addr = os.path.join(INPUT_FOLDER, 'brightid.zip')
    if not os.path.exists(os.path.join(INPUT_FOLDER, 'brightid.zip')):
        if not os.path.exists(INPUT_FOLDER):
            os.makedirs(INPUT_FOLDER)
        backup = requests.get(BACKUP_URL)
        with open(rar_addr, 'wb') as f:
            f.write(backup.content)
        tar_to_zip(rar_addr, zip_addr)
    json_graph = from_dump(zip_addr)
    graph = from_json(json_graph)
    return graph


def tests(graph, description, file_name, outputs, charts):
    if SYBIL_RANK:
        reset_ranks(graph)
        ranker = algorithms.SybilRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'SybilRank\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'SR_{}.html'.format(file_name)))
        charts['SR'][file_name] = successful_honests(graph, description, 'sybil rank')

    if SYBIL_GROUP_RANK_V1:
        reset_ranks(graph)
        ranker = algorithms.V1SybilGroupRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'V1 SybilGroupRank\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'SGR1_{}.html'.format(file_name)))
        charts['SGR1'][file_name] = successful_honests(graph, description, 'sybil group rank v1')

    if SYBIL_GROUP_RANK:
        reset_ranks(graph)
        ranker = algorithms.SybilGroupRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'SybilGroupRank\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'SGR_{}.html'.format(file_name)))
        charts['SGR'][file_name] = successful_honests(graph, description, 'sybil group rank')

    if INTRA_GROUP_WEIGHT:
        reset_ranks(graph)
        ranker = algorithms.GroupSybilRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'IntraGroupWeight\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'IGW_{}.html'.format(file_name)))
        charts['IGW'][file_name] = successful_honests(graph, description, 'intra group weight')

    if GROUP_MERGE:
        reset_ranks(graph)
        ranker = algorithms.GroupMergingRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'GroupMerge\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'GM_{}.html'.format(file_name)))
        charts['GM'][file_name] = successful_honests(graph, description, 'group merge')

    if WEIGHTED_SYBIL_RANK:
        reset_ranks(graph)
        ranker = algorithms.WeightedSybilRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'WeightedSybilRank\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'WSR_{}.html'.format(file_name)))
        charts['WSR'][file_name] = successful_honests(graph, description, 'weighted sybil rank')


def successful_honests(graph, description, algorithm):
    honests = []
    sybils = []
    for node in graph.nodes:
        if node.node_type in ['Sybil', 'Non Bridge Sybil', 'Bridge Sybil']:
            sybils.append(node.rank)
        if node.node_type in ['Seed', 'Honest'] and node.rank > 0:
            honests.append(node.rank)
    avg_sybils = sum(sybils) / len(sybils)
    verified = len([h for h in honests if h > avg_sybils])
    percent = verified / len(honests) * 100
    print('{}\nAlgorithm:\t{}'.format(description, algorithm))
    print('No. honests:\t{}\nNo. sybils:\t{}\nNo. verified:\t{}\nPercent:\t{}\n\n'.format(len(honests), len(sybils), verified, percent))
    return percent


def plot():
    fig, ax = plt.subplots()
    for i, chart in enumerate(charts):
        if not charts[chart]:
            continue
        ax.plot(
            x_axis,
            [charts[chart][p] for p in x_axis],
            'go--',
            color='C{}'.format(i * 2),
            label='= {}'.format(chart),
        )
    ax.legend()
    plt.title('Targets:{} Sybils:{} Attackers:{} Stitches:{} Groups:{}'.format(
        N_TARGETS, N_SYBILS, N_ATTACKERS, N_STITCHES, N_GROUPS))
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, str(int(time.time())) + '.png'))


def main():
    global outputs, charts

    # making the graph and ranking nodes
    graph = generate_graph()
    ranker = algorithms.SybilGroupRank(graph, algorithm_options)
    ranker.rank()

    inputs = []

    if ONE_ATTACKER_TARGETING_SEEDS:
        _graph = lone.targeting_seeds(copy.deepcopy(
            graph), N_TARGETS, N_SYBILS, stitches=N_STITCHES)
        inputs.append([_graph, 'one attacker targeting seeds',
                       'one_attacker_targeting_seeds', outputs, charts])
        x_axis.append('one_attacker_targeting_seeds')

    if ONE_ATTACKER_TARGETING_TOP_NODES:
        _graph = lone.targeting_honest(copy.deepcopy(
            graph), N_TARGETS, N_SYBILS, top=True, stitches=N_STITCHES)
        inputs.append([_graph, 'one attacker targeting top nodes',
                       'one_attacker_targeting_top_nodes', outputs, charts])
        x_axis.append('one_attacker_targeting_top_nodes')

    if ONE_ATTACKER_TARGETING_RANDOM_NODES:
        _graph = lone.targeting_honest(copy.deepcopy(
            graph), N_TARGETS, N_SYBILS, top=False, stitches=N_STITCHES)
        inputs.append([_graph, 'one attacker targeting random nodes',
                       'one_attacker_targeting_random_nodes', outputs, charts])
        x_axis.append('one_attacker_targeting_random_nodes')

    if ONE_ATTACKER_GROUP_TARGET_ATTACK:
        _graph = lone.group_attack(copy.deepcopy(
            graph), N_SYBILS, N_GROUPS, stitches=N_STITCHES)
        inputs.append([_graph, 'one attacker group target attack',
                       'one_attacker_group_target_attack', outputs, charts])
        x_axis.append('one_attacker_group_target_attack')

    if ONE_SEED_AS_ATTACKER:
        _graph = lone.collsion_attack(copy.deepcopy(
            graph), 'Seed', N_SYBILS, stitches=N_STITCHES)
        inputs.append([_graph, 'one seed as attacker',
                       'one_seed_as_attacker', outputs, charts])
        x_axis.append('one_seed_as_attacker')

    if ONE_HONEST_AS_ATTACKER:
        _graph = lone.collsion_attack(copy.deepcopy(
            graph), 'Honest', N_SYBILS, stitches=N_STITCHES)
        inputs.append([_graph, 'one honest as attacker',
                       'one_honest_as_attacker', outputs, charts])
        x_axis.append('one_honest_as_attacker')

    if ONE_GROUP_TARGETING_SEEDS:
        _graph = collaborative.targeting_seeds(
            copy.deepcopy(
                graph), N_ATTACKERS, N_TARGETS, N_SYBILS, one_group=True, stitches=N_STITCHES)
        inputs.append([_graph, 'one group targeting seeds',
                       'one_group_targeting_seeds', outputs, charts])
        x_axis.append('one_group_targeting_seeds')

    if ONE_GROUP_TARGETING_TOP_NODES:
        _graph = collaborative.targeting_honest(copy.deepcopy(
            graph), N_ATTACKERS, N_TARGETS, N_SYBILS, one_group=True, top=True, stitches=N_STITCHES)
        inputs.append([_graph, 'one group targeting top nodes',
                       'one_group_targeting_top_nodes', outputs, charts])
        x_axis.append('one_group_targeting_top_nodes')

    if ONE_GROUP_TARGETING_RANDOM_NODES:
        _graph = collaborative.targeting_honest(copy.deepcopy(
            graph), N_ATTACKERS, N_TARGETS, N_SYBILS, one_group=True, top=False, stitches=N_STITCHES)
        inputs.append([_graph, 'one group targeting random nodes',
                       'one_group_targeting_random_nodes', outputs, charts])
        x_axis.append('one_group_targeting_random_nodes')

    if ONE_GROUP_GROUP_TARGET_ATTACK:
        _graph = collaborative.group_attack(copy.deepcopy(
            graph), N_ATTACKERS, N_TARGETS, N_SYBILS, N_GROUPS, stitches=N_STITCHES)
        inputs.append([_graph, 'one group group target attack',
                       'one_group_group_target_attack', outputs, charts])
        x_axis.append('one_group_group_target_attack')

    if ONE_GROUP_OF_SEEDS_AS_ATTACKER:
        _graph = collaborative.collsion_attack(
            copy.deepcopy(graph), 'Seed', N_UNFAITHFUL_SEEDS, N_SYBILS, one_group=True, stitches=N_STITCHES)
        inputs.append([_graph, 'one group of seeds as attacker',
                       'one_group_of_seeds_as_attacker', outputs, charts])
        x_axis.append('one_group_of_seeds_as_attacker')

    if ONE_GROUP_OF_HONESTS_AS_ATTACKER:
        _graph = collaborative.collsion_attack(
            copy.deepcopy(graph), 'Honest', N_UNFAITHFUL_HONESTS, N_SYBILS, one_group=True, stitches=N_STITCHES)
        inputs.append([_graph, 'one group of honests as attacker',
                       'one_group_of_honests_as_attacker', outputs, charts])
        x_axis.append('one_group_of_honests_as_attacker')

    if N_GROUPS_TARGETING_SEEDS:
        _graph = collaborative.targeting_seeds(copy.deepcopy(
            graph), N_ATTACKERS, N_TARGETS, N_SYBILS, one_group=False, stitches=N_STITCHES)
        inputs.append([_graph, 'n groups targeting seeds',
                       'n_groups_targeting_seeds', outputs, charts])
        x_axis.append('n_groups_targeting_seeds')

    if N_GROUPS_TARGETING_TOP_NODES:
        _graph = collaborative.targeting_honest(copy.deepcopy(
            graph), N_ATTACKERS, N_TARGETS, N_SYBILS, one_group=False, top=True, stitches=N_STITCHES)
        inputs.append([_graph, 'n groups targeting top nodes',
                       'n_groups_targeting_top_nodes', outputs, charts])
        x_axis.append('n_groups_targeting_top_nodes')

    if N_GROUPS_TARGETING_RANDOM_NODES:
        # some teams of attackers targeting random honests
        _graph = collaborative.targeting_honest(copy.deepcopy(
            graph), N_ATTACKERS, N_TARGETS, N_SYBILS, one_group=False, top=False, stitches=N_STITCHES)
        inputs.append([_graph, 'n groups targeting random nodes',
                       'n_groups_targeting_random_nodes', outputs, charts])
        x_axis.append('n_groups_targeting_random_nodes')

    if N_GROUPS_OF_SEEDS_AS_ATTACKER:
        _graph = collaborative.collsion_attack(
            copy.deepcopy(graph), 'Seed', N_UNFAITHFUL_SEEDS, N_SYBILS, one_group=False, stitches=N_STITCHES)
        inputs.append([_graph, 'n groups of seeds as attacker',
                       'n_groups_of_seeds_as_attacker', outputs, charts])
        x_axis.append('n_groups_of_seeds_as_attacker')

    if N_GROUPS_OF_HONESTS_AS_ATTACKER:
        _graph = collaborative.collsion_attack(
            copy.deepcopy(graph), 'Honest', N_UNFAITHFUL_HONESTS, N_SYBILS, one_group=False, stitches=N_STITCHES)
        inputs.append([_graph, 'n groups of honests as attacker',
                       'n_groups_of_honests_as_attacker', outputs, charts])
        x_axis.append('n_groups_of_honests_as_attacker')

    with multiprocessing.Pool(processes=None) as pool:
        pool.starmap(tests, inputs)

    plot()
    write_output_file(outputs, os.path.join(OUTPUT_FOLDER, 'result.csv'))


if __name__ == '__main__':
    t1 = time.time()
    main()
    print('Time:', int(time.time() - t1))
