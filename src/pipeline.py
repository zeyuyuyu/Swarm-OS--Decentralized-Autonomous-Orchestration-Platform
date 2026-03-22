import multiprocessing as mp
import networkx as nx
import time

class DistributedPipeline:
    def __init__(self, graph):
        self.graph = graph
        self.node_procs = {}

    def run(self):
        for node in self.graph.nodes:
            proc = mp.Process(target=self.execute_node, args=(node,))
            proc.start()
            self.node_procs[node] = proc

        for node, proc in self.node_procs.items():
            proc.join()

    def execute_node(self, node):
        print(f'Executing node: {node}')
        # Execute node logic here
        time.sleep(2)
        print(f'Node {node} complete')

        # Check dependencies
        deps = list(self.graph.predecessors(node))
        if not deps:
            return

        # Wait for dependencies to complete
        for dep in deps:
            self.node_procs[dep].join()

        # Execute downstream nodes
        for child in self.graph.successors(node):
            self.execute_node(child)

if __name__ == '__main__':
    graph = nx.DiGraph()
    graph.add_edges_from([('A', 'B'), ('B', 'C'), ('B', 'D'), ('C', 'E'), ('D', 'E')])

    pipeline = DistributedPipeline(graph)
    pipeline.run()
