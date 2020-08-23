import time
import random
import itertools
from anti_sybil.utils import Node


# the attackers connect to the seeds
def targeting_seeds(graph, options):
    sybils = []
    attackers = []
    high_degree_attacker = options.get('high_degree_attacker', False)
    seeds = [n for n in graph if n.node_type == 'Seed']
    seeds.sort(key=lambda n: graph.degree(n), reverse=high_degree_attacker)

    # making attacker nodes
    for i in range(options['num_attacker']):
        groups = {'collaborative_attack': 'NonSeed'} if options['one_group'] else {
            'collaborative_attack_{}'.format(i): 'NonSeed'}
        attacker = Node('attacker_{}'.format(i), 'Attacker',
                        groups=groups, created_at=int(time.time() * 1000))
        attackers.append(attacker)

    # connecting attacker nodes to the seed nodes
    for attacker in attackers:
        for seed in seeds[:options['num_seeds']]:
            graph.add_edge(attacker, seed)

    # making sybil nodes and connecting them to attacker nodes
    num_groups = 1 if options['one_group'] else min(
        options['num_attacker'], options['num_sybils'] // 2)
    for i in range(num_groups):
        for j in range(options['num_sybils'] // num_groups):
            groups = {'collaborative_attack': 'NonSeed'} if options['one_group'] else {
                'collaborative_attack_{}'.format(i): 'NonSeed'}
            sybil = Node('s-{0}-{1}'.format(i, j), 'Sybil',
                         groups=groups, created_at=int(time.time() * 1000))
            sybils.append(sybil)
            if options['one_group']:
                for attacker in attackers:
                    graph.add_edge(attacker, sybil)
            else:
                graph.add_edge(sybil, attackers[i])

    # connecting sybil nodes together
    for i in range(options['stitches']):
        s, t = random.sample(sybils, 2)
        graph.add_edge(s, t)

    return graph


# the attackers connect to the honests
def targeting_honest(graph, options):
    sybils = []
    attackers = []
    honests = [n for n in graph if n.rank > 0]
    if options['top']:
        honests.sort(key=lambda n: n.rank, reverse=True)
    else:
        random.shuffle(honests)

    # making attacker nodes
    for i in range(options['num_attacker']):
        groups = {'collaborative_attack': 'NonSeed'} if options['one_group'] else {
            'collaborative_attack_{}'.format(i): 'NonSeed'}
        attacker = Node('attacker_{}'.format(i), 'Attacker',
                        groups=groups, created_at=int(time.time() * 1000))
        attackers.append(attacker)

    # connecting attacker nodes to the honest nodes
    for attacker in attackers:
        for honest in honests[:options['num_honests']]:
            graph.add_edge(attacker, honest)

    # making sybil nodes and connecting them to attacker nodes
    num_groups = 1 if options['one_group'] else min(
        options['num_attacker'], options['num_sybils'] // 2)
    for i in range(num_groups):
        for j in range(options['num_sybils'] // num_groups):
            groups = {'collaborative_attack': 'NonSeed'} if options['one_group'] else {
                'collaborative_attack_{}'.format(i): 'NonSeed'}
            sybil = Node('s-{0}-{1}'.format(i, j), 'Sybil',
                         groups=groups, created_at=int(time.time() * 1000))
            sybils.append(sybil)
            if options['one_group']:
                for attacker in attackers:
                    graph.add_edge(sybil, attacker)
            else:
                graph.add_edge(sybil, attackers[i])

    # connecting sybil nodes together
    for i in range(options['stitches']):
        s, t = random.sample(sybils, 2)
        graph.add_edge(s, t)

    return graph


# the attackers connect to the top-ranked honests and propagate the score by creating multiple groups
def group_attack(graph, options):
    sybils = []
    attackers = []
    honests = [n for n in graph if n.rank > 0]
    honests.sort(key=lambda n: n.rank, reverse=True)

    # making attacker nodes
    for i in range(options['num_attacker']):
        attacker = Node('attacker_{}'.format(i), 'Attacker',
                        groups={'collaborative_attack': 'NonSeed'}, created_at=int(time.time() * 1000))
        attackers.append(attacker)

        # connecting attacker nodes to the honest nodes
        for honest in honests[:options['num_honests']]:
            graph.add_edge(attacker, honest)

    # making sybil nodes and connecting them to the attacker nodes
    for i in range(options['num_sybils']):
        sybil = Node('s-{0}'.format(i), 'Sybil',
                     groups={'collaborative_attack': 'NonSeed'}, created_at=int(time.time() * 1000))
        sybils.append(sybil)
        for attacker in attackers:
            graph.add_edge(sybil, attacker)

    # making sybil groups
    for i in range(options['num_groups']):
        for attacker in attackers:
            attacker.groups['collaborative_attack_{}'.format(i)] = 'NonSeed'
        random.choice(
            sybils).groups['collaborative_attack_{}'.format(i)] = 'NonSeed'
        random.choice(
            sybils).groups['collaborative_attack_{}'.format(i)] = 'NonSeed'

    # connecting sybil nodes together
    for i in range(options['stitches']):
        s, t = random.sample(sybils, 2)
        graph.add_edge(s, t)

    return graph


# a group of seeds or honests as attackers
def collusion_attack(graph, options):
    sybils = []
    high_degree_attacker = options.get('high_degree_attacker', False)
    if options['attacker_type'] == 'Seed':
        attackers = [n for n in graph if n.node_type == 'Seed']
        attackers.sort(key=lambda n: graph.degree(n), reverse=high_degree_attacker)
        attackers = attackers[:options['num_attacker']]

    elif options['attacker_type'] == 'Honest':
        attackers = [n for n in graph if n.node_type != 'Seed']
        attackers.sort(key=lambda n: n.rank, reverse=high_degree_attacker)
        attackers = attackers[:options['num_attacker']]

    if options.get('disconnect_attacker', False):
        for attacker in attackers:
            for n in list(graph.neighbors(attacker))[1:]:
                graph.remove_edge(attacker, n)

    # making sybil nodes and connecting them to attacker nodes
    num_groups = 1 if options['one_group'] else min(
        options['num_attacker'], options['num_sybils'] // 2)
    for i in range(num_groups):
        for j in range(options['num_sybils'] // num_groups):
            groups = {'collaborative_attack': 'NonSeed'} if options['one_group'] else {
                'collaborative_attack_{}'.format(i): 'NonSeed'}
            sybil = Node('s-{0}-{1}'.format(i, j), 'Sybil',
                         groups=groups, created_at=int(time.time() * 1000))
            sybils.append(sybil)
            if options['one_group']:
                for attacker in attackers:
                    graph.add_edge(sybil, attacker)
            else:
                graph.add_edge(sybil, attackers[i])

    # connecting sybil nodes together
    for i in range(options['stitches']):
        s, t = random.sample(sybils, 2)
        graph.add_edge(s, t)

    return graph


# multi cluster attack
def multi_cluster_attack(graph, options):
    sybils = {}
    if options['attacker_type'] == 'Seed':
        attackers = [n for n in graph if n.node_type == 'Seed']
        attackers.sort(key=lambda n: graph.degree(n), reverse=False)
        attackers = attackers[:options['num_attacker']]

    elif options['attacker_type'] == 'Honest':
        attackers = [n for n in graph if n.node_type != 'Seed']
        attackers.sort(key=lambda n: n.rank, reverse=True)
        attackers = attackers[:options['num_attacker']]

    # making sybil nodes and connecting them to attacker nodes
    num_groups = min(options['num_attacker'], options['num_sybils'] // 2)
    for i in range(num_groups):
        for j in range(options['num_sybils'] // num_groups):
            groups = {'collaborative_attack_{}'.format(i): 'NonSeed'}
            sybil = Node('s-{0}-{1}'.format(i, j), 'Sybil',
                         groups=groups, created_at=int(time.time() * 1000))
            sybils[sybil] = i
            graph.add_edge(sybil, attackers[i])
        # inside_sybils = [n for n in sybils if sybils[n] == i]
        # pairs = itertools.combinations(inside_sybils, 2)
        # for s, t in pairs:
        #     edges.append((s, t))

    for s1 in sybils:
        candidates = [s for s in sybils if sybils[s] !=
                      sybils[s1] and outside_degree(graph, s) < 10]
        num_sample = min(10 - outside_degree(graph, s1), len(candidates))
        if not candidates:
            continue
        candidates = random.sample(candidates, num_sample)
        for s2 in candidates:
            graph.add_edge(s1, s2)
    return graph


def outside_degree(graph, sybil):
    num = 0
    perfix = 's-' + sybil.name.split('-')[1]
    for n in graph.neighbors(sybil):
        if n.name.startswith('s-') and not n.name.startswith(perfix):
            num += 1
    return num


def many_small_groups_attack(graph, options):
    sybils = []
    attackers = [n for n in graph if n.node_type == 'Seed']
    attackers.sort(key=lambda n: n.rank, reverse=False)
    attackers = attackers[:options['num_attacker']]

    for i in range(options['num_sybils']):
        groups = {'sg-{}'.format(i): 'NonSeed'}
        sybil = Node('s-{}'.format(i), 'Sybil', groups=groups, created_at=int(time.time() * 1000))
        sybils.append(sybil)
        for attacker in attackers:
            graph.add_edge(sybil, attacker)
            attacker.groups.update(groups)

    # connecting the sybil nodes together
    for i in range(options['stitches']):
        s, t = random.sample(sybils, 2)
        graph.add_edge(s, t)
    return graph
