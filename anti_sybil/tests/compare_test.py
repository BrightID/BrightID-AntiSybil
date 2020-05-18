import os
import copy
from anti_sybil import algorithms
from anti_sybil.utils import *

# This script helps to compare the result of different anti-sybil algorithms by drawing a compare graph.

OUTPUT_FOLDER = './outputs/compare_test/'

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# load graph from the backup
graph = load_brightid_graph({
    'file_path': os.path.abspath(os.path.join(OUTPUT_FOLDER, 'temp'))
})

# SybilRank
reset_ranks(graph)
ranker = algorithms.SybilRank(graph)
ranker.rank()
graph1 = copy.deepcopy(ranker.graph)
output1 = generate_output(
    graph1, 'SybilRank')
draw_graph(ranker.graph, os.path.join(OUTPUT_FOLDER, 'graph_v01.html'))


# GroupSybilRank
border = stupid_sybil_border(graph)
reset_ranks(graph)
ranker = algorithms.GroupSybilRank(graph, {
    'stupid_sybil_border': border
})
ranker.rank()
graph2 = copy.deepcopy(ranker.graph)
output2 = generate_output(
    graph2, 'GroupSybilRank')
draw_graph(ranker.graph, os.path.join(OUTPUT_FOLDER, 'graph_v02.html'))

# Generate result
write_output_file([output1, output2], os.path.join(
    OUTPUT_FOLDER, 'result.csv'))
draw_compare_graph(graph1, graph2, os.path.join(
    OUTPUT_FOLDER, 'compare_graph.html'))
