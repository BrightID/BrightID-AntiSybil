import copy
import os
from anti_sybil import algorithms
from anti_sybil.utils import *


OUTPUT_FOLDER = './outputs/compare_test/'

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# load graph from the backup
graph = load_brightid_graph({
    'file_path': os.path.abspath(os.path.join(OUTPUT_FOLDER, 'temp'))
})

# SybilGroupRank V01 with the stupid sybil border option
border = stupid_sybil_border(graph)
reset_ranks(graph)
ranker = algorithms.V1SybilGroupRank(graph, {
    'stupid_sybil_border': border
})
ranker.rank()
graph1 = copy.deepcopy(ranker.graph)
output1 = generate_output(
    graph1, 'SybilGroupRank V01\n(stupid sybil border)')
draw_graph(ranker.graph, os.path.join(OUTPUT_FOLDER, 'graph_v01.html'))


# SybilGroupRank with the stupid sybil border option
border = stupid_sybil_border(graph)
reset_ranks(graph)
ranker = algorithms.SybilGroupRank(graph, {
    'cleaning': True
})
ranker.rank()
graph2 = copy.deepcopy(ranker.graph)
output2 = generate_output(
    graph2, 'SybilGroupRank\n(stupid sybil border)')
draw_graph(ranker.graph, os.path.join(OUTPUT_FOLDER, 'graph_v02.html'))

# Generate result
write_output_file([output1, output2], os.path.join(
    OUTPUT_FOLDER, 'result.csv'))
draw_compare_graph(graph1, graph2, os.path.join(
    OUTPUT_FOLDER, 'compare_graph.html'))
