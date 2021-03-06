from graph_tool.all import Graph, graph_draw


class Workflow:
    def __init__(self, edges, weights):
        self.edges = edges
        self.graph = Graph()
        self.size = len(edges['target'])
        self.graph.add_vertex(self.size)
        self.weights = weights

        # init weights part
        self.graph.vp.weights = self.graph.new_vertex_property('int16_t')
        for index in range(0, self.size):
            self.graph.vp.weights[index] = weights[index]

        for source in self.edges['source'].keys():
            for target in self.edges['source'][source]:
                self._add_edge(source, target)

        self.depth_per_node = {x: 0 for x in range(0, self.size)}
        self.accum_weights = {x: 0 for x in range(0, self.size)}
        self.find_depth()
        self.find_accum_weights(self.size - 1)
        self.depth = {x: [] for x in set(self.depth_per_node.values())}

        for node, depth in self.depth_per_node.items():
            self.depth[depth].append(node)

        self.routes_t = {}
        self.find_routes(self.size - 1, 0, self.routes_t)

        self.routes = []
        self.transpose_routes(self.size - 1, self.routes_t[self.size - 1])

    def _add_edge(self, source, target):
        self.graph.add_edge(self.graph.vertex(source), self.graph.vertex(target))

    def show(self, size=1500):
        return graph_draw(self.graph, vertex_text=self.graph.vertex_index, vertex_font_size=18,
                          output_size=(size, size), output="graph.png")

    def find_accum_weights(self, actual_node, accum_weight=0):
        already_accum_weight = self.accum_weights[actual_node]
        self.accum_weights[actual_node] = max(already_accum_weight, accum_weight + self.weights[actual_node])

        for fathers in self.edges['target'][actual_node]:
            self.find_accum_weights(fathers, self.accum_weights[actual_node])

    def find_depth(self, actual_node=0, actual_depth=0):
        self.depth_per_node[actual_node] = max(self.depth_per_node[actual_node], actual_depth)
        for next_node in self.edges['source'][actual_node]:
            self.find_depth(next_node, actual_depth + 1)

    def find_routes(self, actual_node, weight=0, routes={}):
        weight += self.weights[actual_node]
        if actual_node != 0:
            routes[actual_node] = {}
            for fathers in self.edges['target'][actual_node]:
                self.find_routes(fathers, weight, routes[actual_node])
        else:
            routes[actual_node] = weight

    def transpose_routes(self, actual_node, routes, path=[]):
        if actual_node != 0:
            path = path.copy()
            path.append(actual_node)
            for child in routes.keys():
                self.transpose_routes(child, routes[child], path)
        else:

            self.routes.append({
                'path': path,
                'weight': routes
            })

    def find_cycles(self):
        visited = [ False for _ in range(0, self.size) ]

        return self.find_cycles_helper( 0, [])

    def find_cycles_helper(self, actual_node, rec_list):
        if actual_node in rec_list:
            print(rec_list, actual_node)
            return True

        call_this = []
        for child in self.edges['source'][actual_node]:
            new_rec_list = rec_list.copy()
            new_rec_list.append(actual_node)
            call_this.append([child, new_rec_list])


        return any([self.find_cycles_helper(x[0], x[1]) for x in call_this])
