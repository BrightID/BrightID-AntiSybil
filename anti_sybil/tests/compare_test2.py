# compare the result of SybilGroupRank algorithm with SybilRank

from anti_sybil.utils import *
from anti_sybil import algorithms
import copy
import os

OUTPUT_FOLDER = './outputs/compare_test2/'

# load graph from the backup
graph = graphs.generators.brightid_backup.generate({
    'file_path': os.path.abspath(os.path.join(OUTPUT_FOLDER, 'temp'))
})

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
print('*' * 100)
print('border1', border)

# SybilGroupRank with the stupid sybil border option
reset_ranks(graph)
ranker = algorithms.SybilGroupRank(graph, {
    'stupid_sybil_border': border
})
ranker.rank()
graph1 = copy.deepcopy(ranker.graph)
draw_graph(graph1, os.path.join(OUTPUT_FOLDER, 'graph1.html'))
output1 = generate_output(graph1, 'SybilGroupRank\n(stupid sybil border)')

# SybilRank
reset_ranks(graph)
ranker = algorithms.SybilRank(graph)
ranker.rank()
output2 = generate_output(ranker.graph, 'SybilRank')
draw_graph(ranker.graph, os.path.join(OUTPUT_FOLDER, 'graph2.html'))

# Generate result
draw_compare_graph(graph1, ranker.graph, os.path.join(
    OUTPUT_FOLDER, 'compare_graph.html'))
write_output_file([output1, output2], os.path.join(
    OUTPUT_FOLDER, 'result.csv'))
