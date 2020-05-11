from anti_sybil.graphs.node import Node
import random

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
    ['s_1', 's1'],
    ['s_1', 's2'],
    ['s_1', 's3'],
    ['s_1', 's4'],
    ['s_1', 's5'],
    ['s_1', 's6'],
    ['s_1', 's7'],
    ['s_1', 's8'],
    ['s_1', 's9'],
    ['s_1', 's10'],
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


def generate(graph):
    update_graph(graph, group1, 'sybil1', top=True)
    update_graph(graph, group2, 'sybil2', top=True)
    update_graph(graph, group3, 'sybil3', top=True)
    update_graph(graph, group4, 'sybil4', top=True)
    return graph
