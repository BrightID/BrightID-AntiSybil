import sys
sys.path.append('../')

import os
import json
import time
import requests
import networkx as nx
from threading import Thread
from flask import Flask, redirect, request, make_response
import io

from anti_sybil import algorithms
from anti_sybil.graphs.node import Node
from anti_sybil.utils import *


abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

app = Flask(__name__)
app.secret_key = '80393af8b3d99736c8b0d49d9a9da4ff'

algorithm_options = {
    'min_degree': 5,
    'accumulative': False,
    'weaken_under_min': False,
    'nonlinear_distribution': True,
}

default_graph_addr = './data/brightid.json'


@app.route('/')
def index():
    return redirect('/static/index.html')


def edit_output(graph):
    output = generate_output(graph)
    for key in output:
        if key in ('', ' ', 'Successful Sybils per Attacker'):
            del output[key]
    return output


def add_sybils_to_graph(graph, sybils_defenition):
    nodes_dic = {node.name: node for node in graph.nodes()}
    edges = []
    for i, row in enumerate(sybils_defenition.strip().split('\n')):
        edge = row.strip().split()
        edge = [int(node_name) if node_name.isdigit()
                else node_name for node_name in edge]
        for node_name in edge:
            if node_name not in nodes_dic:
                nodes_dic[node_name] = Node(
                    node_name, 'Sybil', groups=set(['sybils']))
        edges.append((nodes_dic[edge[0]], nodes_dic[edge[1]]))
    graph.add_edges_from(edges)
    sybils = [node for node in nodes_dic.values() if node.node_type == 'Sybil']
    for sybil in sybils:
        for neighbour in graph.neighbors(sybil):
            if neighbour.node_type != 'Sybil':
                # neighbour.node_type = 'Attacker'
                neighbour.groups.add('sybils')


@app.route('/load_default', methods=['GET', 'POST'])
def load_default():
    while not os.path.exists(default_graph_addr):
        time.sleep(1)
    with open(default_graph_addr, 'r') as f:
        graph = from_json(f.read())
    graph_info = edit_output(graph)
    return json.dumps({'success': True, 'graph': to_json(graph), 'graph_info': graph_info})


@app.route('/add_sybils', methods=['GET', 'POST'])
def add_sybils():
    json_graph = request.form['json_graph']
    sybils_defenition = request.form['sybils']
    graph = from_json(json_graph)
    if sybils_defenition:
        add_sybils_to_graph(graph, sybils_defenition)
    ranker = algorithms.SybilGroupRank(graph, algorithm_options)
    ranker.rank()
    graph_info = edit_output(graph)
    json_graph = to_json(graph)
    return json.dumps({'success': True, 'graph': json_graph, 'graph_info': graph_info})


@app.route('/upload_graph_json', methods=['POST'])
def upload_graph_json():
    file = request.files.get('graph_json_file', None)
    if not file:
        return json.dumps({'success': False})
    ext = file.filename.rsplit('.', 1)[1]
    if ext == 'json':
        json_graph = file.stream.read()
    elif ext == 'zip':
        f = io.BytesIO(file.stream.read())
        json_graph = from_dump(f)
    else:
        return json.dumps({'success': False})
    graph = from_json(json_graph)
    reset_ranks(graph)
    ranker = algorithms.SybilGroupRank(graph, algorithm_options)
    ranker.rank()
    graph_info = edit_output(graph)
    return json.dumps({'success': True, 'graph': to_json(graph), 'graph_info': graph_info})


@app.route('/save_json_file', methods=['GET', 'POST'])
def save_json_file():
    graph_json = request.form['json_file']
    response = make_response(graph_json)
    response.headers["Content-Disposition"] = "attachment; filename=graph.json"
    response.headers["Content-type"] = "application/json"
    return response


@app.route('/new_graph', methods=['GET', 'POST'])
def new_graph():
    form_data = request.form
    graph = graphs.generators.group_based.generate({
        'num_groups': int(form_data['num_groups']),
        'num_seed_groups': int(form_data['num_seed_groups']),
        'min_group_nodes': int(form_data['min_group_nodes']),
        'max_group_nodes': int(form_data['max_group_nodes']),
        'max_known_ratio': float(form_data['max_known_ratio']),
        'avg_known_ratio': float(form_data['avg_known_ratio']),
        'min_known_ratio': float(form_data['min_known_ratio']),
        'num_seed_nodes': int(form_data['num_seed_nodes']),
        'num_attacker_to_num_honest': float(form_data['num_attacker_to_num_honest']),
        'num_sybil_to_num_attacker': int(form_data['num_sybil_to_num_attacker']),
        'sybil_to_attackers_con': float(form_data['sybil_to_attackers_con']),
        'num_joint_node': int(form_data['num_joint_node']),
        'num_inter_group_con': int(form_data['num_inter_group_con'])
    })
    ranker = algorithms.SybilGroupRank(graph, algorithm_options)
    ranker.rank()
    graph_info = edit_output(graph)
    json_graph = to_json(graph)
    return json.dumps({'success': True, 'graph': json_graph, 'graph_info': graph_info})


def gen_default():
    if not os.path.exists('./data/'):
        os.makedirs('./data/')
    backup = requests.get(
        'https://storage.googleapis.com/brightid-backups/brightid.tar.gz')
    with open('./data/brightid.tar.gz', 'wb') as f:
        f.write(backup.content)
    tar_to_zip('./data/brightid.tar.gz', './data/brightid.zip')
    json_graph = from_dump('./data/brightid.zip')
    graph = from_json(json_graph)
    # find stupid sybil border
    reset_ranks(graph)
    ranker = algorithms.SybilGroupRank(graph)
    ranker.rank()
    attacker = max(graph.nodes, key=lambda node: node.rank)
    attacker.groups.add('stupid_sybil')
    sybil1 = graphs.node.Node('stupid_sybil_1', 'Sybil', set(['stupid_sybil']))
    sybil2 = graphs.node.Node('stupid_sybil_2', 'Sybil', set(['stupid_sybil']))
    graph.add_edge(attacker, sybil1)
    graph.add_edge(attacker, sybil2)
    reset_ranks(graph)
    ranker = algorithms.SybilGroupRank(graph)
    ranker.rank()
    border = max(sybil1.raw_rank, sybil2.raw_rank)
    graph.remove_nodes_from([sybil1, sybil2])
    attacker.groups.remove('stupid_sybil')
    # SybilGroupRank with the stupid sybil border option
    reset_ranks(graph)
    ranker = algorithms.SybilGroupRank(graph, {
        'stupid_sybil_border': border
    })
    ranker.rank()
    with open(default_graph_addr, 'w') as f:
        f.write(to_json(ranker.graph))
    return True


def main():
    Thread(target = gen_default).start()
    app.run(debug=True, host='127.0.0.1', port=8082, threaded=True)


if __name__ == '__main__':
    main()
