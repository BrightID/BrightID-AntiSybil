from . import sybil_rank
import networkx as nx


class WeightedSybilRank(sybil_rank.SybilRank):

    def __init__(self, graph, options=None):
        sybil_rank.SybilRank.__init__(self, graph, options)
        self.weighted_graph = self.gen_weighted_graph()

    def rank(self):
        ranker = sybil_rank.SybilRank(self.weighted_graph, self.options)
        ranker.rank()

        for node in self.graph.nodes:
            node2 = next(filter(lambda n: n.name == node.name,
                                self.weighted_graph.nodes), None)
            node.rank = node2.rank if node2 else 0
            node.raw_rank = node2.raw_rank if node2 else 0
        return self.graph

    def gen_weighted_graph(self):
        weighted_graph = nx.Graph()
        for edge in self.graph.edges:
            neighbors1 = self.graph.neighbors(edge[0])
            neighbors2 = self.graph.neighbors(edge[1])
            weight = len(set(list(neighbors1)) & set(list(neighbors2)))
            weighted_graph.add_edge(edge[0], edge[1], weight=weight)
        return weighted_graph
