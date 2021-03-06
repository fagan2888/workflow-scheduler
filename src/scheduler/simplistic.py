from .scheduler import Scheduler
import numpy as np

# Simplistic scheduler that maps the best resource to critical path


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class Simplistic(Scheduler):

    def schedule(self):
        routes = self.workflow.routes.copy()

        routes = self.order_routes(routes)

        policy = {x: None if x > 0 else self.resources[0] for x in range(0, self.workflow.size)}

        resources = self.resources.copy()
        resources = self.order_resources(resources)
        resources_size = len(resources)

        routes_len = len(routes)

        divide = round(routes_len / resources_size)

        i = 0
        tasks_per_chunk = {x: [] for x in range(0, self.workflow.size)}
        for chunk in chunks(routes, divide):
            for route in chunk:
                for task in route['path']:
                    tasks_per_chunk[task].append(i)
            if i < len(resources) - 1:
                i += 1

        for task in list(tasks_per_chunk.keys())[1:]:
            policy[task] = self.resources[np.bincount(tasks_per_chunk[task]).argmax()]

        self.policy = policy
