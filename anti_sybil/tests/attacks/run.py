import matplotlib.pyplot as plt
import multiprocessing
import requests
import networkx as nx
import time
import os
from anti_sybil import algorithms
from anti_sybil.utils import *
from config import *
import random

random.seed(2)
x_axis = []
manager = multiprocessing.Manager()
outputs = manager.list()
charts = manager.dict()


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
    attacks = {}
    attacks['nodes'] = [{'id': n.name, 'scores': {},
                         'type': n.node_type, 'clusters': {}} for n in graph.nodes]
    attacks['links'] = [{'source': e[0].name,
                         'target': e[1].name, 'value': 1} for e in graph.edges]
    nodes = {}
    for i, n in enumerate(graph.nodes):
        nodes[n.name] = i
    for algorithm_name in ALGORITHMS:
        reset_ranks(graph)
        ranker = ALGORITHMS[algorithm_name](
            graph, ALGORITHMS_OPTIONS[algorithm_name])
        ranker.rank()
        for node in graph.nodes:
            attacks['nodes'][nodes[node.name]
                             ]['scores'][algorithm_name] = node.rank
            if hasattr(node, 'clusters'):
                attacks['nodes'][nodes[node.name]
                                 ]['clusters'].update(node.clusters)
        if algorithm_name in ['SybilRank']:
            linear_distribution(graph)
        outputs.append(generate_output(
            graph, '{}\n{}'.format(algorithm_name, description)))
        draw_graph(graph, os.path.join(OUTPUT_FOLDER,
                                       '2D_{}_{}.html'.format(algorithm_name, file_name)))
        charts[algorithm_name][description] = successful_honests(
            graph, description, algorithm_name)
    draw_3d_graph(attacks, list(ALGORITHMS.keys()), os.path.join(
        OUTPUT_FOLDER, '{}.html'.format(file_name)))


def successful_honests(graph, description, algorithm):
    main_component = sorted([component for component in nx.connected_components(
        graph)], key=lambda l: len(l), reverse=True)[0]
    honests = []
    sybils = []
    attackers = []
    zeros = 0
    for node in main_component:
        if node.node_type in ['Seed', 'Honest', 'New'] and node.rank == 0:
            zeros += 1
        if node.node_type in ['Sybil', 'Non Bridge Sybil', 'Bridge Sybil']:
            sybils.append(node.rank)
        elif node.node_type in ['Seed', 'Honest', 'New']:
            honests.append(node.rank)
        elif node.node_type == 'Attacker':
            attackers.append(node.rank)
    avg_sybils = sum(sybils) / len(sybils) if sybils else 0
    verified = len([h for h in honests if h > avg_sybils])
    percent = verified / (len(main_component) - len(sybils) - len(attackers)) * 100
    print('{}\nAlgorithm:\t{}'.format(description, algorithm))
    print('No. Zeros:\t{}'.format(zeros))
    print('No. honests:\t{}\nNo. sybils:\t{}\nNo. verified:\t{}\nPercent:\t{}\n\n'.format(
        len(honests), len(sybils), verified, percent))
    return percent


def plot():
    fig, ax = plt.subplots()
    colors = ['b', 'r', 'c', 'y', 'm', 'y', 'k', 'g']
    for i, chart in enumerate(charts):
        ax.plot(
            x_axis,
            [charts[chart][p] for p in x_axis],
            'go--',
            color=colors[i],
            alpha=0.5,
            label='= {}'.format(chart),
        )
    ax.legend()
    plt.title('Targets:{} Sybils:{} Attackers:{} Stitches:{} Groups:{} Unfaithful Seeds:{} Unfaithful Honests:{}'.format(
        N_TARGETS, N_SYBILS, N_ATTACKERS, N_STITCHES, N_GROUPS, N_UNFAITHFUL_SEEDS, N_UNFAITHFUL_HONESTS), fontsize=7)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, str(int(time.time())) + '.png'))


def main():
    global outputs, charts
    inputs = []
    for algorithm in ALGORITHMS:
        charts[algorithm] = manager.dict()

    # making the graph and ranking nodes
    graph = generate_graph()
    ranker = algorithms.SybilRank(graph)
    ranker.rank()

    # modeling the attacks
    for attack_name in ATTACKS:
        _graph = ATTACKS[attack_name](
            graph.copy(), ATTACKS_OPTIONS[attack_name])
        file_name = attack_name.replace(' ', '_')
        inputs.append([_graph, attack_name, file_name, outputs, charts])
        x_axis.append(attack_name)

    # run the algorithms
    with multiprocessing.Pool(processes=None) as pool:
        pool.starmap(tests, inputs)

    plot()
    write_output_file(outputs, os.path.join(OUTPUT_FOLDER, 'result.csv'))


if __name__ == '__main__':
    t1 = time.time()
    main()
    print('Time:', int(time.time() - t1))
