from anti_sybil.templates.node import Node
import random


# the attacker connects to the seeds
def targeting_seeds(graph, options):
    edges = []
    sybils = []
    seeds = [n.name for n in graph.nodes if n.node_type == 'Seed']
    nodes_dic = {node.name: node for node in graph.nodes}

    # making the attacker node
    nodes_dic['attacker'] = Node(
        'attacker', 'Attacker', groups=set(['target_attack']))

    # connecting the attacker node to the seed nodes
    for i in range(options['num_seeds']):
        edges.append(
            (nodes_dic['attacker'], nodes_dic[seeds[i]]))

    # making the sybil nodes and connecting them to attacker nodes
    for i in range(options['num_sybils']):
        nodes_dic['s-{0}'.format(i)] = Node(
            's-{0}'.format(i), 'Sybil', groups=set(['target_attack']))
        sybils.append('s-{0}'.format(i))
        edges.append((nodes_dic['s-{0}'.format(i)], nodes_dic['attacker']))

    # connecting the sybil nodes together
    for i in range(options['stitches']):
        edges.append((nodes_dic[random.choice(sybils)],
                      nodes_dic[random.choice(sybils)]))

    # updating graph
    graph.add_edges_from(edges)
    return graph


# the attacker connects to the honests
def targeting_honest(graph, options):
    edges = []
    sybils = []
    honests = [n for n in graph.nodes if n.rank > 0]
    if options['top']:
        honests = sorted(honests, key=lambda n: n.rank, reverse=True)
    else:
        random.shuffle(honests)
    nodes_dic = {node.name: node for node in graph.nodes}

    # making the attacker node
    nodes_dic['attacker'] = Node(
        'attacker', 'Attacker', groups=set(['target_attack']))

    # connecting the attacker node to the honest nodes
    for honest in honests[:options['num_honests']]:
        edges.append(
            (nodes_dic['attacker'], nodes_dic[honest.name]))

    # making the sybil nodes and connecting them to the attacker node
    for i in range(options['num_sybils']):
        nodes_dic['s-{0}'.format(i)] = Node(
            's-{0}'.format(i), 'Sybil', groups=set(['target_attack']))
        sybils.append('s-{0}'.format(i))
        edges.append((nodes_dic['s-{0}'.format(i)], nodes_dic['attacker']))

    # connecting the sybil nodes together
    for i in range(options['stitches']):
        edges.append((nodes_dic[random.choice(sybils)],
                      nodes_dic[random.choice(sybils)]))

    # updating graph
    graph.add_edges_from(edges)
    return graph


# one attacker connects to one top-ranked honest node and propagates the score by creating multiple groups
def group_attack(graph, options):
    edges = []
    sybils = []
    target = sorted([n for n in graph.nodes],
                    key=lambda n: n.rank, reverse=True)[0]
    nodes_dic = {node.name: node for node in graph.nodes}

    # making the attacker node
    nodes_dic['attacker'] = Node(
        'attacker', 'Attacker', groups=set(['target_attack']))

    # connecting the attacker to a top-ranked node
    edges.append((nodes_dic['attacker'], nodes_dic[target.name]))

    # making the sybil nodes and connecting them to the attacker
    for i in range(options['num_sybils']):
        nodes_dic['s-{0}'.format(i)] = Node(
            's-{0}'.format(i), 'Sybil', groups=set(['target_attack']))
        sybils.append('s-{0}'.format(i))
        edges.append((nodes_dic['s-{0}'.format(i)], nodes_dic['attacker']))

    # connecting the sybil nodes together
    for i in range(options['stitches']):
        edges.append((nodes_dic[random.choice(sybils)],
                      nodes_dic[random.choice(sybils)]))

    # making sybils groups
    for i in range(options['num_groups']):
        nodes_dic['attacker'].groups.add('target_attack_{}'.format(i))
        nodes_dic[random.choice(sybils)].groups.add(
            'target_attack_{}'.format(i))
        nodes_dic[random.choice(sybils)].groups.add(
            'target_attack_{}'.format(i))

    # updating graph
    graph.add_edges_from(edges)
    return graph


# one seed or honest node as an attacker
def collsion_attack(graph, options):
    edges = []
    sybils = []
    if options['attacker_type'] == 'Seed':
        attacker = sorted([n for n in graph.nodes if n.node_type ==
                           'Seed'], key=lambda n: n.rank, reverse=True)[0]
    elif options['attacker_type'] == 'Honest':
        attacker = sorted([n for n in graph.nodes if n.node_type !=
                           'Seed'], key=lambda n: n.rank, reverse=True)[0]

    nodes_dic = {node.name: node for node in graph.nodes}

    # making the sybil nodes and connecting them to the attacker node
    for i in range(options['num_sybils']):
        nodes_dic['s-{0}'.format(i)] = Node(
            's-{0}'.format(i), 'Sybil', groups=set(['seeds_as_attacker']))
        sybils.append('s-{0}'.format(i))
        edges.append((nodes_dic['s-{0}'.format(i)], nodes_dic[attacker.name]))

    # connecting the sybil nodes together
    for i in range(options['stitches']):
        edges.append((nodes_dic[random.choice(sybils)],
                      nodes_dic[random.choice(sybils)]))

    # updating graph
    graph.add_edges_from(edges)
    return graph
