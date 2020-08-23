from . import sybil_rank


class LandingProbability(sybil_rank.SybilRank):

    def __init__(self, graph, options=None):
        self.graph = graph
        self.options = options if options else {}

    def rank(self):
        graph = super().rank()
        for node in graph:
            node.rank = node.rank * graph.degree(node)
