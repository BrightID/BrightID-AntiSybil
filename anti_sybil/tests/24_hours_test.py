import xmltodict
import requests
import os
from anti_sybil import algorithms
from anti_sybil.utils import *

BACKUP_URL = 'http://storage.googleapis.com/brightid-backups/'
OUTPUT_FOLDER = './outputs/24_hours_test/'


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
        if not scores_dic:
            scores_dic = {k.name: [] for k in list(graph.nodes)}
        border = stupid_sybil_border(graph)
        print('border', border)
        reset_ranks(graph)
        ranker = algorithms.SybilGroupRank(graph, {
            'stupid_sybil_border': border
        })
        ranker.rank()
        for n in ranker.graph.nodes():
            if n.name in scores_dic:
                scores_dic[n.name].append(n.rank)

        outputs.append(generate_output(
            ranker.graph, 'SybilRank\n{}'.format(l[1])))
        draw_graph(ranker.graph, os.path.join(
            OUTPUT_FOLDER, 'graph{}.html'.format(i)))
    write_output_file(outputs, os.path.join(
        OUTPUT_FOLDER, 'result.csv'))

    for n in scores_dic:
        print(n)
        print(scores_dic[n])
        print('*' * 100)


if __name__ == '__main__':
    main()
