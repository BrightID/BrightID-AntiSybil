from anti_sybil import utils
from anti_sybil import utils_v01
from anti_sybil import graphs
from anti_sybil import algorithms
import xmltodict
import requests
import os

BACKUP_URL = 'http://storage.googleapis.com/brightid-backups/'
OUTPUT_FOLDER = './outputs/24_hours_test/'


def find_border_old(graph):
    utils_v01.reset_ranks(graph)
    ranker = algorithms.V1SybilGroupRank(graph)
    ranker.rank()
    attacker = max(graph.nodes, key=lambda node: node.rank)
    attacker.groups.add('stupid_sybil')
    sybil1 = graphs.node.Node('stupid_sybil_1', 'Sybil', set(['stupid_sybil']))
    sybil2 = graphs.node.Node('stupid_sybil_2', 'Sybil', set(['stupid_sybil']))
    graph.add_edge(attacker, sybil1)
    graph.add_edge(attacker, sybil2)
    utils_v01.reset_ranks(graph)
    ranker = algorithms.V1SybilGroupRank(graph)
    ranker.rank()
    border = max(sybil1.raw_rank, sybil2.raw_rank)
    graph.remove_nodes_from([sybil1, sybil2])
    attacker.groups.remove('stupid_sybil')
    return border


def find_border(graph):
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
    return border


def main():
    outputs = []
    scores_dic = None
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
        utils.tar_to_zip(rar_addr, zip_addr)

    # old version
    for i, l in enumerate(urls):
        zip_addr = '{0}temp/brightid{1}.zip'.format(OUTPUT_FOLDER, i)
        json_graph = utils_v01.from_dump(zip_addr)
        graph = utils_v01.from_json(json_graph)
        if not scores_dic:
            scores_dic = {k.name: [] for k in list(graph.nodes)}
        border = find_border_old(graph)
        print('border', border)
        utils.reset_ranks(graph)
        ranker = algorithms.V1SybilGroupRank(graph, {
            'stupid_sybil_border': border
        })
        ranker.rank()
        for n in ranker.graph.nodes():
            if n.name in scores_dic:
                scores_dic[n.name].append(n.rank)

        outputs.append(utils_v01.generate_output(
            ranker.graph, 'SybilGroupRank v1\n{}'.format(l[1])))
        utils_v01.draw_graph(ranker.graph, os.path.join(
            OUTPUT_FOLDER, 'v1_{}.html'.format(i)))
    utils_v01.write_output_file(outputs, os.path.join(
        OUTPUT_FOLDER, 'v1.csv'))

    for n in scores_dic:
        print(n)
        print(scores_dic[n])
        print('_v1_' * 30)

    # new version
    scores_dic = None
    outputs = []
    for i, l in enumerate(urls):
        zip_addr = '{0}temp/brightid{1}.zip'.format(OUTPUT_FOLDER, i)
        json_graph = utils.from_dump(zip_addr)
        graph = utils.from_json(json_graph)
        if not scores_dic:
            scores_dic = {k.name: [] for k in list(graph.nodes)}
        border = find_border(graph)
        print('border', border)
        utils.reset_ranks(graph)
        ranker = algorithms.SybilGroupRank(graph, {
            'stupid_sybil_border': border
        })
        ranker.rank()
        for n in ranker.graph.nodes():
            if n.name in scores_dic:
                scores_dic[n.name].append(n.rank)

        outputs.append(utils.generate_output(
            ranker.graph, 'SybilGroupRank v2\n{}'.format(l[1])))
        utils.draw_graph(ranker.graph, os.path.join(
            OUTPUT_FOLDER, 'v2_{}.html'.format(i)))
    utils.write_output_file(outputs, os.path.join(
        OUTPUT_FOLDER, 'v2.csv'))

    for n in scores_dic:
        print(n)
        print(scores_dic[n])
        print('_v2_' * 30)


if __name__ == '__main__':
    main()
