import random
import copy

from utils import *


# Config
random.seed(12)

# Constants
# robot
CAPACITY = 50
RANGE = 150
# map
X, Y = 50, 50
# samples
SAMPLES_N = 20
VALUES_RANGE = (1,10)
CATEGORIES_N = 2
CATEGORIES = [random.randrange(*VALUES_RANGE) for _ in range(CATEGORIES_N)]
MASS_RANGE = (1,10)


N_cycles = 1000  # cycles
MUTATION_CHANCE = 0.25

# Creating a Robot
robot = Robot(CAPACITY, RANGE)
# Generating a map of Mars
mars_map = MarsMap(X,Y)
# Generating the samples and mapping them onto the map
samples = [Sample(i, CATEGORIES, MASS_RANGE) for i in range(SAMPLES_N)]
for sample in samples:
  mars_map.push_sample(sample)
# Calculating distances between all samples and every sample and the base
distances_map = DistancesMap(SAMPLES_N,SAMPLES_N, samples)




def generate_first_generation(solution, decisions):
  generation = []
  length = 50
  while len(generation) < length:
    candidate = get_variables(solution, decisions)
    if constraint_capacity(robot.capacity, candidate[1], samples) and \
      constraint_categories(samples, candidate[1], CATEGORIES) and \
      constraint_range(robot.range, candidate[0], distances_map):
      generation.append(candidate)
  return generation


def sort_fitness(generation):
    generation.sort(key=lambda x: objective(samples,x[1]))
    return generation
    

def mutate(unit):
    
    decisions = [0 for _ in range(len(unit[0])-1)]
    path = [[0 for _ in range(len(unit[0]))] for _ in range(len(unit[0]))]
    values = [i for i in range(1,len(unit[0])-1)]
    new_unit = transform_path(unit[0])

    if random.random()>0.5:
        if len(new_unit) > 2:
            new_unit.pop(random.randint(1,len(new_unit)-2))
            for j in range(len(new_unit)-1):
                path[new_unit[j]][new_unit[j+1]] = 1
            for i in range(1,len(new_unit)-1):
                decisions[new_unit[i]-1] = 1
            return path,decisions
    if len(new_unit) > 2 and len(new_unit) < len(decisions)+2:
        position = random.randint(1,len(new_unit)-2)
        v = random.choice([i for i in values if i not in new_unit])
        new_unit.insert(position,v)
        for j in range(len(new_unit)-1):
            path[new_unit[j]][new_unit[j+1]] = 1
        for i in range(1,len(new_unit)-1):
            decisions[new_unit[i]-1] = 1
        return path,decisions   
    return unit

    


def crossover(p1, p2):
    decisions = [0 for _ in range(len(p1)-1)]
    path = [[0 for _ in range(len(p1))] for _ in range(len(p1))]
    child = [0]
    parent1 = transform_path(p1)
    parent2 = transform_path(p2)
    
    while len(parent1) != len(parent2):
        if len(parent1) < len(parent2):
            parent1.append(0)
        else:
            parent2.append(0)
    for i in range(1,len(parent1)):
        pair = [parent1[i],parent2[i]]
        choice = pair.pop(random.randint(0,1))
        if choice == 0:
            break
        elif decisions[choice-1] == 0 :
            decisions[choice-1] = 1
            child.append(choice)
        elif decisions[pair[0]-1] == 0:
            decisions[pair[0]-1] = 1
            child.append(pair[0]) 
    child.append(0)          
    
    for j in range(len(child)-1):
        path[child[j]][child[j+1]] = 1
        
    return path,decisions


def transform_path(path):
    t_path = [0]
    id = 0
    for _ in range(len(path)):
        id = get_index(path[id])[0]
        t_path.append(id)
        if id == 0:
            break
    return t_path
    

def select_best_units(generation):
    n = len(generation)
    new_generation = []

    while len(new_generation) < int(n/2):
        c_max = 0
        id_max = 0
        for i in range(len(generation)):
            temp = objective(samples, generation[i][1])
            if temp >= c_max:
                c_max = temp
                id_max = i
        new_generation.append(generation.pop(id_max))
    return new_generation



def genetic_algorithm(path, decisions, distance):
    population = generate_first_generation(path, decisions)

    counter = 0
    while counter < N_cycles:
        new_population = select_best_units(copy.deepcopy(population))
        while len(new_population) != len(population):
            child = crossover(random.choice(new_population)[0],random.choice(new_population)[0])
            if random.random() <= MUTATION_CHANCE:
                child = mutate(child)
            if constraint_capacity(robot.capacity, child[1], samples) and\
                constraint_range(robot.range, child[0], distances_map) and \
                constraint_categories(samples, child[1], CATEGORIES) and \
                constraint_comeback(child[0]) and \
                constraint_row_col_sum(child[0]):
                new_population.append(child)
        
        population = new_population
        best = max(population, key=lambda x: objective(samples,x[1]))

        print(objective(samples,best[1]))
        counter += 1
        print(counter)



path, decisions = create_first_list(SAMPLES_N)
distance = objective(samples, decisions)
solution, value = genetic_algorithm(path, decisions, distance)


