from numpy import random
from deap import base, creator
from deap import tools
from deap import algorithms

from .scheduler import Scheduler
from simulation.executor import Executor
from simulation.resource import Resource
from simulation.config import RESOURCES
from .extreme import MaxResource, MinResource


NUM_GEN = 1500


class GeneticScheduler(Scheduler):
    def schedule(self):
        random.seed(64)
        maxScheduler = MaxResource(0,0, self.workflow)
        maxScheduler.schedule()
        min_time, max_cost = maxScheduler.run()
        minScheduler = MinResource(0,0, self.workflow)
        minScheduler.schedule()
        max_time, min_cost = minScheduler.run()
        toolbox = base.Toolbox()
        IND_SIZE = self.workflow.size

        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        toolbox.register("attribute", random.randint, 0, len(self.resources))
        toolbox.register("individual", tools.initRepeat, creator.Individual,
                         toolbox.attribute, n=IND_SIZE)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
        toolbox.register("select", tools.selTournament, tournsize=3)

        workflow = self.workflow

        def feasible(individual):
            available_resources = [Resource(**resource) for resource in RESOURCES]
            for x in individual:
                if x > len(available_resources) or x < 0:
                    return False
            return True

        def evaluate(ind):
            available_resources = [Resource(**resource) for resource in RESOURCES]
            executor = Executor()

            policy = {i: available_resources[int(ind[i])] for i in range(0, len(ind))}

            total_time, total_cost = executor.run(workflow, available_resources, policy)

            return (total_cost - min_cost) / (max_cost - min_cost) + (total_time - min_time) / (max_time - min_time),

        toolbox.register("evaluate", evaluate)
        toolbox.decorate("evaluate", tools.DeltaPenalty(feasible, 10000))

        pop = toolbox.population(n=50)
        pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=NUM_GEN, verbose=False)

        pop.sort(key=lambda x: x.fitness.values)
        self.policy = {i: self.resources[int(pop[0][i])] for i in range(0, workflow.size)}
