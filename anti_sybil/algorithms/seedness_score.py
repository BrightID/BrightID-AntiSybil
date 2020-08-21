import community
from anti_sybil.utils import *


class SeednessScore():

    def __init__(self, graph, options=None):
        self.graph = graph
        self.options = options

        # remove the unconnected nodes to the main component
        main_component = sorted([comp for comp in nx.connected_components(
            graph)], key=lambda l: len(l), reverse=True)[0]
        for node in list(self.graph):
            if node not in main_component:
                self.graph.remove_node(node)

    def rank(self):
        graph = self.graph.copy()
        for n in graph:
            n.rank = n.init_rank

        for resolution in [.1, .2, .3, .5, .7, 1, 1.3, 1.6, 2]:
            clusters = community.best_partition(
                graph, resolution=resolution, randomize=False)
            cluster_members = {cluster: set() for cluster in clusters.values()}
            cluster_score = dict.fromkeys(clusters.values(), 0)
            for node in clusters:
                cluster = clusters[node]
                cluster_members[cluster].add(node)
                if node.node_type == 'Seed':
                    cluster_score[cluster] += node.init_rank
            for cluster in cluster_members:
                members = cluster_members[cluster]
                rank = cluster_score[cluster] / len(members)
                for member in members:
                    if member.rank < rank:
                        member.rank = rank
        for n in graph:
            n.rank = int(n.rank * 10000)
        return self.graph
