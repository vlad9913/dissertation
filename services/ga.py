from models.chromosome import Chromosome


class GeneticAlgorithm():
    def __init__(self, solutionSize, nrGens, popLength, entities, function_map, attribute_diff):
        self.__solutionSize = solutionSize
        self.__nrGens = nrGens
        self.__popLength = popLength
        self.__entities = entities
        self.__function_map = function_map
        self.__attribute_diff = attribute_diff

    def fitness_evaluation(self, chromosome):
        sum_scores = {attr: 0 for attr in self.__function_map.keys()}

        for attr, function in self.__function_map.items():
            chr_diff = chromosome.get_attribute_max(attr)[0] - chromosome.get_attribute_min(attr)[0]
            rate = chr_diff / self.__attribute_diff[attr]

            chromo = chromosome.get_repres()

            for i in range(len(chromo[:-1])):
                relative_position = i * (1 / self.__solutionSize)
                relative_position_next = (i + 1) * (1 / self.__solutionSize)

                best_attr = rate * (float(function(relative_position_next)) - float(
                    function(relative_position)))
                actual_attr = float(chromo[i + 1][attr]) - float(chromo[i][attr])
                attr_score = self.evaluate_rate(actual_attr, best_attr) / self.__solutionSize
                sum_scores[attr] += attr_score

        return sum(sum_scores.values()) / len(sum_scores)

    def evaluate_rate(self, actual, best):
        import numpy as np
        if np.sign(actual) != np.sign(best):
            evaluation = -0.5
            return evaluation
        evaluation = self.quadratic_formula(best, best - actual)
        return evaluation

    def quadratic_formula(self, denominator, x):
        value = -(x / (denominator + 0.000000001)) ** 2 + 1
        if value >= 0:
            return value
        return 0

    def evolution(self):
        import random
        import numpy as np
        population = []
        maxFitness = 0

        while len(population) < self.__popLength:
            c = Chromosome(self.__solutionSize, self.__entities, 1, list(self.__function_map.keys()))
            c.fitness = self.fitness_evaluation(c)
            if c.fitness > 0:
                population.append(c)

                if c.fitness > maxFitness:
                    maxFitness = c.fitness
                    bestChromosome = c

        for i in range(self.__nrGens):

            newPopulation = []
            newPopulation.append(bestChromosome)

            sorted_population = sorted(population, key=lambda x: x.get_fitness())
            rank_sum = self.__popLength * (self.__popLength + 1) / 2.0

            selection_probs = [rank/rank_sum for rank in range(1, self.__popLength+1)]

            for j in range(self.__popLength - 1):

                mother = sorted_population[np.random.choice(len(population), p=selection_probs)]
                father = sorted_population[np.random.choice(len(population), p=selection_probs)]

                c1 = mother.crossover(father)

                c1.mutation()
                c1.set_fitness(self.fitness_evaluation(c1))

                c2 = father.crossover(mother)

                c2.mutation()
                c2.set_fitness(self.fitness_evaluation(c2))

                if c1.get_fitness() > c2.get_fitness():
                    child = c1
                else:
                    child = c2

                newPopulation.append(child)

                if maxFitness < child.get_fitness():
                    maxFitness = child.get_fitness()
                    bestChromosome = child

            print("Generation " + str(i + 1) + "'s best fit: " + str(bestChromosome.get_fitness()))
            population = newPopulation

        return bestChromosome
