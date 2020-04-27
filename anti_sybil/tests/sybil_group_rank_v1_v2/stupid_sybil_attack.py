# compare the result of the V1 SybilGroupRank algorithm with stupid sybil border option and V2

from anti_sybil import utils
from anti_sybil import utils_v01
from anti_sybil import algorithms
from anti_sybil import graphs
import copy
import os
import requests

BACKUP_URL = 'https://storage.googleapis.com/brightid-backups/brightid.tar.gz'
OUTPUT_FOLDER = './outputs/stupid_sybil_attack/'


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

# find stupid sybil border old version
utils.reset_ranks(graph)
ranker = algorithms.V1SybilGroupRank(graph)
ranker.rank()
attacker = max(graph.nodes, key=lambda node: node.rank)
attacker.groups.add('stupid_sybil')
sybil1 = graphs.node.Node('stupid_sybil_1', 'Sybil', set(['stupid_sybil']))
sybil2 = graphs.node.Node('stupid_sybil_2', 'Sybil', set(['stupid_sybil']))
graph.add_edge(attacker, sybil1)
graph.add_edge(attacker, sybil2)
utils.reset_ranks(graph)
ranker = algorithms.V1SybilGroupRank(graph)
ranker.rank()
border = max(sybil1.raw_rank, sybil2.raw_rank)
graph.remove_nodes_from([sybil1, sybil2])
attacker.groups.remove('stupid_sybil')
print('*' * 100)
print('border1', border)

# V1 SybilGroupRank with the stupid sybil border option
utils.reset_ranks(graph)
ranker = algorithms.V1SybilGroupRank(graph, {
    'stupid_sybil_border': border
})
ranker.rank()
graph1 = copy.deepcopy(ranker.graph)
utils.draw_graph(graph1, os.path.join(OUTPUT_FOLDER, 'v1.html'))
output1 = utils.generate_output(
    graph1, 'SybilGroupRank v1\n(stupid sybil border)')

# load graph from the backup new version
json_graph = utils.from_dump(zip_addr)
graph = utils.from_json(json_graph)

# find stupid sybil border new version
utils.reset_ranks(graph)
ranker = algorithms.SybilGroupRank(graph)
ranker.rank()
attacker = max(graph.nodes, key=lambda node: node.rank)
attacker.groups.add('stupid_sybil')
sybil1 = graphs.node.Node('stupid_sybil_1', 'Sybil', set(['stupid_sybil']))
sybil2 = graphs.node.Node('stupid_sybil_2', 'Sybil', set(['stupid_sybil']))
graph.add_edge(attacker, sybil1)
graph.add_edge(attacker, sybil2)
utils.reset_ranks(graph)
ranker = algorithms.SybilGroupRank(graph)
ranker.rank()
border = max(sybil1.raw_rank, sybil2.raw_rank)
graph.remove_nodes_from([sybil1, sybil2])
attacker.groups.remove('stupid_sybil')
print('*' * 100)
print('border', border)

# SybilGroupRank with the stupid sybil border option
utils.reset_ranks(graph)
ranker = algorithms.SybilGroupRank(graph, {
    'stupid_sybil_border': border
})
ranker.rank()
graph2 = copy.deepcopy(ranker.graph)
utils.draw_graph(graph2, os.path.join(OUTPUT_FOLDER, 'v2.html'))
output2 = utils.generate_output(
    graph2, 'SybilGroupRank v2\n(stupid sybil border)')

# Generate result
utils.draw_compare_graph(graph1, graph2, os.path.join(
    OUTPUT_FOLDER, 'compare_graph.html'))
utils.write_output_file([output1, output2], os.path.join(
    OUTPUT_FOLDER, 'result.csv'))
