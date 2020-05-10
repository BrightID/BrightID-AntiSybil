from anti_sybil.graphs.node import Node
import random


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
