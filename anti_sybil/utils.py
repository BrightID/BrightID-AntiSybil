from arango import ArangoClient
from bisect import bisect
import networkx as nx
import numpy as np
import zipfile
import tarfile
import requests
import shutil
import json
import csv
import os

GRAPH_TEMPLATE = GRAPH_3D_TEMPLATE = COMPARE_GRAPH_TEMPLATE = None
BACKUP_URL = 'https://storage.googleapis.com/brightid-backups/brightid.tar.gz'


class Node:
    def __init__(self, name, node_type, groups=None, init_rank=0, raw_rank=0, rank=None, created_at=None, verifications=None):
        self.name = name
        self.node_type = node_type
        self.rank = rank
        self.groups = groups if groups else {}
        self.init_rank = init_rank
        self.raw_rank = raw_rank
        self.created_at = created_at
        self.verifications = verifications if verifications else []

    def __repr__(self):
        return 'Node: {}'.format(self.name)


def write_output_file(outputs, file_name):
    if len(outputs) == 0:
        return
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))
    rows = [['Results'] + [output['name'] for output in outputs]]
    for title in outputs[0]:
        if title != 'name':
            rows.append([title] + [output.get(title, '')
                                   for output in outputs])
    with open(file_name, 'w') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)


def find_border(graph):
    best_border = best_score = 0
    for i in range(100):
        honest_score = len([node for node in graph if node.node_type in (
            'Honest', 'Seed') and node.rank > i])
        sybil_score = len([node for node in graph if node.node_type in (
            'Sybil', 'Non Bridge Sybil', 'Bridge Sybil') and node.rank < i])
        score = (honest_score * sybil_score)**.5
        if score >= best_score:
            best_border = i
            best_score = score
    return best_border


def calculate_successful_sybils(ranks_dic):
    honests = []
    sybils = []
    attackers = []
    result = {}
    for category in ranks_dic:
        if category in ['Sybil', 'Non Bridge Sybil', 'Bridge Sybil']:
            sybils.extend(ranks_dic[category])
        elif category in ['Seed', 'Honest']:
            honests.extend(ranks_dic[category])
        elif category == 'Attacker':
            attackers.extend(ranks_dic[category])
    if sybils:
        honests = [h for h in honests if h]
    honests.sort()
    # for limit in [.8, .9, 1]:
    #     successful_sybils = [rank for rank in sybils if rank >= min(
    #         honests[:int(limit * len(honests))])]
    #     result['successful_sybils_percent_{0}'.format(limit)] = round(
    #         (len(successful_sybils) * 100.0) / max(1, len(sybils)), 2)
    # if len(attackers) != 0:
    #     result['successful_sybils_per_attacker'] = round(
    #         len(successful_sybils) / len(attackers), 2)
    # else:
    #     result['successful_sybils_per_attacker'] = '__'
    result['better_than_pct'] = bisect(
        honests, max(sybils) if sybils else 0) / len(honests)
    return result


def calculate_successful_honest(ranks_dic):
    honests = []
    sybils = []
    result = {}
    for category in ranks_dic:
        if category in ['Sybil', 'Non Bridge Sybil', 'Bridge Sybil']:
            sybils.extend(ranks_dic[category])
        elif category in ['Seed', 'Honest']:
            honests.extend(ranks_dic[category])
    avg_sybils = sum(sybils) / len(sybils) if sybils else 0
    successful_honest = len([h for h in honests if h > avg_sybils])
    result['no'] = successful_honest
    result['percent'] = successful_honest / len(honests) * 100
    return result


def generate_output(graph, name=''):
    categories = set([node.node_type for node in graph])
    ranks_dic = {}
    for category in categories:
        ranks_dic[category] = [
            node.rank if node.rank else 0 for node in graph if node.node_type == category]
    output = {}
    output['name'] = name
    successful_sybils = calculate_successful_sybils(ranks_dic)
    successful_honests = calculate_successful_honest(ranks_dic)
    # output['Successful Sybils Percentage'] = successful_sybils['successful_sybils_percent_1']
    # output['Successful Sybils Percentage (-10 percent of honests)'] = successful_sybils['successful_sybils_percent_0.9']
    # output['Successful Sybils Percentage (-20 percent of honests)'] = successful_sybils['successful_sybils_percent_0.8']
    # output['Successful Sybils per Attacker'] = successful_sybils['successful_sybils_per_attacker']
    output['No. Successful Honests'] = successful_honests['no']
    output['Successful Honests Percent'] = successful_honests['percent']
    output['Sybils scored >= %'] = successful_sybils['better_than_pct']
    output['Avg Honest - Avg Sybil'] = None
    view_order = ('Seed', 'Honest', 'Attacker',
                  'Bridge Sybil', 'Non Bridge Sybil', 'Sybil')
    for category in view_order:
        if category not in categories:
            continue
        for parameter in ['Max', 'Avg', 'Min']:
            if len(ranks_dic[category]) == 0:
                v = '__'
            elif parameter == 'Min':
                v = min(ranks_dic[category])
            elif parameter == 'Avg':
                v = sum(ranks_dic[category]) / len(ranks_dic[category])
            elif parameter == 'Max':
                v = max(ranks_dic[category])
            output['{0} {1}'.format(parameter, category)] = v
    output['Avg Honest - Avg Sybil'] = output['Avg Honest'] - \
        output.get('Avg Sybil', output.get('Avg Bridge Sybil', 0))
    output['Border'] = find_border(graph)
    return output


def save_graph(file_name, graph):
    with open(file_name, 'w') as f:
        f.write(to_json(graph))


def to_json(graph):
    data = {'nodes': [], 'edges': []}
    for node in graph:
        data['nodes'].append({
            'name': node.name,
            'node_type': node.node_type,
            'groups': node.groups,
            'rank': node.rank,
            'cluster': node.clusters.get('graph', None) if hasattr(node, 'clusters') else None
        })
    for edge in graph.edges:
        weight = graph[edge[0]][edge[1]].get('weight', 1)
        data['edges'].append((edge[0].name, edge[1].name, weight))
    return json.dumps(data)


def load_graph(file_name):
    with open(file_name, 'r') as f:
        data = f.read()
    return from_json(data)


def from_json(data, directed=False):
    data = json.loads(data)
    graph = nx.DiGraph() if directed else nx.Graph()
    nodes = {}
    for node in data['nodes']:
        groups = node['groups'] if node['groups'] else None
        nodes[node['name']] = Node(node['name'], node['node_type'],
                                   groups, node['init_rank'], 0, node['rank'], node['created_at'], node['verifications'])
        graph.add_node(nodes[node['name']])
    graph.add_edges_from([(nodes[edge[0]], nodes[edge[1]])
                          for edge in data['edges']])
    return graph


def zip2dict(f, table):
    zf = zipfile.ZipFile(f)
    fnames = zf.namelist()
    def pattern(fname): return fname.endswith(
        '.data.json') and fname.count('/{}_'.format(table)) > 0
    fname = list(filter(pattern, fnames))[0]
    content = zf.open(fname).read().decode('utf-8')
    ol = [json.loads(line) for line in content.split('\n') if line.strip()]
    d = {}
    for o in ol:
        if o['type'] == 2300:
            d[o['data']['_key']] = o['data']
        elif o['type'] == 2302 and o['data']['_key'] in d:
            del d[o['data']['_key']]
    return dict((d[k]['_id'].replace(table + '/', ''), d[k]) for k in d)


def from_dump(f, directed=False):
    ret = {'nodes': [], 'edges': []}
    hashes = json.loads(
        next(filter(lambda v: v['_key'] == 'VERIFICATIONS_HASHES', records(f, 'variables')))['hashes'])
    verifications_block = sorted([int(block) for block in hashes])[-1]
    user_verifications = {}
    for v in records(f, 'verifications'):
        if v['block'] != verifications_block:
            continue
        if v['user'] not in user_verifications:
            user_verifications[v['user']] = []
        user_verifications[v['user']].append(v['name'])

    seed_groups = {g['_key']: 0 for g in filter(lambda r: r.get('seed'), records(f, 'groups'))}
    ug_data = {}
    for ug in records(f, 'usersInGroups'):
        u = ug['_from']
        g = ug['_to'].replace('groups/', '')
        if u not in ug_data:
            ug_data[u] = {'node_type': 'Honest', 'groups': {}, 'init_rank': 0}
        if g in seed_groups:
            ug_data[u]['groups'][g] = 'Seed'
            ug_data[u]['node_type'] = 'Seed'
            seed_groups[g] += 1
        else:
            ug_data[u]['groups'][g] = 'NonSeed'

    for u in ug_data:
        if ug_data[u]['node_type'] != 'Seed':
            continue
        for g in ug_data[u]['groups']:
            if ug_data[u]['groups'][g] != 'Seed':
                continue
            ug_data[u]['init_rank'] += 1 / seed_groups[g]

    for u in records(f, 'users'):
        temp = ug_data.get(
            u['_id'], {'node_type': 'Honest', 'groups': {}, 'init_rank': 0})
        ret['nodes'].append({
            'node_type': temp['node_type'],
            'init_rank': min(.3, temp['init_rank']),
            'rank': 0,
            'name': u['_key'],
            'groups': temp['groups'],
            'created_at': u['createdAt'],
            'verifications': sorted(user_verifications.get(u['_key'], []))
        })

    connections = {(
        c['_from'].replace('users/', ''),
        c['_to'].replace('users/', '')
    ): c for c in records(f, 'connections')}
    for ft in connections:
        if connections[ft]['level'] not in ('already known', 'recovery'):
            continue
        if directed:
            ret['edges'].append(ft)
        else:
            tf = (ft[1], ft[0])
            tf_level = connections.get(tf, {}).get('level')
            if tf_level in ('already known', 'recovery') and tf not in ret['edges']:
                ret['edges'].append(ft)

    ret['nodes'].sort(key=lambda i: i['name'])
    ret['nodes'].sort(key=lambda i: i['created_at'], reverse=True)
    return json.dumps(ret)


def from_db(arango_server, db_name, directed=False):
    db = ArangoClient(hosts=arango_server).db(db_name)
    ret = {'nodes': [], 'edges': []}
    seed_groups = {}
    for seed_group in db['groups'].find({'seed': True}):
        c = db['usersInGroups'].find({'_to': seed_group['_id']})
        seed_groups[seed_group['_key']] = c.count()

    hashes = json.loads(
        next(filter(lambda v: v['_key'] == 'VERIFICATIONS_HASHES', db['variables']))['hashes'])
    verifications_block = sorted([int(block) for block in hashes])[-1]
    user_verifications = {}
    for v in db['verifications'].find({'block': verifications_block}):
        if v['user'] not in user_verifications:
            user_verifications[v['user']] = []
        user_verifications[v['user']].append(v['name'])

    ug_data = {}
    for ug in db['usersInGroups']:
        u = ug['_from']
        g = ug['_to'].replace('groups/', '')
        if u not in ug_data:
            ug_data[u] = {'node_type': 'Honest', 'groups': {}, 'init_rank': 0}
        if g in seed_groups:
            ug_data[u]['groups'][g] = 'Seed'
            ug_data[u]['node_type'] = 'Seed'
            ug_data[u]['init_rank'] += 1 / seed_groups[g]
        else:
            ug_data[u]['groups'][g] = 'NonSeed'

    for u in db['users']:
        temp = ug_data.get(
            u['_id'], {'node_type': 'Honest', 'groups': {}, 'init_rank': 0})
        ret['nodes'].append({
            'node_type': temp['node_type'],
            'init_rank': min(.3, temp['init_rank']),
            'rank': 0,
            'name': u['_key'],
            'groups': temp['groups'],
            'created_at': u['createdAt'],
            'verifications': sorted(user_verifications.get(u['_key'], []))
        })

    connections = {(
        c['_from'].replace('users/', ''),
        c['_to'].replace('users/', '')
    ): c for c in db['connections']}
    for ft in connections:
        if connections[ft]['level'] not in ('already known', 'recovery'):
            continue
        if directed:
            ret['edges'].append(ft)
        else:
            tf = (ft[1], ft[0])
            tf_level = connections.get(tf, {}).get('level')
            if tf_level in ('already known', 'recovery') and tf not in ret['edges']:
                ret['edges'].append(ft)

    ret['nodes'].sort(key=lambda i: i['name'])
    ret['nodes'].sort(key=lambda i: i['created_at'], reverse=True)
    return json.dumps(ret)


def draw_graph(graph, file_name):
    global GRAPH_TEMPLATE
    if not GRAPH_TEMPLATE:
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        with open(os.path.join(dname, 'templates/graph.html')) as f:
            GRAPH_TEMPLATE = f.read()
    dname = os.path.dirname(file_name)
    if dname and not os.path.exists(dname):
        os.makedirs(dname)
    json_dic = to_json(graph)
    edited_string = GRAPH_TEMPLATE.replace('JSON_GRAPH', json_dic)
    with open(file_name, 'w') as output_file:
        output_file.write(edited_string)
    return edited_string


def draw_compare_graph(graph1, graph2, file_name):
    global COMPARE_GRAPH_TEMPLATE
    if not COMPARE_GRAPH_TEMPLATE:
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        with open(os.path.join(dname, 'templates/compare_graph.html')) as f:
            COMPARE_GRAPH_TEMPLATE = f.read()
    dname = os.path.dirname(file_name)
    if dname and not os.path.exists(dname):
        os.makedirs(dname)
    for node in graph1.nodes:
        node2 = next(filter(lambda n: n.name == node.name, graph2.nodes))
        node.rank = '{0}-{1}'.format(int(node.rank), int(node2.rank))
    graph_json = to_json(graph1)
    edited_string = COMPARE_GRAPH_TEMPLATE.replace('JSON_GRAPH', graph_json)
    with open(file_name, 'w') as output_file:
        output_file.write(edited_string)
    return edited_string


def draw_3d_graph(attacks, algorithms, file_name):
    global GRAPH_3D_TEMPLATE
    if not GRAPH_3D_TEMPLATE:
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        with open(os.path.join(dname, 'templates/graph3d.html')) as f:
            GRAPH_3D_TEMPLATE = f.read()
    dname = os.path.dirname(file_name)
    if dname and not os.path.exists(dname):
        os.makedirs(dname)

    edited_string = GRAPH_3D_TEMPLATE.replace(
        'JSON_GRAPH', json.dumps(attacks)).replace('ALGORITHMS', json.dumps(algorithms))
    with open(file_name, 'w') as output_file:
        output_file.write(edited_string)
    # with open(file_name.replace('.html', '.json'), 'w') as output_file:
    #     output_file.write(json.dumps(attacks))
    return edited_string


def reset_ranks(graph):
    for node in graph:
        node.rank = 0


def load_brightid_graph(data, directed=False):
    if not os.path.exists(data['file_path']):
        os.makedirs(data['file_path'])
    rar_addr = os.path.join(data['file_path'], 'brightid.tar.gz')
    backup_addr = os.path.join(data['file_path'], 'brightid/')
    backup = requests.get(BACKUP_URL)
    with open(rar_addr, 'wb') as f:
        f.write(backup.content)
    shutil.rmtree(backup_addr, ignore_errors=True)
    os.makedirs(backup_addr)
    tarf = tarfile.open(rar_addr, mode='r|gz')
    tarf.extractall(backup_addr)
    tarf.close()
    json_graph = from_dump(os.path.join(backup_addr, 'dump/'), directed)
    graph = from_json(json_graph, directed)
    return graph


def records(backup_addr, table):
    fnames = os.listdir(backup_addr)
    fname = next(filter(lambda fn: fn.startswith(
        f'{table}_') and fn.endswith('.data.json'), fnames))
    recs = []
    with open(os.path.join(backup_addr, fname), 'r') as f:
        for line in f.read().split('\n'):
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec['type'] == 2300:
                recs.append(rec['data'])
            elif rec['type'] == 2302 and rec['data'] in recs:
                recs.remove(rec['data'])
    return recs


def stupid_sybil_border(graph):
    from . import algorithms
    border = 0
    reset_ranks(graph)
    ranker = algorithms.GroupSybilRank(graph)
    ranker.rank()
    attackers = sorted(graph.nodes, key=lambda n: n.rank, reverse=True)
    for attacker in attackers:
        attacker.groups['stupid_sybil'] = 'NonSeed'
        sybil1 = Node('stupid_sybil_1', 'Sybil', set(['stupid_sybil']))
        sybil2 = Node('stupid_sybil_2', 'Sybil', set(['stupid_sybil']))
        graph.add_edge(attacker, sybil1)
        graph.add_edge(attacker, sybil2)
        reset_ranks(graph)
        ranker = algorithms.GroupSybilRank(graph)
        ranker.rank()
        border = max(sybil1.raw_rank, sybil2.raw_rank)
        graph.remove_nodes_from([sybil1, sybil2])
        del attacker.groups['stupid_sybil']
        reset_ranks(graph)
        print('attacker: {}\t type: {}\t border: {}'.format(
            attacker, attacker.node_type, border))
        if border:
            return border


def nonlinear_distribution(graph, ratio, df, dt):
    ranks = [(n, n.rank) for n in graph]
    avg_floating_points = sum(
        [int(('%E' % rank[1]).split('E')[1]) for rank in ranks]) / len(ranks)
    multiplier = 10 ** (-1 * (avg_floating_points - 1))
    nums = [rank[1] * multiplier for rank in ranks]
    counts = {}
    for num in nums:
        counts[int(num)] = counts.get(int(num), 0) + 1
    f = int(len(nums) / 10)
    t = int(-1 * len(nums) / 10)
    navg = sum(sorted(nums)[f:t]) / (.8 * len(nums))
    navg = int(navg)
    max_num = max(nums)
    # find distance from average which include half of numbers
    distance = 0
    while True:
        distance += 1
        count = sum([counts.get(i, 0)
                     for i in range(navg - distance, navg + distance)])
        if count > len(nums) * ratio:
            break
    f, t = navg - distance, navg + distance
    ret = []
    for num in nums:
        if 0 <= num < f:
            num = num * df / f
        elif f <= num < t:
            num = df + (((num - f) / (t - f)) * (dt - df))
        else:
            num = dt + (((num - t) / (max_num - t)) * (100 - dt))
        ret.append(round(num, 2))
    for i, r in enumerate(ranks):
        r[0].rank = ret[i]
    return graph


def linear_distribution(graph):
    ranks = [(n, n.rank) for n in graph]
    max_rank = max(ranks, key=lambda item: item[1])[1]
    min_rank = min(ranks, key=lambda item: item[1])[1]
    for node in graph:
        new_rank = (node.rank - min_rank) * 100 / (max_rank - min_rank)
        node.rank = int(new_rank)
    return graph


def border_based_distribution(graph, border):
    ranks = [(n, n.rank) for n in graph]
    max_rank = max(ranks, key=lambda item: item[1])[1]
    for node, rank in ranks:
        if rank < border:
            new_rank = 9.99 * rank / border
        else:
            new_rank = 90 + 9.99 * (rank - border) / (max_rank - border)
        node.rank = round(new_rank, 2)
    return graph


def z_score_distribution(ranks):
    _mean = np.mean([r[1] for r in ranks])
    _std = np.std([r[1] for r in ranks])
    z_scores = {r[0]: (r[1] - _mean) / _std for r in ranks}
    temp = dict(linear_distribution(
        [r for i, r in enumerate(ranks) if z_scores[r[0]] < 3]))
    new_ranks = [(r[0], temp.get(r[0], 100)) for r in ranks]
    return new_ranks
