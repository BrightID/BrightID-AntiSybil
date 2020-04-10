import sys
sys.path.append('../')

from anti_sybil.utils import *
import algorithms
import os

OUTPUT_FOLDER = './outputs/repeatability_test/'

outputs = []
for i in range(5):
    g = graphs.generators.brightid_backup.generate({
        'file_path': os.path.abspath('./outputs/repeatability_test/temp/')
    })
    reset_ranks(g)
    ranker = algorithms.SybilGroupRank(g)
    ranker.rank()
    outputs.append(generate_output(ranker.graph, 'SybilGroupRank'))

write_output_file(outputs, os.path.join(OUTPUT_FOLDER, 'result.csv'))
