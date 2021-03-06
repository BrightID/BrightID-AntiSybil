import math


class SybilRank():

    def __init__(self, graph, options=None):
        self.graph = graph
        self.options = options if options else {}

    def rank(self):
        m = 2 if self.options.get('directed', False) else 1
        num_iterations = max(
            3, int(math.ceil(math.log10(self.graph.order())) / m))
        nodes_rank = {node: node.init_rank for node in self.graph}
        for i in range(num_iterations):
            nodes_rank = self.spread_nodes_rank(nodes_rank)
        for node in self.graph:
            node.rank = nodes_rank[node]
            node_degree = self.graph.degree(node, weight='weight')
            if node_degree > 0:
                node.rank /= node_degree
        return self.graph

    def spread_nodes_rank(self, nodes_rank):
        new_nodes_rank = {}
        for node in nodes_rank:
            new_trust = 0
            if self.options.get('directed', False):
                neighbors = self.graph.predecessors(node)
            else:
                neighbors = self.graph.neighbors(node)
            for neighbor in neighbors:
                neighbor_degree = self.graph.degree(neighbor, weight='weight')
                edge_weight = self.graph[neighbor][node].get('weight', 1)
                if neighbor_degree > 0:
                    new_trust += nodes_rank[neighbor] * \
                        edge_weight / neighbor_degree
            new_nodes_rank[node] = new_trust
        return new_nodes_rank
