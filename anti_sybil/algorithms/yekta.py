import community
from anti_sybil.utils import *

BORDERS = [3, 8, 13, 20, 30]

class Yekta():

    def __init__(self, graph, options=None):
        self.graph = graph
        self.options = options

        # remove the unconnected nodes to the main component
        main_component = sorted([comp for comp in nx.connected_components(
            graph)], key=lambda l: len(l), reverse=True)[0]
        for node in list(self.graph):
            if node not in main_component:
                self.graph.remove_node(node)

    def check_seedness(self):
        clusters = community.best_partition(
            self.graph, resolution=2, randomize=False)
        cluster_members = {cluster: set() for cluster in clusters.values()}
        for node in clusters:
            cluster = clusters[node]
            cluster_members[cluster].add(node)
        for cluster in cluster_members:
            members = cluster_members[cluster]
            members = sorted(members, key=lambda m: m.created_at)
            init_rank = sum([m.init_rank for m in members])
            # this means for each seed group in a cluster 100 members can be passed
            limit = init_rank / 0.01
            for i in range(len(members)):
                members[i].has_enough_seedness = (i < limit)

    def rank(self):
        self.check_seedness()
        graph = self.graph.copy()

        for resolution in [.1, .2, .3, .5, .7, 1, 1.3, 1.6, 2]:
            # clustering the nodes
            clusters = community.best_partition(
                graph, resolution=resolution, randomize=False)
            cluster_members = {cluster: set() for cluster in clusters.values()}
            for node in clusters:
                cluster = clusters[node]
                cluster_members[cluster].add(node)

            # find the edges both sides are inside the cluster for all clusters
            inside_edges = {}
            for cluster in cluster_members:
                members = cluster_members[cluster]
                inside_edges[cluster] = set()
                for m in members:
                    # ignore members without enough seedness
                    if not m.has_enough_seedness:
                        continue
                    inside_neighbors = set(graph.neighbors(m)) & members
                    for n in inside_neighbors:
                        # ignore neighbors without enough seedness
                        if not n.has_enough_seedness:
                            continue
                        # ignore duplicate edges
                        if (n, m) in inside_neighbors:
                            continue
                        inside_edges[cluster].add((m, n))

            # calculate the weighted average of the number of inside edges per cluster
            num_inside_edges = sum([len(inside_edges[cluster])
                                    for cluster in inside_edges])
            order = len([n for n in graph if n.has_enough_seedness])
            avg = num_inside_edges / order

            # decrease the weight for inside edges for the clusters
            # that their number of inside edges are more than average
            for cluster in cluster_members:
                edge_per_node = len(
                    inside_edges[cluster]) / len(cluster_members[cluster])
                if edge_per_node > avg:
                    weight = avg / edge_per_node
                    for f, t in inside_edges[cluster]:
                        old_weight = graph[f][t].get('weight', 1)
                        graph[f][t]['weight'] = min(weight, old_weight)

        for n in graph:
            n.rank = 0
        for i, border in enumerate(BORDERS):
            step = i + 1
            for node in graph:
                if step - node.rank > 1:
                    continue
                num = 0
                for neighbor in graph.neighbors(node):
                    if not neighbor.has_enough_seedness:
                        continue
                    w = graph[node][neighbor].get('weight', 1)
                    # weaken weight if the neighbor has low rank
                    # use max(1, ) because we may reach neighbor before node
                    # and it has current step as rank in this step
                    num += w / max(1, (step - neighbor.rank))
                if num >= border:
                    node.rank = step
        return self.graph
