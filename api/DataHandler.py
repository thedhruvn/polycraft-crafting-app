import pandas as pd
import re
import logging
from util.csv_cleaner import *
from util.exceptions import *
import os
import networkx as nx
import graphviz as gv
import util.constants as CONST
from util.mermaidAdapter import MermaidAdapter


class DataHandler:

    def __init__(self):
        self.log = logging.getLogger("data-handler")
        self.log.setLevel(CONST.LOG_LEVEL)
        self.all_data = None
        self.tree = None
        self.all_items = None
        self._combine_csvs()
        self._append_crafting_conversions()
        # self._create_data_tree()
        self._create_nx_graph()

    def _combine_csvs(self):
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), CONST.RAW_FILE_PATH.replace('./', ''))
        self.log.debug("Combining all input datasets")
        df_list = []
        for filename in os.listdir(dir_path):
            if filename.endswith(CONST.FILTERED_FILENAME_ENDING):
                df_list.append(pd.read_csv(f"{dir_path}/{filename}", index_col=0))

        self.all_data = pd.concat(df_list, axis=0, join='outer', ignore_index=True, keys=None,
                                  levels=None, names=None, verify_integrity=False, copy=True).fillna(0.0)

    @DeprecationWarning
    def _create_data_tree(self):
        self.tree = gv.Digraph()
        for index1, row in self.all_data.iterrows():
            idx = str(index1)
            out_r = re.compile(r"Output*|O\d")
            in_r = re.compile(r"Input*|I\d")
            headers = [i for i in row.index]
            outputs = list(filter(out_r.match, headers))
            inputs = list(filter(in_r.match, headers))
            self.tree.node(str(idx), type='process', weight=str(row['rank_value']))
            for val, ct in list(zip(outputs, outputs[1:]))[::2]:
                if row[ct] > 0:
                    self.tree.edge(row[val].upper(), str(idx), type='item', data=str(row[ct]), parent=str(idx))
            for val, ct in list(zip(inputs, inputs[1:]))[::2]:
                if row[ct] > 0:
                    self.tree.edge(str(idx), row[val].upper(), type='item', data=str(row[ct]), parent=row[val].upper())
        self.log.debug("Graph Successfully Created.")
        self.log.debug("Graph contains: ")
        self.log.debug(print(self.tree))

    def _create_nx_graph(self):
        self.tree = nx.MultiDiGraph()
        out_r = re.compile(r"Output*|O\d")
        in_r = re.compile(r"Input*|I\d")
        headers = [i for i in self.all_data.columns.to_list()]
        outputs = list(filter(out_r.match, headers))
        inputs = list(filter(in_r.match, headers))
        for index1, row in self.all_data.iterrows():
            idx = str(index1)

            self.tree.add_node(str(idx), type='process', subtype=row['process'], weight=row['rank_value'])
            for val, ct in list(zip(outputs, outputs[1:]))[::2]:
                if row[ct] > 0:
                    self.tree.add_node(row[val].upper(), type='item', subtype='item')  # TODO: Add weight = Count?
                    self.tree.add_edge(row[val].upper(), str(idx), count=str(row[ct]))
            for val, ct in list(zip(inputs, inputs[1:]))[::2]:
                if row[ct] > 0:
                    self.tree.add_node(row[val].upper(), type='item', subtype='item')  # TODO: Add weight = Count?
                    self.tree.add_edge(str(idx), row[val].upper(), count=str(row[ct]))
        self.log.debug("Graph Successfully Created.")
        self.log.debug("Graph contains: ")
        self.log.debug(print(self.tree))

    @staticmethod
    def is_node_an_item(node_idx):
        return not all(val.isdigit() for val in str(node_idx))
        # types = nx.get_node_attributes(self.tree, 'type')
        # if node_idx in types.keys():
        #     return False
        # else:
        #     return True

    def _append_crafting_conversions(self):
        self.all_data["id"] = self.all_data.index
        value_r = re.compile(r"Input*|Output*")
        idv = list(filter(value_r.match, self.all_data.columns.to_list()))

        vals = pd.melt(self.all_data, id_vars=['id'], value_vars=idv)['value'].drop_duplicates()
        self.log.debug(f"Sending {len(list(vals))} items for crafting conversion evaluation: ")

        convs = Cleaner.craft_conversions(vals)
        self.log.debug(f"Received {str(convs.shape)} items to add to network")
        self.all_data = pd.concat([self.all_data, convs], axis=0, join='outer', ignore_index=True, keys=None,
                                  levels=None, names=None, verify_integrity=False, copy=True).fillna(
            0.0).drop_duplicates()

        self.all_items = list(pd.melt(self.all_data, id_vars=['id'], value_vars=idv)['value'].drop_duplicates().str.upper())

    def query_item(self, item):
        if item not in self.all_items:
            raise ItemNotFoundException(f"Error: {item} does not exist")
        return nx.algorithms.shortest_paths.weighted.single_source_dijkstra(self.tree,
                                                                            item.upper(),
                                                                            cutoff=150)

    def build_network(self, list_of_nodes):
        if isinstance(list_of_nodes, dict):
            list_of_nodes = next(iter(list_of_nodes.values()))

        G = self.tree.subgraph(list_of_nodes)
        H = nx.MultiDiGraph(G)
        H.remove_nodes_from([g for g in H if g not in list_of_nodes])
        return H

    def print_network(self, list_of_nodes, start=None):
        net = self.build_network(list_of_nodes)
        ma = MermaidAdapter(net)
        return ma.get_mermaid(start)
        # TODO: Print to File
        # For now, use Mermaid formatting and build the graph using mermaid logic. What is mermaid logic?
        # https://mermaid-js.github.io/mermaid-live-editor/
        # NodeID[Node Name] --> |Edge Data| NodeID2[Node Name 2]


if __name__ == '__main__':
    dh = DataHandler()
    # dh.tree.render('testing2.gv')
    # dh.all_data.to_csv("all_data.csv")
