def generate_a_random_chromosome(n, entities, attributes):
    import random
    repres = []
    max_attr_values = {attr: [0, 0] for attr in attributes}
    min_attr_values = {attr: [1, 0] for attr in attributes}

    for i in range(n):
        choice = random.choice(entities)
        repres.append(choice)

        for attr in attributes:
            if float(choice[attr]) < min_attr_values[attr][0]:
                min_attr_values[attr] = [float(choice[attr]), i]
            if float(choice[attr]) > max_attr_values[attr][0]:
                max_attr_values[attr] = [float(choice[attr]), i]

    return repres, min_attr_values, max_attr_values


class Chromosome:
    def __init__(self, n, entities, option, attributes):
        self.__repres = []
        self.__fitness = 0.0
        self.__length = n
        self.__entities = entities
        self.attributes = attributes
        for attr in self.attributes:
            setattr(self, 'max_' + attr, [0, 0])
            setattr(self, 'min_' + attr, [1, 0])

        if option == 1:
            self.__repres, min_attr_values, max_attr_values = generate_a_random_chromosome(
                n, entities, self.attributes)
            for attr in self.attributes:
                setattr(self, 'min_' + attr, min_attr_values[attr])
                setattr(self, 'max_' + attr, max_attr_values[attr])

    def get_repres(self):
        return self.__repres

    def set_repres(self, new_repres):
        self.__repres = new_repres

    def get_fitness(self):
        return self.__fitness

    def set_fitness(self, new_fitness):
        self.__fitness = new_fitness

    def get_length(self):
        return self.__length

    def set_length(self, new_length):
        self.__length = new_length

    def get_attribute_max(self, attr):
        return getattr(self, 'max_' + attr)

    def set_attribute_max(self, attr, value):
        setattr(self, 'max_' + attr, value)

    def get_attribute_min(self, attr):
        return getattr(self, 'min_' + attr)

    def set_attribute_min(self, attr, value):
        setattr(self, 'min_' + attr, value)

    def crossover(self, c):
        import random
        pos1 = random.randint(1, self.__length - 2)
        pos2 = random.randint(1, self.__length - 2)
        if pos2 < pos1:
            pos1, pos2 = pos2, pos1

        max_attr_values = {attr: [0, 0] for attr in self.attributes}
        min_attr_values = {attr: [1, 0] for attr in self.attributes}

        for attr in self.attributes:
            if self.get_attribute_max(attr)[1] < pos1 or self.get_attribute_max(attr)[1] > pos2:
                max_attr_values[attr] = self.get_attribute_max(attr)
            if self.get_attribute_min(attr)[1] < pos1 or self.get_attribute_min(attr)[1] > pos2:
                min_attr_values[attr] = self.get_attribute_min(attr)
            if pos1 <= c.get_attribute_max(attr)[1] <= pos2:
                max_attr_values[attr] = c.get_attribute_max(attr)
            if pos1 <= c.get_attribute_min(attr)[1] <= pos2:
                min_attr_values[attr] = c.get_attribute_min(attr)

        new_representation = self.get_repres()[:pos1]
        for atom in c.get_repres()[pos1:pos2]:
            if atom not in new_representation:
                new_representation.append(atom)
            else:
                new_representation.append(random.choice(self.__entities))

        for atom in self.get_repres()[pos2:]:
            if atom not in new_representation:
                new_representation.append(atom)
            else:
                new_representation.append(random.choice(self.__entities))

        offspring = Chromosome(self.__length, self.__entities, 0, self.attributes)
        offspring.set_repres(new_representation)
        for attr in self.attributes:
            offspring.set_attribute_max(attr, max_attr_values[attr])
            offspring.set_attribute_min(attr, min_attr_values[attr])
        return offspring

    def mutation(self):
        import random
        pos1 = random.randint(1, self.__length - 2)
        pos2 = random.randint(1, self.__length - 2)
        if pos2 < pos1:
            pos1, pos2 = pos2, pos1

        entity1 = self.__repres[pos1]
        entity2 = self.__repres[pos2]
        self.__repres[pos1], self.__repres[pos2] = entity2, entity1

        for attr in self.attributes:
            max_attr_val, max_attr_pos = self.get_attribute_max(attr)
            min_attr_val, min_attr_pos = self.get_attribute_min(attr)

            if entity1[attr] == max_attr_val or entity2[attr] == max_attr_val:
                max_pos = max(range(self.__length), key=lambda index: self.__repres[index][attr])
                self.set_attribute_max(attr, [self.__repres[max_pos][attr], max_pos])

            if entity1[attr] == min_attr_val or entity2[attr] == min_attr_val:
                min_pos = min(range(self.__length), key=lambda index: self.__repres[index][attr])
                self.set_attribute_min(attr, [self.__repres[min_pos][attr], min_pos])

        # replacement mutation
        mutation_chance = 0.05
        if random.random() < mutation_chance:
            pos = random.randint(0, self.__length - 1)
            new_entity = random.choice(self.__entities)
            while new_entity in self.__repres:
                new_entity = random.choice(self.__entities)
            self.__repres[pos] = new_entity

            for attr in self.attributes:
                if new_entity[attr] > self.get_attribute_max(attr)[0]:
                    self.set_attribute_max(attr, [new_entity[attr], pos])
                if new_entity[attr] < self.get_attribute_min(attr)[0]:
                    self.set_attribute_min(attr, [new_entity[attr], pos])


