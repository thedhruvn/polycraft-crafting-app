import logging
import re
import os
from util.exceptions import *
from collections import OrderedDict

class MermaidAdapter:

    def __init__(self, graph):
        self.graph = graph
        self.log = logging.getLogger()
        self.process_order = OrderedDict()
        self.mermaid = ''
        self.node_prefix = '['
        self.node_suffix = ']'
        self.process_prefix = '{'
        self.process_suffix = '}'
        self.edge_delim = '|'
        self.arrow_type = '-->'

    def get_mermaid(self, start=None):
        self.mermaid = ''  # reset
        if start is None:
            list_of_roots = [n for n, d in self.graph.in_degree if d == 0]
            start = list_of_roots[0]
        if self.graph.nodes[start]['type'] != 'item':
            raise BadSubgraphForMermaidException(f"Graph starts with: {start} which isn't an item")

        self._get_next_process_step(start, 1)
        return self.mermaid

    def convert_process_to_mermaid(self, process):
        for item in self.graph.predecessors(process):
            self.mermaid += self._format_mermaid_process_string(item, process, dir='I->P')
        for item in self.graph.successors(process):
            self.mermaid += self._format_mermaid_process_string(item, process, dir='P->I')

    def _get_next_process_step(self, prev_step, flag):
        if flag == 1:  # Prev_Step = Item, current step = process
            next_steps = [n for n in self.graph.successors(prev_step) if self.graph.nodes[n]['type'] == 'process']
            if len(next_steps) == 0:
                return
            if any(item in self.process_order for item in next_steps):
                # Item already processed...
                return
            for step in next_steps:
                self.process_order[step] = self.graph.nodes[step]['subtype']
                self.convert_process_to_mermaid(step)
                self._get_next_process_step(step, 0)
        else:  #Prev_Step == Process
            next_items = [n for n in self.graph.successors(prev_step) if self.graph.nodes[n]['type'] == 'item']
            for item in next_items:  # Skip the process and go through each item to get the process.
                # next_steps = [n for n in self.graph.successors(item) if self.graph.nodes[n]['type'] == 'process']
                if len(next_items) == 0:
                    print("ERROR! This should never trigger.")
                    continue  #This should NEVER trigger...
                #if all(item in self.process_order for item in next_steps):
                #    continue # (step already processed)
                #for step in next_steps:
                    #self.process_order[step] = self.graph.nodes[step]['subtype']
                    #self.convert_process_to_mermaid(step)
                self._get_next_process_step(item, 1)

    def _get_process_string(self, process):
        return f"{str(process)}{self.process_prefix}{self.graph.nodes[process]['subtype']}:{str(process)}{self.process_suffix}"

    def _get_item_string(self, item):
        r = re.compile(r"[\s\(]+")
        it_id = re.sub(r"[\s\(\)]+", '', str(item))
        it_nm = re.sub(r"[\(\)]+", '', str(item))
        return f"{it_id}{self.node_prefix}{it_nm}{self.node_suffix}"

    def _get_edge_string(self, A, B):
        return f"{self.edge_delim}{self.graph.edges[(A, B, 0)]['count']}{self.edge_delim}"

    def _format_mermaid_process_string(self, item, process, dir='IP', **kwargs):

        ## Update shapes as needed TODO: Move to its own function?
        self.node_prefix = kwargs.pop('node_prefix', self.node_prefix)
        self.node_suffix = kwargs.pop('node_suffix', self.node_suffix)
        self.process_prefix = kwargs.pop('process_prefix', self.process_prefix)
        self.process_suffix = kwargs.pop('process_suffix', self.process_suffix)
        self.edge_delim = kwargs.pop('edge_delim', self.edge_delim)
        # edge_suffix = kwargs.pop('edge_suffix', '|')
        self.arrow_type = kwargs.pop('arrow_type', self.arrow_type)

        if self.graph.nodes[item]['type'] != 'item':
            raise BadSubgraphForMermaidException(f"Process {str(process)} has neighbor: {str(item)} that isn't an item")

        if dir == 'I->P':
            return f"{self._get_item_string(item)} {self.arrow_type} " \
                   f"{self._get_edge_string(item, process)} " \
                   f"{self._get_process_string(process)}\n"
        else:
            return f"{self._get_process_string(process)} {self.arrow_type} " \
                   f"{self._get_edge_string(process, item)} " \
                   f"{self._get_item_string(item)}\n"
