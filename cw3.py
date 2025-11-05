import random

N = 8
POPULATION_SIZE = 100
MAX_ITERATIONS = 10000
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.2

def calculate_fitness(individual):
    collisions = 0
    for i in range(N):
        for j in range(i + 1, N):
            if abs(i - j) == abs(individual[i] - individual[j]):
                collisions += 1
    return collisions

def initialize_population(size):
    population = []
    for _ in range(size):
        individual = list(range(N))
        random.shuffle(individual) 
        population.append(individual)
    return population

def get_two_unique_indices(max_val):
    idx1 = random.randint(0, max_val - 1)
    idx2 = random.randint(0, max_val - 1)
    while idx1 == idx2:
        idx2 = random.randint(0, max_val - 1)
    return idx1, idx2

def crossover_ox(parent1, parent2):
    start, end = get_two_unique_indices(N)
    if start > end:
        start, end = end, start
    
    child1 = [None] * N
    child1[start:end] = parent1[start:end]
    p2_index = end
    c1_index = end
    while None in child1:
        if parent2[p2_index % N] not in child1:
            child1[c1_index % N] = parent2[p2_index % N]
            c1_index += 1
        p2_index += 1
        
    child2 = [None] * N
    child2[start:end] = parent2[start:end]
    p1_index = end
    c2_index = end
    while None in child2:
        if parent1[p1_index % N] not in child2:
            child2[c2_index % N] = parent1[p1_index % N]
            c2_index += 1
        p1_index += 1
        
    return child1, child2

def mutate_swap(individual):
    idx1, idx2 = get_two_unique_indices(N)
    
    individual[idx1], individual[idx2] = individual[idx2], individual[idx1]
    return individual

def selection(population, fitnesses, size):
    combined = sorted(zip(population, fitnesses), key=lambda x: x[1])
    elite_population = [ind for ind, fitness in combined[:size]]
    return elite_population

def solve_n_queens_ga():
    population = initialize_population(POPULATION_SIZE)
    best_solution = None
    best_fitness = float('inf')
    
    for iteration in range(MAX_ITERATIONS):
        fitnesses = [calculate_fitness(ind) for ind in population]
        min_fitness = min(fitnesses)
        
        if min_fitness < best_fitness:
            best_fitness = min_fitness
            best_solution = population[fitnesses.index(min_fitness)]
            print(f"Iteracja: {iteration + 1}. Minimalny błąd: {best_fitness}")
            
        if best_fitness == 0:
            print(f"Iteracja: {iteration + 1} - odnaleziono ustawienie!")
            return best_solution, iteration + 1
            
        selected_population = selection(population, fitnesses, POPULATION_SIZE)
        new_population = []
        
        while len(new_population) < POPULATION_SIZE:
            p1, p2 = random.choices(selected_population, k=2)
            
            if random.random() < CROSSOVER_RATE:
                c1, c2 = crossover_ox(p1, p2)
            else:
                c1, c2 = p1[:], p2[:]
                
            if random.random() < MUTATION_RATE:
                c1 = mutate_swap(c1)
            if random.random() < MUTATION_RATE:
                c2 = mutate_swap(c2)
                
            new_population.append(c1)
            if len(new_population) < POPULATION_SIZE:
                 new_population.append(c2)
            
        population = new_population
        
    print(f"Iteracja: {MAX_ITERATIONS}. Osiągnięto limit iteracji. Błąd końcowy: {best_fitness}")
    return best_solution, MAX_ITERATIONS

def print_board(solution):
    if solution is None:
        print("Brak rozwiązania do wyświetlenia.")
        return
    
    print(f"Lista: {', '.join(map(str, solution))}")

    print("\n   " + "".join(chr(ord('A') + i) for i in range(N)))
    for i in range(N):
        row = str(i + 1) + " "
        for j in range(N):
            if solution[i] == j:
                row += "X"
            else:
                row += "."
        print(row)

final_solution, final_iteration = solve_n_queens_ga()
if final_solution is not None:
    print_board(final_solution)