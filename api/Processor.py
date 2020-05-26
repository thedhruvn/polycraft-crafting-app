import logging
import pandas as pd
import re
import sys
from util.exceptions import *
import DataHandler
import util.constants as CONST
import networkx as nx
from collections import defaultdict
import pprint
import matplotlib


class Processor:

    def __init__(self):
        self.dh = DataHandler.DataHandler()
        self.log = logging.getLogger()
        self.log.setLevel(CONST.LOG_LEVEL)
        self.base_item_list = self._get_base_item_list()
        self._temp_graph = nx.MultiDiGraph()
        self._search_terms = []

    def _query_handler(self, query, filtered = False):
        self._search_terms.append(query)
        raw_answer_dist, raw_answer_path = self.dh.query_item(query)
        self.log.info(f"Query Complete: {query} has {len(raw_answer_dist.keys())} possible solutions.")
        self.log.info(f"Commencing cleaning of raw results...")
        clean_answer = self._check_answer(raw_answer_dist, raw_answer_path, filtered)
        self.log.debug(f"Answer cleaned: {[pprint.pprint(i) for i in clean_answer]}")
        return clean_answer

    def query_solution(self, item):
        item = item.upper()
        query_result = self._query_handler(item)
        result = self._expand_answer(query_result)
        self._search_terms = []
        return result
        # return clean_answer

    def build_network(self, list_of_nodes):
        if isinstance(list_of_nodes, dict):
            list_of_nodes = next(iter(list_of_nodes.values()))

        G = self.dh.tree.subgraph(list_of_nodes)
        H = nx.MultiDiGraph(G)
        H.remove_nodes_from([g for g in H if g not in list_of_nodes])
        return H

    def query_network(self, item):
        """
        Returns a NetworkX graph representing the crafting solution for the item queried
        :param item: String representing the item name. Case in-sensitive
        :return: {@link:NetworkX.Graph} of the network required to build the network
        """
        item = item.upper()
        return self.build_network(self.query_solution(item))

    def query_mermaid(self, item):
        """
        Returns a Mermaid Markdown String representing the crafting solution for the item queried
        :param item: String representing the item name. Case in-sensitive
        :return: {Str} representing the network in Mermaid markdown format
        """
        item = item.upper()
        return self.dh.print_network(self.query_solution(item), item)
        #net = self.build_network(self.query_solution(item))


    def _get_base_item_list(self):
        raw = pd.read_csv(f"{CONST.RAW_FILE_PATH}{CONST.BASE_ITEM_LIST_CSV}")
        series = raw.iloc[:, 0]
        # base_item_list = list(series.str.upper())
        items = list(series.str.upper())
        self.log.debug(f"{len(items)} number of items read from CSV")
        items.extend(self._generate_additional_base_items(items))
        return items

    def _generate_additional_base_items(self, items):
        all_nodes = list(self.dh.tree.nodes)
        additional_base_items =[]
        for node in all_nodes:
            if self.dh.is_node_an_item(node):
                if node not in items:
                    if any(sub in str(node) for sub in CONST.ADDITIONAL_BASE_ITEM_SEARCH):
                        additional_base_items.append(str(node))
        return additional_base_items

    def _get_filtered_path(self, raw_dist, raw_path):
        filtered_dist = {k: v for k, v in raw_dist.items() if k in self.base_item_list}
        # TODO: Do I want to expand this criteria to include paths not just with the least number of steps?
        min_filtered_dict = {k: v for k, v in filtered_dist.items() if
                             v <= min(filtered_dist.values())*CONST.FILTER_SCALE}

        min_filtered_path = {k: v for k, v in raw_path.items() if k in min_filtered_dict.keys()}

        wt_dict = defaultdict(lambda: 0.)
        wt = defaultdict(lambda: None)
        wt.update(nx.get_node_attributes(self.dh.tree, 'weight'))
        for key, items in min_filtered_path.items():
            for item in items:
                weight = wt[item] # Use the weight attribute. TODO: include ct?
                if weight is not None:
                    wt_dict[key] += float(weight)
        return {k: v for k, v in min_filtered_path.items() if k == min(wt_dict, key=wt_dict.get)}

    def _check_answer(self, raw_dist, raw_path, filtered=False):
        # self._temp_graph.clear()
        sets_of_answers = {}
        result_set = {}

        filtered_path = self._get_filtered_path(raw_dist, raw_path)

        self.log.debug(f"{pprint.pprint(filtered_path)}")
        for key, steps in filtered_path.items():
            list_of_steps = []
            for step in steps:
                number = re.search(r'\d+', step)
                if number is not None:
                    number = number.group() #leave as a str for now...
                    list_of_steps.append(number)

            sets_of_answers[key] = list_of_steps

        #result_set = {key: self.dh.tree.subgraph(answers).add_nodes_from([G for G in self.dh.tree.neighbors(answers)]) for key, answers in sets_of_answers.items()}
        for key, answers in sets_of_answers.items():
            node_list = []
            for i in answers:
                node_list.append(i)
                node_list.extend(self.dh.tree.successors(i))
                node_list.extend(self.dh.tree.predecessors(i))

            result_set[key] = node_list
            # result_set[key] = self.dh.tree.subgraph(node_list)

        return result_set

    def _expand_answer(self, answer):
        re_run_list = defaultdict(lambda: [])
        for key, values in answer.items():
            for val in values:
                if val not in self.base_item_list and val not in self._search_terms and self.dh.is_node_an_item(val) and val not in re_run_list[key]:
                    re_run_list[key].append(val)

        if len(re_run_list.items()) == 0:
            return answer
        else:
            more_answers = defaultdict(lambda: [])
            for key, items in re_run_list.items():
                for item in items:
                    more_answers.update(self._query_handler(item, filtered=True)) # This also updates the 'Search term'
                    # TODO: Am I going to pick every combination?
                    if len(more_answers) > 0:
                        for key2, item2 in more_answers.items():
                            for val in more_answers[key2]:
                                if val not in answer[key]: #force this to be a set?
                                    answer[key].append(val)
                        # answer[key].extend(list(more_answers.values())[0])
            return self._expand_answer(answer)

if __name__ == '__main__':
    ps = Processor()
    sys.setrecursionlimit(10 ** 6)
    #rs = ps.query_solution('DRUM (KEROSENE)')
    #pprint.pprint(rs)
    mermaid = ps.query_mermaid('industrial oven')
    print(mermaid)

    # pprint.pprint(ps.query_solution('DRUM (KEROSENE)'))