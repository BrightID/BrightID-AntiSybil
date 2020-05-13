import os
import random
from anti_sybil.utils import *
from manual_attack_config import *
from anti_sybil import algorithms
from anti_sybil.graphs.node import Node

outputs = []
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

# use `h_ + integer` format to connect to the honests nodes
# use `s_ + integer` format to connect to the seed nodes
# use `id_ + Brightid` format to connect to the node by Brightid of the node
# When the "top" variable set True, the `integer` part is the position in the list of the nodes sorted in descending order


group1 = [
    ['id_xGUyVQLYV80pajm8QP-9cfHC7xri49V58k02kqTAiUI', 's12'],
    ['id_xGUyVQLYV80pajm8QP-9cfHC7xri49V58k02kqTAiUI', 's13'],
    ['id_xGUyVQLYV80pajm8QP-9cfHC7xri49V58k02kqTAiUI', 's14'],
    ['id_xGUyVQLYV80pajm8QP-9cfHC7xri49V58k02kqTAiUI', 's15'],
    ['id_xGUyVQLYV80pajm8QP-9cfHC7xri49V58k02kqTAiUI', 's16'],
    ['id_xGUyVQLYV80pajm8QP-9cfHC7xri49V58k02kqTAiUI', 's17'],
    ['id_xGUyVQLYV80pajm8QP-9cfHC7xri49V58k02kqTAiUI', 's18'],
    ['id_xGUyVQLYV80pajm8QP-9cfHC7xri49V58k02kqTAiUI', 's19'],
    ['id_xGUyVQLYV80pajm8QP-9cfHC7xri49V58k02kqTAiUI', 's20'],
]

group2 = [
    ['h_1', 's1'],
    ['h_1', 's2'],
    ['h_1', 's3'],
    ['h_1', 's4'],
    ['h_1', 's5'],
    ['h_1', 's6'],
    ['h_1', 's7'],
    ['h_1', 's8'],
    ['h_1', 's9'],
    ['h_1', 's10'],
]

group3 = [
    ['s_5', 's1'],
    ['s_5', 's2'],
    ['s_5', 's3'],
    ['s_5', 's4'],
    ['s_5', 's5'],
    ['s_5', 's6'],
    ['s_5', 's7'],
    ['s_5', 's8'],
    ['s_5', 's9'],
    ['s_5', 's10'],
]

group4 = [
    ['s1', 's2'],
    ['s1', 's3'],
    ['s1', 's4'],
    ['s1', 's5'],
    ['s1', 's6'],
    ['s1', 's7'],
    ['s1', 's8'],
    ['s1', 's9'],
    ['s1', 's10'],
]


def update_graph(graph, group, group_name, top=True):
    nodes_dic = {n.name: n for n in graph.nodes}
    seeds = [n for n in graph.nodes if n.node_type == 'Seed']
    honests = [n for n in graph.nodes if n.node_type in [
        'Honest', 'Seed'] and n.rank > 0]
    if top:
        honests = sorted(honests, key=lambda n: n.rank, reverse=True)
        seeds = sorted(seeds, key=lambda n: n.rank, reverse=True)
    else:
        random.shuffle(honests)
        random.shuffle(seeds)
    edges = []
    for edge in group:
        e = []
        for node_name in edge:
            if node_name.startswith('id_'):
                k = node_name[3:]
                nodes_dic[k].groups.add(group_name)
                e.append(nodes_dic[k])
            elif node_name.startswith('s_'):
                k = seeds[int(node_name[2:])].name
                nodes_dic[k].groups.add(group_name)
                e.append(nodes_dic[k])
            elif node_name.startswith('h_'):
                k = honests[int(node_name[2:])].name
                nodes_dic[k].groups.add(group_name)
                e.append(nodes_dic[k])
            else:
                if node_name not in nodes_dic:
                    nodes_dic[node_name] = Node(
                        node_name, 'Sybil', groups=set([group_name]))
                e.append(nodes_dic[node_name])
        edges.append(e)
    graph.add_edges_from(edges)


def attack(graph):
    update_graph(graph, group1, 'sybil1', top=True)
    update_graph(graph, group2, 'sybil2', top=True)
    update_graph(graph, group3, 'sybil3', top=True)
    update_graph(graph, group4, 'sybil4', top=True)
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

    if WEIGHTED_SYBIL_RANK:
        reset_ranks(graph)
        ranker = algorithms.WeightedSybilRank(graph, algorithm_options)
        ranker.rank()
        outputs.append(generate_output(
            graph, 'WeightedSybilRank\n{}'.format(description)))
        draw_graph(graph, os.path.join(
            OUTPUT_FOLDER, 'WSR_{}.html'.format(file_name)))


def main():
    # making the graph and ranking nodes
    graph = generate_graph()
    ranker = algorithms.SybilGroupRank(graph, algorithm_options)
    ranker.rank()

    graph = attack(graph)
    tests(graph, 'manual attack', 'manual_attack')

    write_output_file(outputs, os.path.join(OUTPUT_FOLDER, 'result.csv'))


if __name__ == '__main__':
    main()
