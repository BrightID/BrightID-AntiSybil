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

    def check_seedness(self, graph):
        clusters = community.best_partition(
            graph, resolution=2, randomize=False)
        cluster_members = {cluster: set() for cluster in clusters.values()}
        for node in clusters:
            cluster = clusters[node]
            cluster_members[cluster].add(node)
            # node.clusters = {'graph': cluster}
        for cluster in cluster_members:
            members = cluster_members[cluster]
            members = sorted(members, key=lambda m: m.created_at)
            init_rank = sum([m.init_rank for m in members])
            # This means for each seed group in a cluster 50 members can be passed
            # and it will increase by increasing the number of seeds in the cluster
            if init_rank > 1:
                init_rank = init_rank ** 1.7
            limit = int(init_rank / 0.02)
            for member in members[limit:]:
                graph.remove_node(member)

    def rank(self):
        graph = self.graph.copy()
        self.check_seedness(graph)

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
            # print(f"resolution: {resolution}")
            for cluster in cluster_members:
                members = cluster_members[cluster]
                inside_edges[cluster] = set()
                for m in members:
                    inside_neighbors = set(graph.neighbors(m)) & members
                    for n in inside_neighbors:
                        # ignore duplicate edges
                        if (n, m) in inside_neighbors:
                            continue
                        inside_edges[cluster].add((m, n))
                # num_sybils = len([m for m in members if m.node_type == 'Sybil'])
                # if num_sybils > 0 or True:
                #     print(cluster, len(inside_edges[cluster]) / len(members), len(members), len(inside_edges[cluster]), num_sybils)
            # calculate the weighted average of the number of inside edges per cluster
            num_inside_edges = sum([len(inside_edges[cluster])
                                    for cluster in inside_edges])
            avg = num_inside_edges / graph.order()
            # print(f'avg: {avg}')

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
                    w = graph[node][neighbor].get('weight', 1)
                    # weaken weight if the neighbor has low rank
                    # use max(1, ) because we may reach neighbor before node
                    # and it has current step as rank in this step
                    num += w / max(1, (step - neighbor.rank))
                if num >= border:
                    node.rank = step
        return self.graph
