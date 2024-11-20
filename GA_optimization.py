
"""
Genetic Algorithm optimization
"""

import random
import numpy as np
from deap import base, creator, tools, algorithms
import yfinance as yf
from triple_barrier_method import TripleBarrierMethod
from equity_strategy import EquityStrategy

# test on a stock value
data_daily = yf.download('AAPL', start='2020-01-01', end='2024-12-31', interval='1d')
target_price = data_daily['Close']

## Optimization ============================================================================================================

def evaluate_individual(individual)-> tuple:
    """
    evaluate one indivual
    :individual: 5 parameters of one individual
    :return: fitness value (deap need a tuple as fitness value)
    """
    # one individual is 5 parameters
    lower_barrier, upper_barrier, time_barrier, buy_number, sell_number = individual 
    
    # constraints
    if -0.5 < lower_barrier < 0 and 0 < upper_barrier < 0.5 and 1 < buy_number < 10 and 1 < sell_number < 10 and 1 < time_barrier < 1000:
    
        # label using TBM
        tbm = TripleBarrierMethod(target_price, lower_barrier=lower_barrier, upper_barrier=upper_barrier, time_barrier=int(time_barrier))
        df_labeled = tbm.label_data()
        
        # compute fitness based on my equity strategy
        equity_strategy = EquityStrategy(df=df_labeled, buy_number=buy_number, sell_number=sell_number)
        fitness = (equity_strategy.fitness_function(weight_p=0.3, weight_mdd=0.7),)

    else:
        fitness = (0.0,)

    return fitness
    

# DEAP settings
creator.create("FitnessMax", base.Fitness, weights=(1.0,))  # goal : maximizing fitness value
creator.create("Individual", list, fitness=creator.FitnessMax) # individual lists definition

# defining individuals and population
toolbox = base.Toolbox()

# defining constraints
toolbox.register("attr_lower_barrier", random.uniform, -0.5, 0)
toolbox.register("attr_upper_barrier", random.uniform, 0, 0.5)
toolbox.register("attr_time_barrier", random.randint, 1, 1000)
toolbox.register("attr_buy_number", random.randint, 1, 10)
toolbox.register("attr_sell_number", random.randint, 1, 10)

# defining creation of one individual
toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.attr_lower_barrier,
                  toolbox.attr_upper_barrier,
                  toolbox.attr_time_barrier,
                  toolbox.attr_buy_number,
                  toolbox.attr_sell_number),
                 n=1)

# defining creation of the population
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# defining computation fitness function
toolbox.register("evaluate", evaluate_individual)

# defining genetic operations
toolbox.register("mate", tools.cxBlend, alpha=0.5) # crossover / alpha : crossover variability
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2) # mutation / random draw in gaussian distribution
toolbox.register("select", tools.selTournament, tournsize=5) # selection / 5 individuals chosen

# genetic algorithm hyperparameters
population_size = 20
generations = 5
crossover_probability = 0.7
mutation_probability = 0.2

# initial population creation
population = toolbox.population(n=population_size)

# compute genetic algorithm
for generation in range(generations):
    print(f"{'-'*30} Generation {generation + 1}/{generations} {'-'*30}\n")
    offspring = algorithms.varAnd(population, toolbox, cxpb=crossover_probability, mutpb=mutation_probability)
    fits = toolbox.map(toolbox.evaluate, offspring)

    # evaluate individuals
    i=0
    for fit, ind in zip(fits, offspring):
        i += 1
        ind.fitness.values = fit
        print(f"individual {i}/{population_size}: {np.round(ind, 2)}, fitness: {np.round(fit, 2)}")
    # select next generation
    population = toolbox.select(offspring, k=population_size)


best_individual = tools.selBest(population, k=1)[0]
best_fitness = best_individual.fitness.values[0]
print("best individual:", best_individual)
print("best fitness:", best_fitness)

# plot best individual using its TBM

tbm = TripleBarrierMethod(target_price, lower_barrier=best_individual[0], upper_barrier=best_individual[1], time_barrier=int(best_individual[2]))
df_labeled = tbm.label_data()
tbm.plot_labels(colors=['#ff0000', '#7945d9', '#0fff00'], title='Labeled Price Data')
tbm.plot_square(date='2022-01-07 00:00:00+00:00', title='Triple-Barrier square exemple')

