from . import sybil_rank
import networkx as nx
import itertools
from anti_sybil.utils import Node


class GroupSybilRank():

    def __init__(self, graph, options=None):
        sybil_rank.SybilRank.__init__(self, graph, options)
        groups = {}
        for node in self.graph.nodes:
            for group in node.groups:
                if group not in groups:
                    groups[group] = []
                groups[group].append(node)

        # remove the groups with the same members
        rgroups = {tuple(v): k for k, v in groups.items()}
        groups = {v: list(k) for k, v in rgroups.items()}
        self.groups = groups
        self.group_graph = self.gen_group_graph()

    def rank(self):
        ranker = sybil_rank.SybilRank(self.group_graph, self.options)
        ranker.rank()
        groups_ranks = {g.name: g.rank for g in self.group_graph.nodes}

        for node in self.graph.nodes:
            if not node.groups:
                node.rank = 0
                node.node_type = 'New'
            else:
                max_group = max(
                    node.groups, key=lambda g: groups_ranks.get(g, 0))
                node.rank = groups_ranks.get(max_group, 0)
        return self.group_graph

    @staticmethod
    def get_group_type(group_nodes):
        flag = set([node.node_type for node in group_nodes])
        if flag == set(['Seed']):
            group_type = 'Seed'
        elif flag == set(['Sybil', 'Attacker']) or flag == set(['Sybil']):
            group_type = 'Sybil'
        else:
            group_type = 'Honest'
        return group_type

    def gen_group_graph(self):
        group_graph = nx.Graph()
        seed_groups = set()
        groups_dic = {}
        for group in self.groups:
            group_type = self.get_group_type(self.groups[group])
            if group_type == 'Seed':
                seed_groups.add(group)
            groups_dic[group] = Node(group, group_type)
        for group in seed_groups:
            groups_dic[group].init_rank = 1 / len(seed_groups)
        valid_pairs = {}
        for n1 in self.graph.nodes:
            neighbors = self.graph.neighbors(n1)
            for n2 in neighbors:
                for g1 in n1.groups:
                    for g2 in n2.groups:
                        valid_pairs[(g1, g2)] = True
        pairs = itertools.combinations(self.groups.keys(), 2)
        pairs = sorted([(f, t) if f < t else (t, f)
                        for f, t in pairs], key=lambda pair: str(pair))
        for source_group, target_group in pairs:
            if (source_group, target_group) not in valid_pairs:
                continue
            removed = set()
            weight = 0
            source_nodes = self.groups[source_group]
            target_nodes = self.groups[target_group]
            for source_node in source_nodes:
                if source_node in removed:
                    continue
                for target_node in target_nodes:
                    if source_node in removed:
                        break
                    if target_node in removed:
                        continue
                    if not self.graph.has_edge(source_node, target_node):
                        continue

                    # set number of common neighbors as the weight of the edge (trustworthy of connection)
                    n1 = self.graph.neighbors(source_node)
                    n2 = self.graph.neighbors(target_node)
                    edge_weight = len(set(list(n1)) & set(list(n2)))
                    if not edge_weight:
                        continue

                    weight += edge_weight
                    removed.add(source_node)
                    removed.add(target_node)

            if weight > 0:
                num = len(source_nodes) + len(target_nodes)
                group_graph.add_edge(
                    groups_dic[source_group], groups_dic[target_group], weight=weight / num)
        return group_graph
