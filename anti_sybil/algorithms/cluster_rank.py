import community
from anti_sybil.utils import *


class ClusterRank():

    def __init__(self, graph, options=None):
        self.graph = graph
        self.options = options

    def rank(self):
        graph = self.graph.copy()

        for step in range(5):
            # clustering the remained nodes in this step
            clusters = community.best_partition(
                graph, resolution=.3, randomize=False)
            cluster_members = {cluster: set() for cluster in clusters.values()}
            clusters_seedness = {cluster: 0 for cluster in clusters.values()}
            for node in clusters:
                cluster = clusters[node]
                cluster_members[cluster].add(node)
                clusters_seedness[cluster] += node.init_rank

            # count number of clusters knowing nodes
            seedness_border = 1 / 10
            repeating_border = 3
            for cluster in cluster_members:
                members = cluster_members[cluster]
                for m in members:
                    neighboring_clusters = set()
                    m.score = 0
                    for neighbor in graph.neighbors(m):
                        if neighbor in members:
                            continue
                        neighboring_cluster = clusters[neighbor]
                        # ignore duplicate clusters
                        if neighboring_cluster in neighboring_clusters:
                            continue
                        # ignore clusters that do not have enough seeds
                        if clusters_seedness[neighboring_cluster] < seedness_border:
                            continue
                        # weakening nodes that are neighbors for many members of a cluster
                        num_neighbors_in_cluster = len(
                            set(graph.neighbors(neighbor)) & members)
                        if num_neighbors_in_cluster > repeating_border:
                            m.score += repeating_border / num_neighbors_in_cluster
                        else:
                            m.score += 1
                        neighboring_clusters.add(neighboring_cluster)
                    m.clusters = {'graph': str(cluster)}

            # 1/2 nodes are passed based on the number of neighboring clusters and its degree
            def score(n): return (m.score, graph.degree(n))
            nodes = sorted(graph, key=score, reverse=True)
            index = len(nodes) // 2
            passeds = nodes[:index]
            print('border: {}, passeds: {}'.format(
                score(nodes[index]), len(passeds)))
            for node in graph:
                if node in clusters:
                    node.rank = '#{}-{}'.format(clusters[node], score(node))
                else:
                    node.rank = ''
            draw_graph(
                graph, './outputs/simple_attacks/{}.html'.format(step + 1))

            # remove the nodes that are not verified in this step
            for node in list(graph):
                node.rank = step + 1
                if node not in passeds:
                    graph.remove_node(node)

        return self.graph
