import copy
import random


def euclidean_distance(p1, p2):
  return round( ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) ** (1/2), 3 )


def pretty_matrix(array):
  max_len = max([len(str(p)) for l in array for p in l])
  output = ''
  for i, level in enumerate(array):
    for point in level:
      output += str(point) + ' '*(max_len-len(str(point))) + ' '
    if i != len(array)-1:
      output += '\n'
  return output


def mass_vector(decision, samples):
  vector = []
  for j in decision:
    summary = []
    for i in range(len(samples)):
      summary.append(j[1][i] * samples[i].mass)
    vector.append(sum(summary))
  return vector


def distance_vector(path, distance_map):
  vector = []
  for p in path:
    summary =[]
    for i in range(len(distance_map.distances)):
      for j in range(len(distance_map.distances)):
        summary.append(p[0][i][j]*distance_map.distances[i][j])
    vector.append(sum(summary))
  return vector


def get_column(path, n):
  return [path[i][n] for i in range(len(path))]
    

def get_index(vector):
  return [i for i, el in enumerate(vector) if el]


def create_first_list(x):
  decisions = [0 for _ in range(x)]
  path = [[0 for _ in range(x+1)] for _ in range(x+1)]
  for i in range(x//10 + 1):
    path[i][i+1] = 1
    decisions[i] = 1
  path[(x//10)+1][0] = 1
  return path, decisions


def get_variables(path, decisions):    
  new_decisions = copy.deepcopy(decisions)
  new_path = copy.deepcopy(path)
  rand_id = random.randint(0,len(decisions)-1)
  
  if decisions[rand_id] == 0: 
    new_decisions[rand_id] = 1
    change = True
    id_replacement = random.choice(get_index(decisions))+1
  else: 
    new_decisions[rand_id] = 0
    change = False
    id_replacement = random.choice(get_index(new_decisions))+1
  if change:
    new_path[id_replacement][rand_id+1] = 1
    new_path[id_replacement][get_index(path[id_replacement])[0]] = 0
    new_path[rand_id+1][get_index(path[id_replacement])[0]] = 1
  else:
    new_path[rand_id+1][get_index(path[rand_id+1])[0]] = 0
    new_path[get_index(get_column(path, rand_id+1))[0]][id_replacement] = 1
    new_path[get_index(get_column(path, rand_id+1))[0]][rand_id+1] = 0

  if constraint_comeback(new_path) and constraint_row_col_sum(new_path):
    return new_path, new_decisions
  else:
    return get_variables(path, decisions)


class Robot:
  def __init__(self, capacity, range):
    self.capacity = capacity
    self.range = range


class Sample:
  def __init__(self, id, categories, mass_range):
    self.id = id
    self.category = random.randrange(0, len(categories))
    self.value = categories[self.category]
    self.mass = random.randrange(*mass_range)
    self.position = (None,None)
    self.base_distance = (None,None)

  def __str__(self):
    return str(self.id)


class MarsMap:
  def __init__(self, x, y):
    self.x, self.y = x, y
    self.spaces = [[None for _ in range(self.y)] for _ in range(self.x)]
    self.spaces[self.x//2][self.y//2] = -1  # set base

  def __str__(self):
    return pretty_matrix(self.spaces)

  def get_base(self):
    return self.x//2,self.y//2

  def push_sample(self, sample):
    while True:
      pos = (random.randrange(0, self.x), random.randrange(0, self.y))
      if self.spaces[pos[0]][pos[1]] == None:
        self.spaces[pos[0]][pos[1]] = sample
        sample.position = pos
        sample.base_distance = (round(
          euclidean_distance((self.x//2,self.y//2), pos) \
            * random.uniform(1.0, 1.1), 2),
        round(euclidean_distance((self.x//2,self.y//2), pos) \
          * random.uniform(1.0, 1.1), 2))
        break


class DistancesMap:
  def __init__(self, x, y, samples):
    self.x, self.y = x, y
    self.distances = [[None for _ in range(self.y)] for _ in range(self.x)]
    for i, s1 in enumerate(samples):
      for j, s2 in enumerate(samples):
        self.distances[i][j] = round(
          euclidean_distance(s1.position, s2.position) \
            * random.uniform(1.0, 1.1), 2)
    for i, d in enumerate(self.distances):
      d.insert(0, samples[i].base_distance[0])
    self.distances.insert(0,[0])
    for s in samples:
      self.distances[0].append(s.base_distance[1])
    
  def __str__(self):
    return pretty_matrix(self.distances)


def constraint_capacity(capacity, decision, samples):
  # Robot "knapsack" capacity
  _sum = 0
  for i in range(len(samples)):
    _sum += decision[i] * samples[i].mass
  return _sum <= capacity


def constraint_range(robot_range, path, distance_map):
  # Robot max distance traveled
  sum = 0
  for i in range(len(path)):
    for j in range(len(path)):
      sum += path[i][j]*distance_map.distances[i][j]
  return sum <= robot_range


def constraint_categories(samples, decisions, categories):
  # Collect minimum one sample of each category
  _sum = 0
  for j in range(len(categories)):
    counter = 0
    for i in range(len(decisions)):
      if samples[i].category == j:
        counter += 1
    if counter == 0:
      return False
    _sum += 1
  return _sum == len(categories)


def constraint_comeback(path):
  # Robot need to come back to base
  row_sum = sum([i for i in path[0][1:]])
  col_sum = sum([path[j][0] for j in range (len(path[1:])+1)])
  return row_sum + col_sum == 2
  

def constraint_row_col_sum(path):
  # Robot cannot time travel (go to two points at the same time)
  for row in path:
    row_sum = sum([i for i in row])
    if row_sum > 1:
      return False
  for col in range(len(path)):
    col_sum = sum([path[j][col] for j in range(len(path))])
    if col_sum > 1:
      return False
  return True


def objective(samples, decisions):
  # Objective: Maximize the sample value
  return sum([samples[i].value * decisions[i] for i in range(len(decisions))])
