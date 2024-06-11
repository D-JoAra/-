# import numpy as np
import random
import copy

class np:
    @staticmethod
    def sign(x):
        if x > 0:
            return 1
        if x < 0:
            return -1
        else:
            return 0

    @staticmethod
    def clip(x, y, z):
        if x < y:
            return y
        if x > z:
            return z
        else:
            return x

    @staticmethod
    def mean(x):
        res = 0
        for i in x:
            res += i

        res = res/len(x)
        return res

# Visualize the final opinion distribution changes over cycles
def visualize_final_opinion_distribution(opinion_distribution, title):
    pass

    final_opinions = opinion_distribution[-1]

# Entity class with attributes
class Entity:
    def __init__(self, id, P, F, C, H):
        self.id = id
        self.P = P
        self.F = F
        self.C = C
        self.H = H


# Create entities with uniform opinion distribution and symmetric pairs
def create_entities(num_entities, num_hate_types=3):
    entities = []
    possible_features = list(range(1, num_hate_types + 1))
    possible_hates = list(range(1, num_hate_types + 1))
    half_num_entities = num_entities // 2

    P_values = list(range(-5, 0)) + list(range(1, 6))
    F_values = list(range(1, 11))
    combinations = [(P, F) for P in P_values for F in F_values]
    random.shuffle(combinations)

    num_feature_holders = num_entities // 20
    feature_holders = random.sample(range(num_entities), num_feature_holders)
    hate_holders = random.sample(range(num_entities), num_feature_holders)

    for i in range(half_num_entities):
        P, F = combinations[i % len(combinations)]
        C = [possible_features[i % len(possible_features)]] if i in feature_holders else []
        possible_hates_filtered = [h for h in possible_hates if h not in C]
        if i in hate_holders:
            H = random.sample(possible_hates_filtered,
                              min(len(possible_hates_filtered), random.randint(1, num_hate_types)))
        else:
            H = []
        entities.append(Entity(i, P, F, C, H))

    for i in range(half_num_entities):
        original_entity = entities[i]
        opposite_entity = Entity(i + half_num_entities, -original_entity.P, original_entity.F, original_entity.C,
                                 original_entity.H)
        entities.append(opposite_entity)

    return entities

def create_entities2(num_entities, num_hate_types=1):
    entities = []
    possible_features = list(range(1, num_hate_types + 1))
    possible_hates = list(range(1, num_hate_types + 1))
    half_num_entities = num_entities // 2

    P_values = list(range(-5, 0)) + list(range(1, 6))
    F_values = list(range(1, 11))
    combinations = [(P, F) for P in P_values for F in F_values]
    random.shuffle(combinations)

    num_feature_holders = num_entities // 20
    feature_holders = random.sample(range(num_entities), num_feature_holders)
    hate_holders = random.sample(range(num_entities), num_feature_holders)

    for i in range(half_num_entities):
        P, F = combinations[i % len(combinations)]
        C = [possible_features[i % len(possible_features)]] if i in feature_holders else []
        possible_hates_filtered = [h for h in possible_hates if h not in C]
        if i in hate_holders:
            H = random.sample(possible_hates_filtered,
                              min(len(possible_hates_filtered), random.randint(1, num_hate_types)))
        else:
            H = []
        entities.append(Entity(i, P, F, C, []))

    for i in range(half_num_entities):
        original_entity = entities[i]
        opposite_entity = Entity(i + half_num_entities, -original_entity.P, original_entity.F, [],
                                 original_entity.C)
        entities.append(opposite_entity)

    return entities

# Simulate interaction between two entities
def simulate_interaction(entity1, entity2):
    if abs(entity1.P * entity1.F) > abs(entity2.P * entity2.F):
        winner, loser = entity1, entity2
    elif abs(entity1.P * entity1.F) < abs(entity2.P * entity2.F):
        winner, loser = entity2, entity1
    else:
        # If tied, randomize winner and loser
        if random.random() > 0.5:
            winner, loser = entity1, entity2
        else:
            winner, loser = entity2, entity1

    new_P = round((winner.P * winner.F + loser.P * loser.F) / (winner.F + loser.F))
    loser.P = np.clip(new_P, -5, 5)

    return winner, loser


# Run the simulation with entities and cycles
def run_simulation(num_entities, cycles=50, options=[]):
    entities = create_entities2(num_entities)
    entities_dict = {e.id: e for e in entities}  # Use a dictionary for faster access
    initial_entities = copy.deepcopy(entities_dict)
    opinion_distribution = []
    pairs_per_cycle = []

    for cycle in range(cycles):
        pairs = []
        entity_ids_shuffled = random.sample(list(entities_dict.keys()), len(entities_dict))

        for i in range(0, len(entity_ids_shuffled) - 1, 2):
            pairs.append((entity_ids_shuffled[i], entity_ids_shuffled[i + 1]))

        pairs_per_cycle.append(pairs)

        for entity1_id, entity2_id in pairs:
            entity1 = entities_dict[entity1_id]
            entity2 = entities_dict[entity2_id]
            if 'no_interaction_hate' in options:
                if (any(h in entity2.C for h in entity1.H) or any(h in entity1.C for h in entity2.H)) \
                        and np.sign(entity1.P) != np.sign(entity2.P):
                    continue  # Skip interaction if option is set
            simulate_interaction(entity1, entity2)

        opinions = [e.P for e in entities_dict.values()]
        opinion_distribution.append(opinions)

    return opinion_distribution, pairs_per_cycle, initial_entities


# Run the simulation with predefined pairs
def run_simulation_with_pairs(initial_entities, pairs_per_cycle, cycles=50, options=[]):
    entities_dict = copy.deepcopy(initial_entities)
    opinion_distribution = []

    for cycle in range(cycles):
        pairs = pairs_per_cycle[cycle]

        for entity1_id, entity2_id in pairs:
            entity1 = entities_dict[entity1_id]
            entity2 = entities_dict[entity2_id]
            if 'no_interaction_hate' in options:
                if any(h in entity2.C for h in entity1.H) or any(h in entity1.C for h in entity2.H)\
                        and np.sign(entity1.P) != np.sign(entity2.P):
                    continue  # Skip interaction if option is set
            simulate_interaction(entity1, entity2)

        opinions = [e.P for e in entities_dict.values()]
        opinion_distribution.append(opinions)

    return opinion_distribution


# Calculate convergence speed
def calculate_convergence_speed(opinion_distribution, threshold=0.9):
    total_entities = len(opinion_distribution[0])
    for cycle, opinions in enumerate(opinion_distribution):
        positive_count = sum(1 for p in opinions if p > 0)
        negative_count = sum(1 for p in opinions if p < 0)
        if positive_count / total_entities >= threshold or negative_count / total_entities >= threshold:
            return cycle
    return len(opinion_distribution)


# Run multiple simulations and calculate convergence speed
def run_multiple_simulations(num_simulations=50, num_entities=1500, cycles=50):
    convergence_speeds_no_options = []
    convergence_speeds_with_options = []


    for _ in range(num_simulations):
        opinion_distribution_no_options, pairs_per_cycle, initial_entities = run_simulation(num_entities, cycles)
        opinion_distribution_with_options = run_simulation_with_pairs(initial_entities, pairs_per_cycle, cycles,
                                                                      ['no_interaction_hate'])

        speed_no_options = calculate_convergence_speed(opinion_distribution_no_options)
        speed_with_options = calculate_convergence_speed(opinion_distribution_with_options)

        convergence_speeds_no_options.append(speed_no_options)
        convergence_speeds_with_options.append(speed_with_options)
    _, pairs_per_cycle, initial_entities = run_simulation(num_entities, cycles)
    opinion_distribution_no_options = run_simulation_with_pairs(initial_entities, pairs_per_cycle, cycles)
    opinion_distribution_with_options = run_simulation_with_pairs(initial_entities, pairs_per_cycle, cycles, ['no_interaction_hate'])

#    visualize_final_opinion_distribution(opinion_distribution_no_options, 'Without Options')
#    visualize_final_opinion_distribution(opinion_distribution_with_options, 'With Options')

    return convergence_speeds_no_options, convergence_speeds_with_options


# Calculate the average convergence speed
def calculate_average_convergence_speed(num_simulations=50, num_entities=1500, cycles=50):
    convergence_speeds_no_options, convergence_speeds_with_options = run_multiple_simulations(
        num_simulations, num_entities, cycles)

    average_speed_no_options = np.mean(convergence_speeds_no_options)
    average_speed_with_options = np.mean(convergence_speeds_with_options)

    return average_speed_no_options, average_speed_with_options


# Get the average convergence speeds
n = 0
res = ''
res1 = 0
res2 = 0
file_name = "result.txt"

while n != 10:
    n += 1
    average_speed_no_options, average_speed_with_options = calculate_average_convergence_speed(cycles=120, num_simulations=50, )
    print(f'```fig{n}')
    print(f"convergence speed without options: {average_speed_no_options:.2f} cycles")
    print(f"convergence speed with options: {average_speed_with_options:.2f} cycles")
    print('```')
    res += f'```fig{n} \n' + f"convergence speed without options: {average_speed_no_options:.2f} cycles \n" \
           + f"convergence speed with options: {average_speed_with_options:.2f} cycles \n" + '```'

    if average_speed_no_options < average_speed_with_options:
        print("without option wins")
        res += "\n without option wins \n"
        res1 += 1
    else:
        print("with option wins")
        res += "\n with option wins \n"
        res2 += 1

    with open(file_name, 'a') as f:
        f.write(res)
    res = ''

# print(f"without option wins for {res1} times")
# print(f"with option wins for {res2} times")

# res += f"without option wins for {res1} times \n" + f"with option wins for {res2} times"


with open(file_name, 'a') as f:
    f.write(res)
