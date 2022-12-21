# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 19:56:00 2022

@author: Jairo Enrique
"""
import neat
from mypopulation import Population
import pickle
import numpy as np
from joblib import dump, load
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

class ai:
    
    
    def __init__(self, app, test = False):
        self.test = test
        self.model = load('JERS.joblib') 
        self.app = app
        self.p = None
        self.time_spent = 0
        self.generation = 0
        self.best_fitness_generation = []
        if test:
            self.car_per_generation = 1
        else:    
            self.car_per_generation = 15
        self.current_car = 0
        self.nets = []
        
        self.on_start()
        
        
        
    def on_start(self, test = False):
        config_path = "./config-feedforward.txt"
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    
            
        # Create core evolution algorithm class
        self.p = Population(config)
    
        # Add reporter for fancy statistical result
        self.p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        self.p.add_reporter(stats)
        
        
        self.initialize_fitness()
        
        """
        best = self.p.run(self.run_car, 2)
        
        with open("winner.pkl", "wb") as f:
            pickle.dump(best, f)
            f.close()
        """
        
        
    def initialize_fitness(self):
        if self.test:
            #genome_path = 'winners/1_winner_gen_0271.pkl'
            genome_path = 'winners/1_winner_gen_0007.pkl'
                # Unpickle saved winner
            with open(genome_path, "rb") as f:
                genome = pickle.load(f)
        
            genomes = [(1, genome)]
            config_path = "./config-feedforward.txt"
            config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                        neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

        else:
            genomes, config = self.p.get_genome()

        self.nets = []
        
        for id, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            self.nets.append(net)
            g.fitness = 0
        
              
    
    def run_car(self):
        
        death = False
        
        genomes, config = self.p.get_genome()
        
        self.time_spent += 1     

        # Input my data and get result from network
        radar = self.app.car_2.distance_to_off_circuit()
        
        #radar.append(self.app.car.velocity)
        
        radar.append(self.app.car_2.get_curviness())
        
        
        radar = np.array(radar)
        
        #radar[radar > 30] = 30
        
        output = self.nets[self.current_car].activate(radar)
        i = output.index(max(output))
        
        #i = self.model.predict(radar.reshape(1,-1))
        
        #print(self.model.predict_proba(radar.reshape(1,-1)))
        
        if i == 0:
            #self.app.car.move_forward()
            pass
            #print(f"Action: Move towards")
            
        elif i == 1:
            self.app.car_2.move_left()
            #print(f"Action: Move left")
        elif i == 2:
            self.app.car_2.move_right()
            #print(f"Action: Move right")
        elif i == 3:
            #print(f"Action: wait")
            pass
        
        if self.time_spent% 100 == 0:
            print(f"--------- CAR {self.current_car} for generation {self.generation} ---------")
            print(f"reward until time {self.time_spent}: {genomes[self.current_car][1].fitness}")
        
        if self.time_spent > 10_0000:
            death = True
            
        # Update car and fitness
        
        if not self.test:
            genomes[self.current_car][1].fitness += self.get_reward(self.app.car_2.velocity,
                                                  self.app.car_2.distance, 
                                                         self.time_spent)
        #print(f"Fitness: {genomes[self.current_car][1].fitness}")
        if not self.app.car_2.on_circuit():
            if not self.test:
                genomes[self.current_car][1].fitness -= 1e2
            death = True
    
    
        if death:
            self.current_car += 1
            self.app.car_2.distance = 0
            self.app.car_2.move_to_start()
            self.time_spent = 0
            print("New Car")
            #Y un reset a la posición del carro
            
        if self.current_car == self.car_per_generation:
            self.generation += 1
            self.current_car = 0
            if not self.test:
                self.p.reproduce()
                self.best_fitness_generation.append(self.p.best_genome.fitness)
                pd.DataFrame(self.best_fitness_generation).to_csv("Generations.csv")
                self.initialize_fitness()
                self.save()
    
    
    def save(self):
        
        with open(f"winners/winner_gen_{(4 - len(str(self.generation)) )* '0' + str(self.generation)}.pkl", "wb") as f:
            pickle.dump(self.p.best_genome, f)
            f.close()
    
        
        
    def get_reward(self, velocity, distance, time_spent):
        reward = 0
        reward -= 10 if velocity < 5 else 0
        reward -= 5 if velocity <= 10 and velocity >= 5 else 0
        reward += 10 if velocity > 10 else 0
        
        reward /= 3
        
        #reward = 100 if reward > 100 else reward
        #reward += 40 if self.speed > 10 else 0
        reward = distance / (time_spent / 5)
        
        #reward += 100 if self.app.car.check_if_on_checkpoint() else 0
        
        reward /= 100
            
        
        
        return reward