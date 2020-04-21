from anti_sybil import algorithms
from anti_sybil.graphs.node import Node
from anti_sybil.utils import *

OUTPUT_FOLDER = './outputs/attackers_in_groups/'

graph_params = {
    'num_seed_nodes': 14,
    'num_attacker_to_num_honest': 0.0,
    'num_sybil_to_num_attacker': 0,
    'num_groups': 30,
    'min_group_nodes': 3,
    'max_group_nodes': 12,
    'num_joint_node': 1200,
    'num_seed_groups': 2,
    'min_known_ratio': .125,
    'avg_known_ratio': .5,
    'max_known_ratio': 1,
    'sybil_to_attackers_con': 1,
    'num_inter_group_con': 100
}

algorithm_options = {
    'accumulative': False,
    'weaken_under_min': False,
    'min_degree': 8,
    'weaken_seed': 0,
    'nonlinear_distribution': True,
    'group_edge_weight': 20,
    'thresholds': [.36, .24, .22, .21, .20, .19, .18, .12, .06, .04, .02, .01, .005, .004, .003, .002, .0015, .001, .0005, 0]
}

sybil_edges1 = [
    [30, 's1'],
    [31, 's1'],
    [32, 's1'],
    [33, 's1'],
    [34, 's1'],
    [35, 's1'],
    [36, 's1'],
    [37, 's1'],
    [38, 's1'],
    [39, 's1'],
]

sybil_edges2 = [
    [30, 's1'],
    [31, 's1'],
    [32, 's1'],
    [33, 's1'],
    [34, 's1'],
    [35, 's1'],
    [36, 's1'],
    [37, 's1'],
    [38, 's1'],
    [39, 's1'],
]

sybil_edges3 = [
    [30, 's1'],
    [31, 's1'],
    [32, 's1'],
    [33, 's1'],
    [34, 's1'],
    [35, 's1'],
    [36, 's1'],
    [37, 's1'],
    [38, 's1'],
    [39, 's1'],
]

sybil_edges4 = [
    [30, 's1'],
    [31, 's1'],
    [32, 's1'],
    [33, 's1'],
    [34, 's1'],
    [35, 's1'],
    [36, 's1'],
    [37, 's1'],
    [38, 's1'],
    [39, 's1'],
]

sybil_edges5 = [
    [6, 's51'],
    [6, 's52'],
    [6, 's53'],
    [6, 's54'],
    [6, 's55'],
    [6, 's56'],
    [6, 's57'],
    [6, 's58'],
    ['s51', 's52'],
    ['s53', 's54'],
    ['s55', 's56'],
    ['s57', 's58']
]

sybil_edges6 = [
    [6, 's61'],
    [6, 's62'],
    [6, 's63'],
    [6, 's64'],
    [6, 's65'],
    [6, 's66'],
    [6, 's67'],
    [6, 's68'],
    ['s61', 's62'],
    ['s63', 's64'],
    ['s65', 's66'],
    ['s67', 's68']
]

sybil_edges7 = [
    [6, 's71'],
    [6, 's72'],
    [6, 's73'],
    [6, 's74'],
    [6, 's75'],
    [6, 's76'],
    [6, 's77'],
    [6, 's78'],
    ['s71', 's72'],
    ['s73', 's74'],
    ['s75', 's76'],
    ['s77', 's78']
]

sybil_edges8 = [
    [6, 's81'],
    [6, 's82'],
    [6, 's83'],
    [6, 's84'],
    [6, 's85'],
    [6, 's86'],
    [6, 's87'],
    [6, 's88'],
    ['s81', 's82'],
    ['s83', 's84'],
    ['s85', 's86'],
    ['s87', 's88']
]

sybil_edges9 = [
    [6, 's91'],
    [6, 's92'],
    [6, 's93'],
    [6, 's94'],
    [6, 's95'],
    [6, 's96'],
    [6, 's97'],
    [6, 's98'],
    ['s91', 's92'],
    ['s93', 's94'],
    ['s95', 's96'],
    ['s97', 's98']
]

sybil_edges10 = [
    [6, 's101'],
    [6, 's102'],
    [6, 's103'],
    [6, 's104'],
    [6, 's105'],
    [6, 's106'],
    [6, 's107'],
    [6, 's108'],
    ['s101', 's102'],
    ['s103', 's104'],
    ['s105', 's106'],
    ['s107', 's108']
]


def add_sybils(graph, sybil_edges, group):
    nodes_dic = {node.name: node for node in graph.nodes()}
    edges = []
    for edge in sybil_edges:
        for node_name in edge:
            if node_name in nodes_dic:
                nodes_dic[node_name].groups.add(group)
            else:
                nodes_dic[node_name] = Node(node_name, 'Sybil', groups=set([group]))
        edges.append((nodes_dic[edge[0]], nodes_dic[edge[1]]))
    graph.add_edges_from(edges)


graph = graphs.generators.group_based.generate(graph_params)
add_sybils(graph, sybil_edges1, 'sybil1')
add_sybils(graph, sybil_edges2, 'sybil2')
add_sybils(graph, sybil_edges3, 'sybil3')
add_sybils(graph, sybil_edges4, 'sybil4')
# add_sybils(graph, sybil_edges5, 'sybil5')
# add_sybils(graph, sybil_edges6, 'sybil6')
# add_sybils(graph, sybil_edges7, 'sybil7')
# add_sybils(graph, sybil_edges8, 'sybil8')
# add_sybils(graph, sybil_edges9, 'sybil9')
# add_sybils(graph, sybil_edges10, 'sybil10')

outputs = []

# ranker = algorithms.SybilRank(graph, algorithm_options)
# ranker.rank()
# outputs.append(generate_output(graph, 'SybilRank'))
# draw_graph(graph, os.path.join(OUTPUT_FOLDER, 'SybilRank.html'))
#
# reset_ranks(graph)

ranker = algorithms.SybilGroupRank(graph, algorithm_options)
ranker.rank()
outputs.append(generate_output(graph, 'SybilGroupRank'))
draw_graph(graph, os.path.join(OUTPUT_FOLDER, 'SybilGroupRank.html'))

# reset_ranks(graph)

# ranker = algorithms.GroupSybilRank(graph, algorithm_options)
# ranker.rank()
# outputs.append(generate_output(graph, 'IntraGroupWeight'))
# draw_graph(graph, os.path.join(OUTPUT_FOLDER, 'IntraGroupWeight.html'))
#
# reset_ranks(graph)
# algorithm_options['weaken_under_min'] = True
#
# ranker = algorithms.SybilRank(graph, algorithm_options)
# ranker.rank()
# outputs.append(generate_output(graph, 'SR_weaken'))
# draw_graph(graph, os.path.join(OUTPUT_FOLDER, 'SR_weaken.html'))
#
# reset_ranks(graph)
#
# ranker = algorithms.SybilGroupRank(graph, algorithm_options)
# ranker.rank()
# outputs.append(generate_output(graph, 'SGR_weaken'))
# draw_graph(graph, os.path.join(OUTPUT_FOLDER, 'SGR_weaken.html'))
#
# reset_ranks(graph)

# ranker = algorithms.GroupSybilRank(graph, algorithm_options)
# ranker.rank()
# outputs.append(generate_output(graph, 'IGW_weaken'))
# draw_graph(graph, os.path.join(OUTPUT_FOLDER, 'IGW_weaken.html'))
#
# reset_ranks(graph)
#
# ranker = algorithms.GroupMergingRank(graph, algorithm_options)
# ranker.rank()
# outputs.append(generate_output(graph, 'GroupMerge'))
# draw_graph(graph, os.path.join(OUTPUT_FOLDER, 'GroupMerge.html'))

write_output_file(outputs, os.path.join(OUTPUT_FOLDER, 'result.csv'))