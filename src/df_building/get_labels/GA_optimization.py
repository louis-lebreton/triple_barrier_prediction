"""
@author: Louis Lebreton
Genetic Algorithm optimization of TBM (Triple Barrier method) based on an equity strategy
"""
import random
import numpy as np
from deap import base, creator, tools, algorithms
from functools import partial
from df_building.get_labels.triple_barrier_method import TripleBarrierMethod
from df_building.get_labels.equity_strategy import EquityStrategy


def evaluate_individual(individual, weight_p: float, weight_mdd: float, target_price )-> tuple:
    """
    evaluate one indivual (5 parameters).
    gives the fitness depending on the weight_p and weight_mdd.

    :target_price: time series of target prices to analyze
    :individual: 5 parameters of one individual
    :weight_p: weight of profit
    :weight_mdd: weight of maximum drawdown
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
        fitness = (equity_strategy.fitness_function(weight_p=weight_p, weight_mdd=weight_mdd),)

    else:
        fitness = (0.0,)

    return fitness
    

def run_genetic_algorithm(toolbox, population_size, nb_gen, crossover, mutation) -> tuple:
    """
    execute genetic algorithm and return the best individual and its fitness
    
    :param toolbox: configured DEAP toolbox
    :param population_size: population_size
    :param nb_gen: nb of generations
    :param crossover: crossover probability.
    :param mutation: mutation probability.
    :return: Tuple containing the best individual and its fitness.
    """
    # population creation
    population = toolbox.population(n=population_size)
    
    for generation in range(nb_gen):
        print(f"\n{'-'*40} Generation {generation + 1}/{nb_gen} {'-'*40}\n")
        
        offspring = algorithms.varAnd(population, toolbox, cxpb=crossover, mutpb=mutation)
        fits = toolbox.map(toolbox.evaluate, offspring)

        # evaluate individuals and assign fitness
        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
            print(f"Individual: {np.round(np.array(ind), 2)}, Fitness: {np.round(fit, 2)}")
        
        # next generation
        population = toolbox.select(offspring, k=population_size)

        # the best individual of the generation
        best_individual = tools.selBest(population, k=1)[0]
        best_fitness = best_individual.fitness.values[0]
        print(f"\nBest individual of generation {generation + 1}: {np.round(np.array(best_individual), 2)}")
        print(f"Best fitness of generation {generation + 1}: {np.round(best_fitness, 2)}")

    # best individual and its fitness
    best_individual = tools.selBest(population, k=1)[0]
    best_fitness = best_individual.fitness.values[0]

    return best_individual, best_fitness

if __name__ == '__main__':

    # test on a stock value
    import yfinance as yf
    data_daily = yf.download('AAPL', start='2020-01-01', end='2024-12-31', interval='1d')
    target_price = data_daily['Close']

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
    toolbox.register("evaluate", partial(evaluate_individual, weight_p=0.7, weight_mdd=0.3))

    # defining genetic operations
    toolbox.register("mate", tools.cxBlend, alpha=0.5) # crossover / alpha : crossover variability
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2) # mutation / random draw in gaussian distribution
    toolbox.register("select", tools.selTournament, tournsize=5) # selection / 5 individuals chosen

    best_individual, best_fitness = run_genetic_algorithm(toolbox, population_size= 50, nb_gen=5, crossover=0.7, mutation=0.2)

    # plot best individual using its TBM
    tbm = TripleBarrierMethod(target_price, lower_barrier=best_individual[0], upper_barrier=best_individual[1], time_barrier=int(best_individual[2]))
    df_labeled = tbm.label_data()
    tbm.plot_labels(colors=['#ff0000', '#7945d9', '#0fff00'], title='Labeled Price Data')
    tbm.plot_square(date='2023-02-08 00:00:00', title='Triple-Barrier square exemple')

    df_labeled.to_csv('data/AAPL_df_labeled_test.csv', sep=',', index=True)