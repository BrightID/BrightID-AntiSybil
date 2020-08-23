import time
import random
from anti_sybil.utils import Node
from anti_sybil.utils import reset_ranks
import anti_sybil.algorithms as algorithms


# the attacker connects to the seeds
def targeting_seeds(graph, options):
    sybils = []
    seeds = [n for n in graph if n.node_type == 'Seed']

    groups = {'target_attack': 'NonSeed'}
    # making the attacker node
    attacker = Node('attacker', 'Attacker', groups=groups,
                    created_at=int(time.time() * 1000))

    # connecting the attacker node to the seed nodes
    for i in range(options['num_seeds']):
        graph.add_edge(attacker, seeds[i])

    # making the sybil nodes and connecting them to attacker nodes
    for i in range(options['num_sybils']):
        sybil = Node('s-{0}'.format(i), 'Sybil', groups=groups,
                     created_at=int(time.time() * 1000))
        sybils.append(sybil)
        graph.add_edge(sybil, attacker)

    # connecting the sybil nodes together
    for i in range(options['stitches']):
        s, t = random.sample(sybils, 2)
        graph.add_edge(s, t)

    return graph


# the attacker connects to the honests
def targeting_honest(graph, options):
    sybils = []
    honests = [n for n in graph if n.rank > 0]
    if options['top']:
        honests.sort(key=lambda n: n.rank, reverse=True)
    else:
        random.shuffle(honests)

    groups = {'target_attack': 'NonSeed'}
    # making the attacker node
    attacker = Node('attacker', 'Attacker', groups=groups,
                    created_at=int(time.time() * 1000))

    # connecting the attacker node to the honest nodes
    for honest in honests[:options['num_honests']]:
        graph.add_edge(attacker, honest)

    # making the sybil nodes and connecting them to the attacker node
    for i in range(options['num_sybils']):
        sybil = Node('s-{0}'.format(i), 'Sybil', groups=groups,
                     created_at=int(time.time() * 1000))
        sybils.append(sybil)
        graph.add_edge(sybil, attacker)

    # connecting the sybil nodes together
    for i in range(options['stitches']):
        s, t = random.sample(sybils, 2)
        graph.add_edge(s, t)

    return graph


# one attacker connects to one top-ranked honest node and propagates the score by creating multiple groups
def group_attack(graph, options):
    sybils = []
    target = sorted(graph, key=lambda n: n.rank, reverse=True)[0]

    groups = {'target_attack': 'NonSeed'}
    # making the attacker node
    attacker = Node('attacker', 'Attacker', groups=groups,
                    created_at=int(time.time() * 1000))

    # connecting the attacker to a top-ranked node
    graph.add_edge(attacker, target)

    # making the sybil nodes and connecting them to the attacker
    for i in range(options['num_sybils']):
        sybil = Node('s-{0}'.format(i), 'Sybil', groups=groups,
                     created_at=int(time.time() * 1000))
        sybils.append(sybil)
        graph.add_edge(sybil, attacker)

    # connecting the sybil nodes together
    for i in range(options['stitches']):
        s, t = random.sample(sybils, 2)
        graph.add_edge(s, t)

    # making sybils groups
    for i in range(options['num_groups']):
        attacker.groups['target_attack_{}'.format(i)] = 'NonSeed'
        random.choice(sybils).groups['target_attack_{}'.format(i)] = 'NonSeed'
        random.choice(sybils).groups['target_attack_{}'.format(i)] = 'NonSeed'

    return graph


# one seed or honest node as an attacker
def collusion_attack(graph, options):
    sybils = []
    if options['attacker_type'] == 'Seed':
        attackers = [n for n in graph if n.node_type == 'Seed']
        attackers.sort(key=lambda n: n.rank, reverse=True)
        attacker = attackers[0]
    elif options['attacker_type'] == 'Honest':
        attackers = [n for n in graph if n.node_type != 'Seed']
        attackers.sort(key=lambda n: n.rank, reverse=True)
        attacker = attackers[0]

    # making the sybil nodes and connecting them to the attacker node
    groups = {'seeds_as_attacker': 'NonSeed'}
    for i in range(options['num_sybils']):
        sybil = Node('s-{0}'.format(i), 'Sybil', groups=groups,
                     created_at=int(time.time() * 1000))
        sybils.append(sybil)
        graph.add_edge(sybil, attacker)

    # connecting the sybil nodes together
    for i in range(options['stitches']):
        s, t = random.sample(sybils, 2)
        graph.add_edge(s, t)

    return graph


# the stupid sybil attack
def stupid_sybil(graph, options):
    sybils = []
    attackers = [n for n in graph if n.rank > 0]
    attackers.sort(key=lambda n: n.rank, reverse=True)
    for attacker in attackers:
        attacker.groups['stupid_sybil'] = 'NonSeed'
        for i in range(2):
            groups = {'stupid_sybil': 'NonSeed'}
            sybil = Node('stupid_sybil_{}'.format(i), 'Sybil', groups=groups, created_at=int(time.time() * 1000))
            sybils.append(sybil)
            graph.add_edge(attacker, sybil)
        reset_ranks(graph)
        ranker = algorithms.GroupSybilRank(graph)
        ranker.rank()
        border = max([s.rank for s in sybils])
        if border:
            break
        graph.remove_nodes_from(sybils)
        del attacker.groups['stupid_sybil']
    return graph
