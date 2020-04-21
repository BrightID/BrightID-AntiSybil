from anti_sybil.utils import *
from anti_sybil import algorithms
import xmltodict
import requests
import os

BACKUP_URL = 'http://storage.googleapis.com/brightid-backups/'
OUTPUT_FOLDER = './outputs/24_hours_test/'


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
    if not os.path.exists('{}temp'.format(OUTPUT_FOLDER)):
        os.makedirs('{}temp'.format(OUTPUT_FOLDER))
    r = requests.get(BACKUP_URL)
    backups = xmltodict.parse(r.text)['ListBucketResult']['Contents']
    backups = sorted(backups, key=lambda i: i['LastModified'], reverse=True)
    urls = []
    for backup in backups:
        if len(urls) > 23:
            break
        if not backup['Key'].startswith('brightid_'):
            continue
        urls.append([backup['Key'], backup['LastModified']])
    print(urls)
    for i, l in enumerate(urls):
        rar_addr = '{0}temp/brightid{1}.tar.gz'.format(OUTPUT_FOLDER, i)
        zip_addr = '{0}temp/brightid{1}.zip'.format(OUTPUT_FOLDER, i)
        r = requests.get(requests.compat.urljoin(BACKUP_URL, l[0]))
        with open(rar_addr, 'wb') as f:
            f.write(r.content)
        tar_to_zip(rar_addr, zip_addr)
    for i, l in enumerate(urls):
        zip_addr = '{0}temp/brightid{1}.zip'.format(OUTPUT_FOLDER, i)
        json_graph = from_dump(zip_addr)
        graph = from_json(json_graph)
        border = find_border(graph)
        print('border', border)
        reset_ranks(graph)
        ranker = algorithms.SybilGroupRank(graph, {
            'stupid_sybil_border': border
        })
        ranker.rank()

        outputs.append(generate_output(
            ranker.graph, 'SybilRank\n{}'.format(l[1])))
        draw_graph(ranker.graph, os.path.join(
            OUTPUT_FOLDER, 'graph{}.html'.format(i)))

    write_output_file(outputs, os.path.join(
        OUTPUT_FOLDER, 'result.csv'))


if __name__ == '__main__':
    main()
