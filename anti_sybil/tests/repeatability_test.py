import sys
sys.path.append('../')

from anti_sybil.utils import *
import algorithms
import os

OUTPUT_FOLDER = './outputs/repeatability_test/'


def find_border(graph):
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
    return border


def main():
    outputs = []
    for i in range(5):
        graph = graphs.generators.brightid_backup.generate({
            'file_path': os.path.abspath('./outputs/repeatability_test/temp/')
        })
        border = find_border(graph)
        reset_ranks(graph)
        ranker = algorithms.SybilGroupRank(graph, {
            'stupid_sybil_border': border
        })
        ranker.rank()
        outputs.append(generate_output(ranker.graph, 'SybilGroupRank'))

    write_output_file(outputs, os.path.join(OUTPUT_FOLDER, 'result.csv'))


if __name__ == '__main__':
    main()