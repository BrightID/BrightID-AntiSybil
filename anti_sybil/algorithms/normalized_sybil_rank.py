import community
import networkx as nx
from . import sybil_rank


def distance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)**.5


class NormalizedSybilRank():

    def __init__(self, graph, options=None):
        self.graph = graph
        self.options = options if options else {}

        # remove the unconnected nodes to the main component
        main_component = sorted([comp for comp in nx.connected_components(
            graph)], key=lambda l: len(l), reverse=True)[0]
        for node in list(self.graph):
            if node not in main_component:
                self.graph.remove_node(node)

    def normalize(self, graph):
        original_graph = graph.copy()
        seeds = [n for n in original_graph if n.node_type == 'Seed']

        # connect each node to 8 nearest neighbors that are in the same cluster
        clusters = community.best_partition(
            graph, resolution=.3, randomize=False)
        points = nx.spring_layout(graph, iterations=50, dim=3, random_state=3)
        non_seeds = set(points) - set(seeds)
        non_seeds = sorted(non_seeds, key=lambda n: original_graph.degree(n))
        for node in non_seeds:
            candidates = [
                n for n in original_graph if clusters[n] == clusters[node]]
            candidates = [n for n in candidates if n not in seeds]
            candidates = [n for n in candidates if set(
                original_graph.neighbors(n)) & set(original_graph.neighbors(node))]
            candidates = sorted(candidates, key=lambda n: distance(
                points[node], points[n]))[1:9]
            for n in candidates:
                graph.add_edge(node, n)

        cluster_members = {cluster: set() for cluster in clusters.values()}
        for node in clusters:
            cluster = clusters[node]
            cluster_members[cluster].add(node)

        # each non-seed node can connect to at most 4 seeds
        limit = 4
        for node in original_graph:
            if node.node_type == 'Seed':
                continue
            s_neighbors = set(original_graph.neighbors(node)) & set(seeds)
            s_neighbors = sorted(
                s_neighbors, key=lambda s: original_graph.degree(s), reverse=True)
            for sn in s_neighbors[limit:]:
                graph.remove_edge(node, sn)

        # seeds can not have more than 4 connections in their own clusters and 2 in other clusters
        for seed in seeds:
            for cluster in cluster_members:
                cluster_neighbors = (cluster_members[cluster] & set(
                    graph.neighbors(seed))) - set(seeds)
                cluster_neighbors = sorted(
                    cluster_neighbors, key=lambda n: original_graph.degree(n), reverse=True)
                limit = 4 if cluster == clusters[seed] else 2
                for neighbor in cluster_neighbors[limit:]:
                    graph.remove_edge(seed, neighbor)

    def rank(self):
        graph = self.graph.copy()
        self.normalize(graph)
        ranker = sybil_rank.SybilRank(graph, self.options)
        ranker.rank()
        return self.graph
