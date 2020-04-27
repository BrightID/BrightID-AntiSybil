# compare the result of the old SybilGroupRank algorithm and new one

from anti_sybil import utils
from anti_sybil import utils_v01
from anti_sybil import algorithms
from anti_sybil.graphs.node import Node
import requests
import random
import copy
import os

BACKUP_URL = 'https://storage.googleapis.com/brightid-backups/brightid.tar.gz'
OUTPUT_FOLDER = './outputs/group_target_attack/'


if not os.path.exists(os.path.join(OUTPUT_FOLDER, 'temp')):
    os.makedirs(os.path.join(OUTPUT_FOLDER, 'temp'))
rar_addr = os.path.join(OUTPUT_FOLDER, 'temp', 'brightid.tar.gz')
zip_addr = os.path.join(OUTPUT_FOLDER, 'temp', 'brightid.zip')
backup = requests.get(BACKUP_URL)
with open(rar_addr, 'wb') as f:
    f.write(backup.content)
utils.tar_to_zip(rar_addr, zip_addr)

# load graph from the backup old version
json_graph = utils_v01.from_dump(zip_addr)
graph = utils_v01.from_json(json_graph)


# selecting TOP ranked nodes as target of attack
NUM_ATTACKERS = 1
NUM_SYBILS = 20
NUM_GROUPS = 50
INNER_SYBILS_CONN = 200
TOP = 1
edges = []
sybils = []
nodes = sorted(list(graph.nodes), key=lambda n: n.rank, reverse=True)
nodes_dic = dict([(node.name, node) for node in nodes])
# making attacker node
nodes_dic['a-1'] = Node('a-1',
                        'Attacker', groups=set(['target_attack']))
# connecting attacker to top ranked node
edges.append((nodes_dic['a-1'], nodes_dic[nodes[0].name]))
# making sybils and connecting them to attackers
for i in range(NUM_SYBILS):
    nodes_dic['s-{0}'.format(i)] = Node('s-{0}'.format(i),
                                        'Sybil', groups=set(['target_attack']))
    sybils.append('s-{0}'.format(i))
    edges.append((nodes_dic['s-{0}'.format(i)], nodes_dic['a-1']))

# connecting sybils together
for i in range(INNER_SYBILS_CONN):
    edges.append((nodes_dic[random.choice(sybils)],
                  nodes_dic[random.choice(sybils)]))

# making sybils groups
for i in range(NUM_GROUPS):
    nodes_dic['a-1'].groups.add('stupid_sybil_{}'.format(i))
    nodes_dic[random.choice(sybils)].groups.add('stupid_sybil_{}'.format(i))
    nodes_dic[random.choice(sybils)].groups.add('stupid_sybil_{}'.format(i))

# updating graph
graph.add_edges_from(edges)
utils.reset_ranks(graph)

# OldSybilGroupRank with the stupid sybil border option
utils.reset_ranks(graph)
ranker = algorithms.V1SybilGroupRank(graph)
ranker.rank()
graph1 = copy.deepcopy(ranker.graph)
utils.draw_graph(graph1, os.path.join(OUTPUT_FOLDER, 'v1.html'))
output1 = utils.generate_output(
    graph1, 'V1 SybilGroupRank\ntarget attack by making group')

# SybilGroupRank with the stupid sybil border option
utils.reset_ranks(graph)
ranker = algorithms.SybilGroupRank(graph)
ranker.rank()
graph2 = copy.deepcopy(ranker.graph)
utils.draw_graph(graph2, os.path.join(OUTPUT_FOLDER, 'v2.html'))
output2 = utils.generate_output(
    graph2, 'SybilGroupRank\ntarget attack by making group')

# Generate result
utils.draw_compare_graph(graph1, graph2, os.path.join(
    OUTPUT_FOLDER, 'compare_graph.html'))
utils.write_output_file([output1, output2], os.path.join(
    OUTPUT_FOLDER, 'result.csv'))
