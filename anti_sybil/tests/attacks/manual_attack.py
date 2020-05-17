import random
from anti_sybil.utils import Node


def attack(graph, options):
    nodes_dic = {n.name: n for n in graph.nodes}
    seeds = [n for n in graph.nodes if n.node_type == 'Seed']
    honests = [n for n in graph.nodes if n.node_type in [
        'Honest', 'Seed'] and n.rank > 0]
    if options['top']:
        honests = sorted(honests, key=lambda n: n.rank, reverse=True)
        seeds = sorted(seeds, key=lambda n: n.rank, reverse=True)
    else:
        random.shuffle(honests)
        random.shuffle(seeds)
    edges = []

    # create new nodes and make connections
    for connection in options['connections']:
        edge = []
        for node_name in connection:
            if node_name.startswith('seed_'):
                k = seeds[int(node_name[5:])].name
                edge.append(nodes_dic[k])
            elif node_name.startswith('honest_'):
                k = honests[int(node_name[7:])].name
                edge.append(nodes_dic[k])
            else:
                if node_name not in nodes_dic:
                    nodes_dic[node_name] = Node(
                        node_name, 'Sybil', groups=set())
                edge.append(nodes_dic[node_name])
        edges.append(edge)

    # create new groups
    for group_name in options['groups']:
        for node_name in options['groups'][group_name]:
            if node_name.startswith('seed_'):
                k = seeds[int(node_name[5:])].name
                nodes_dic[k].groups.add(group_name)
            elif node_name.startswith('honest_'):
                k = honests[int(node_name[7:])].name
                nodes_dic[k].groups.add(group_name)
            else:
                if node_name not in nodes_dic:
                    raise Exception(
                        "Error, You should add nodes and connections first")
                nodes_dic[node_name].groups.add(group_name)
    graph.add_edges_from(edges)
    return graph
