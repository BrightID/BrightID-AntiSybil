from bisect import bisect
import networkx as nx
import zipfile
import tarfile
import requests
import json
import csv
import os
from . import algorithms

GRAPH_TEMPLATE = COMPARE_GRAPH_TEMPLATE = None
BACKUP_URL = 'https://storage.googleapis.com/brightid-backups/brightid.tar.gz'


class Node:
    def __init__(self, name, node_type, groups=None, rank=None, raw_rank=None, degree=None):
        self.name = name
        self.node_type = node_type
        self.rank = rank
        self.groups = groups if groups else set()
        self.raw_rank = raw_rank
        self.degree = degree

    def __repr__(self):
        return str(self.name)


def write_output_file(outputs, file_name):
    if len(outputs) == 0:
        return
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))
    rows = [['Results'] + [output['name'] for output in outputs]]
    for title in outputs[0]:
        if title != 'name':
            rows.append([title] + [output.get(title, '') for output in outputs])
    with open(file_name, 'w') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)


def find_border(graph):
    best_border = best_score = 0
    for i in range(100):
        honest_score = len([node for node in graph.nodes if node.node_type in (
            'Honest', 'Seed') and node.rank > i])
        sybil_score = len([node for node in graph.nodes if node.node_type in (
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
    result['better_than_pct'] = bisect(honests, max(sybils) if sybils else 0) / len(honests)
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
    categories = set([node.node_type for node in graph.nodes])
    ranks_dic = {}
    for category in categories:
        ranks_dic[category] = [
            node.rank if node.rank else 0 for node in graph.nodes if node.node_type == category]
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
    for node in graph.nodes():
        data['nodes'].append({
            'name': node.name,
            'node_type': node.node_type,
            'groups': list(node.groups),
            'rank': node.rank
        })
    for edge in graph.edges():
        data['edges'].append((edge[0].name, edge[1].name))
    return json.dumps(data)


def load_graph(file_name):
    with open(file_name, 'r') as f:
        data = f.read()
    return from_json(data)


def from_json(data):
    data = json.loads(data)
    graph = nx.Graph()
    nodes = {}
    for node in data['nodes']:
        groups = set(node['groups']) if node['groups'] else None
        nodes[node['name']] = Node(
            node['name'], node['node_type'], groups, node['rank'])
        graph.add_node(nodes[node['name']])
    graph.add_edges_from([(nodes[edge[0]], nodes[edge[1]])
                          for edge in data['edges']])
    return graph


def zip2dict(f, table):
    zf = zipfile.ZipFile(f)
    fnames = zf.namelist()
    pattern = lambda fname: fname.endswith('.data.json') and fname.count('/{}_'.format(table)) > 0
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


def from_dump(f):
    user_groups = zip2dict(f, 'usersInGroups')
    users = zip2dict(f, 'users')
    groups = zip2dict(f, 'groups')
    connections = zip2dict(f, 'connections')
    ret = {'nodes': [], 'edges': []}
    for u in users:
        users[u] = {'node_type': 'Honest', 'rank': 0, 'name': u , 'groups': [], 'createdAt':users[u]['createdAt']}
        ret['nodes'].append(users[u])
    for user_group in user_groups.values():
        u = user_group['_from'].replace('users/', '')
        g = user_group['_to'].replace('groups/', '')
        users[u]['groups'].append(g)
        if groups[g].get('seed', False):
            users[u]['node_type'] = 'Seed'
    for c in connections.values():
        ret['edges'].append([c['_from'].replace('users/', ''), c['_to'].replace('users/', '')])
    ret['nodes'] = sorted(ret['nodes'], key=lambda i: i['name'])
    ret['nodes'] = sorted(ret['nodes'], key=lambda i: i['createdAt'], reverse=True)
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


def reset_ranks(graph):
    for node in graph.nodes():
        node.rank = 0


def tar_to_zip(fin, fout):
    if os.path.exists(fout):
        os.remove(fout)
    tarf = tarfile.open(fin, mode='r|gz')
    zipf = zipfile.ZipFile(fout, mode='a', compression=zipfile.ZIP_DEFLATED)
    for m in tarf:
        f = tarf.extractfile(m)
        if f:
            zipf.writestr(m.name, f.read())
    tarf.close()
    zipf.close()


def load_brightid_graph(data):
    if not os.path.exists(data['file_path']):
        os.makedirs(data['file_path'])
    rar_addr = os.path.join(data['file_path'], 'brightid.tar.gz')
    zip_addr = os.path.join(data['file_path'], 'brightid.zip')
    backup = requests.get(BACKUP_URL)
    with open(rar_addr, 'wb') as f:
        f.write(backup.content)
    tar_to_zip(rar_addr, zip_addr)
    json_graph = from_dump(zip_addr)
    graph = from_json(json_graph)
    return graph


def stupid_sybil_border(graph):
    reset_ranks(graph)
    ranker = algorithms.GroupSybilRank(graph)
    ranker.rank()
    attacker = max(graph.nodes, key=lambda node: node.rank)
    attacker.groups.add('stupid_sybil')
    sybil1 = Node('stupid_sybil_1', 'Sybil', set(['stupid_sybil']))
    sybil2 = Node('stupid_sybil_2', 'Sybil', set(['stupid_sybil']))
    graph.add_edge(attacker, sybil1)
    graph.add_edge(attacker, sybil2)
    reset_ranks(graph)
    ranker = algorithms.GroupSybilRank(graph)
    ranker.rank()
    border = max(sybil1.raw_rank, sybil2.raw_rank)
    graph.remove_nodes_from([sybil1, sybil2])
    attacker.groups.remove('stupid_sybil')
    reset_ranks(graph)
    return border
