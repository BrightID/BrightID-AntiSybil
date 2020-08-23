from . import sybil_rank
import networkx as nx


class WeightedSybilRank(sybil_rank.SybilRank):

    def __init__(self, graph, options=None):
        sybil_rank.SybilRank.__init__(self, graph, options)
        self.weighted_graph = self.gen_weighted_graph()

    def rank(self):
        ranker = sybil_rank.SybilRank(self.weighted_graph, self.options)
        ranker.rank()

        for node in self.graph:
            node2 = next(filter(lambda n: n.name == node.name,
                                self.weighted_graph), None)
            node.rank = node2.rank if node2 else 0
        return self.graph

    def gen_weighted_graph(self):
        weighted_graph = nx.Graph()
        for node in self.graph:
            neighbors1 = list(self.graph.neighbors(node))
            used_neighbors = set()
            for i, neighbor in enumerate(neighbors1):
                if weighted_graph.has_edge(node, neighbor):
                    continue
                # the common neighbors empower the connection
                neighbors2 = list(self.graph.neighbors(neighbor))
                common_neighbors = set(neighbors1) & set(neighbors2)
                common_neighbors = list(common_neighbors - used_neighbors)
                common_neighbors.sort(key=lambda n: self.graph.degree(n))
                if common_neighbors:
                    used_neighbors.add(common_neighbors[0])
                weight = len(common_neighbors)

                # the common group empower the connection
                # common_groups = len((set(node.groups.keys()) & set(neighbor.groups.keys())))
                # if weight and common_groups:
                #     weight += 1

                # the common group empower the connection
                # if weight and (node.node_type == 'Seed' or neighbor.node_type == 'Seed'):
                #     weight += 1

                weighted_graph.add_edge(node, neighbor, weight=weight)
        return weighted_graph
