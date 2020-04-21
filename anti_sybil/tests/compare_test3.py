from anti_sybil.utils import *
from anti_sybil import algorithms
import copy
import os


OUTPUT_FOLDER = './outputs/compare_test3/'


def stupid_sybil_border(graph):
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
    reset_ranks(graph)
    return border


# load graph from the backup
graph = graphs.generators.brightid_backup.generate({
    'file_path': os.path.abspath(os.path.join(OUTPUT_FOLDER, 'temp'))
})

# SybilGroupRank with the stupid sybil border option without cleaning
border = stupid_sybil_border(graph)
reset_ranks(graph)
ranker = algorithms.SybilGroupRank(graph, {
    'stupid_sybil_border': border
})
ranker.rank()
graph1 = copy.deepcopy(ranker.graph)
output1 = generate_output(
    graph1, 'SybilGroupRank\n(stupid sybil border)')
draw_graph(ranker.graph, os.path.join(OUTPUT_FOLDER, 'graph1.html'))


# SybilGroupRank with the stupid sybil border option with cleaning
# remove the groups with the same members
# don't count intergroup connections as groups connection
# an edge only count once as group connection
border = stupid_sybil_border(graph)
reset_ranks(graph)
ranker = algorithms.SybilGroupRank(graph, {
    'cleaning': True
})
ranker.rank()
graph2 = copy.deepcopy(ranker.graph)
output2 = generate_output(
    graph2, 'SybilGroupRank\n(stupid sybil border)\ncleaning')
draw_graph(ranker.graph, os.path.join(OUTPUT_FOLDER, 'graph2.html'))

# Generate result
write_output_file([output1, output2], os.path.join(
    OUTPUT_FOLDER, 'result.csv'))
draw_compare_graph(graph1, graph2, os.path.join(
    OUTPUT_FOLDER, 'regular_cleaned.html'))
