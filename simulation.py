import math
import random
import json
import matplotlib.pyplot as plt
from enum import Enum

# --- Enums for Sensors and Actions ---
class Sensor(Enum):
    AGE = 0
    BOUNDARY_DIST = 1
    BOUNDARY_DIST_X = 2
    BOUNDARY_DIST_Y = 3
    LAST_MOVE_DIR_X = 4
    LAST_MOVE_DIR_Y = 5
    LOC_X = 6
    LOC_Y = 7
    LONGPROBE_POP_FWD = 8
    LONGPROBE_BAR_FWD = 9
    BARRIER_FWD = 10
    BARRIER_LR = 11
    OSC1 = 12
    POPULATION = 13
    POPULATION_FWD = 14
    POPULATION_LR = 15
    RANDOM = 16
    SIGNAL0 = 17
    SIGNAL0_FWD = 18
    SIGNAL0_LR = 19
    GENETIC_SIM_FWD = 20
    NUM_SENSES = 21

class Action(Enum):
    MOVE_EAST = 0
    MOVE_WEST = 1
    MOVE_NORTH = 2
    MOVE_SOUTH = 3
    MOVE_FORWARD = 4
    MOVE_X = 5
    MOVE_Y = 6
    SET_RESPONSIVENESS = 7
    SET_OSCILLATOR_PERIOD = 8
    EMIT_SIGNAL0 = 9
    KILL_FORWARD = 10
    MOVE_REVERSE = 11
    MOVE_LEFT = 12
    MOVE_RIGHT = 13
    MOVE_RL = 14
    MOVE_RANDOM = 15
    SET_LONGPROBE_DIST = 16
    NUM_ACTIONS = 17

# --- Coord and Direction Types ---
class Coord:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def normalize(self):
        dx = 0 if self.x == 0 else int(self.x / abs(self.x))
        dy = 0 if self.y == 0 else int(self.y / abs(self.y))
        return Coord(dx, dy)

    def length(self):
        return int(math.sqrt(self.x ** 2 + self.y ** 2))

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)

    def ray_sameness(self, other):
        dot = self.x * other.x + self.y * other.y
        mag = math.sqrt(self.x**2 + self.y**2) * math.sqrt(other.x**2 + other.y**2)
        return 1.0 if mag == 0 else dot / mag

# --- Gene and Genome ---
class Gene:
    def __init__(self, source_type, source_num, sink_type, sink_num, weight):
        self.source_type = source_type
        self.source_num = source_num
        self.sink_type = sink_type
        self.sink_num = sink_num
        self.weight = weight

    def weight_as_float(self):
        return self.weight / 8192.0

class Genome:
    def __init__(self):
        self.genes = []

    def generate_random(self, min_length=10, max_length=20):
        length = random.randint(min_length, max_length)
        self.genes = []
        for _ in range(length):
            source_type = random.randint(0, 1)
            source_num = random.randint(0, Sensor.NUM_SENSES.value - 1 if source_type == 1 else 127)
            sink_type = random.randint(0, 1)
            sink_num = random.randint(0, Action.NUM_ACTIONS.value - 1 if sink_type == 1 else 127)
            weight = random.randint(-32768, 32767)
            self.genes.append(Gene(source_type, source_num, sink_type, sink_num, weight))

    def mutate(self, mutation_rate=0.01):
        for gene in self.genes:
            if random.random() < mutation_rate:
                gene.weight += random.randint(-1000, 1000)
                gene.weight = max(-32768, min(32767, gene.weight))

    def copy(self):
        g = Genome()
        g.genes = [Gene(e.source_type, e.source_num, e.sink_type, e.sink_num, e.weight) for e in self.genes]
        return g

# --- Neural Network ---
class Neuron:
    def __init__(self):
        self.output = 0.0
        self.driven = True

class NeuralNet:
    def __init__(self):
        self.connections = []
        self.neurons = []

    def build_from_genome(self, genome):
        self.connections = genome.genes.copy()
        self.neurons = [Neuron() for _ in range(128)]

    def feed_forward(self, sensors):
        neuron_inputs = [0.0 for _ in self.neurons]
        action_outputs = [0.0 for _ in range(Action.NUM_ACTIONS.value)]
        for conn in self.connections:
            val = sensors[conn.source_num] if conn.source_type == 1 else self.neurons[conn.source_num].output
            weighted = val * conn.weight_as_float()
            if conn.sink_type == 1:
                action_outputs[conn.sink_num] += weighted
            else:
                neuron_inputs[conn.sink_num] += weighted
        for i, neuron in enumerate(self.neurons):
            if neuron.driven:
                neuron.output = math.tanh(neuron_inputs[i])
        return action_outputs

# --- Individual ---
class Indiv:
    def __init__(self, genome=None):
        self.genome = genome.copy() if genome else Genome()
        if genome is None:
            self.genome.generate_random()
        self.nnet = NeuralNet()
        self.nnet.build_from_genome(self.genome)
        self.loc = Coord()
        self.facing = random.choice([Coord(1,0), Coord(-1,0), Coord(0,1), Coord(0,-1)])
        self.alive = True
        self.oscillator_phase = 0.0
        self.oscillator_period = 10.0
        self.responsiveness = 1.0

    def execute_actions(self, actions, signal_layer, population):
        self.responsiveness = max(0.1, min(10.0, actions[Action.SET_RESPONSIVENESS.value]))
        self.oscillator_period = max(1.0, min(100.0, actions[Action.SET_OSCILLATOR_PERIOD.value]))

        move_vector = Coord(0,0)
        if actions[Action.MOVE_FORWARD.value] > 0.5:
            move_vector += self.facing
        if actions[Action.MOVE_REVERSE.value] > 0.5:
            move_vector += Coord(-self.facing.x, -self.facing.y)
        if actions[Action.MOVE_LEFT.value] > 0.5:
            move_vector += Coord(-self.facing.y, self.facing.x)
        if actions[Action.MOVE_RIGHT.value] > 0.5:
            move_vector += Coord(self.facing.y, -self.facing.x)
        if actions[Action.MOVE_RANDOM.value] > 0.5:
            move_vector += Coord(random.choice([-1,0,1]), random.choice([-1,0,1]))

        self.loc.x += max(-1, min(1, move_vector.x))
        self.loc.y += max(-1, min(1, move_vector.y))

        if 0 <= self.loc.x < len(signal_layer.grid) and 0 <= self.loc.y < len(signal_layer.grid[0]):
            if actions[Action.EMIT_SIGNAL0.value] > 0.5:
                signal_layer.increment(self.loc.x, self.loc.y)

        if actions[Action.KILL_FORWARD.value] > 0.5:
            target = self.loc + self.facing
            for other in population:
                if other.alive and other.loc.x == target.x and other.loc.y == target.y:
                    other.alive = False

        self.oscillator_phase += 1.0 / self.oscillator_period
        if self.oscillator_phase > 1.0:
            self.oscillator_phase -= 1.0

    def get_sensor_value(self, sensor, signals, population):
        if sensor == Sensor.OSC1.value:
            return math.sin(2 * math.pi * self.oscillator_phase)
        elif sensor == Sensor.SIGNAL0.value:
            return signals.grid[self.loc.x][self.loc.y] if 0 <= self.loc.x < len(signals.grid) and 0 <= self.loc.y < len(signals.grid[0]) else 0
        elif sensor == Sensor.LONGPROBE_POP_FWD.value:
            probe = self.loc + self.facing
            for other in population:
                if other.alive and other.loc.x == probe.x and other.loc.y == probe.y:
                    return 1.0
            return 0.0
        return random.random()

# --- Signal Layer ---
class SignalLayer:
    def __init__(self, size_x, size_y):
        self.grid = [[0 for _ in range(size_y)] for _ in range(size_x)]

    def increment(self, x, y):
        self.grid[x][y] += 1

    def fade(self):
        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                self.grid[x][y] = max(0, self.grid[x][y] - 1)

# --- Simulation Parameters ---
class Parameters:
    def __init__(self, config_file=None):
        self.size_x = 100
        self.size_y = 100
        self.population = 100
        self.steps_per_generation = 50
        self.mutation_rate = 0.01
        self.survivor_fraction = 0.2
        self.visualise_interval = 2
        if config_file:
            self.load_config(config_file)

    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)

# --- Simulation ---
class Simulation:
    def __init__(self, config_file=None):
        self.params = Parameters(config_file)
        self.population = [Indiv() for _ in range(self.params.population)]
        self.signals = SignalLayer(self.params.size_x, self.params.size_y)

    def run_generation(self):
        for _ in range(self.params.steps_per_generation):
            for indiv in self.population:
                if indiv.alive:
                    sensors = [indiv.get_sensor_value(i, self.signals, self.population) for i in range(Sensor.NUM_SENSES.value)]
                    actions = indiv.nnet.feed_forward(sensors)
                    indiv.execute_actions(actions, self.signals, self.population)
            self.signals.fade()

    def reproduce(self):
        survivors = [indiv for indiv in self.population if indiv.alive]
        if not survivors:
            survivors = random.sample(self.population, 1)
        self.population = [Indiv(random.choice(survivors).genome.copy().mutate(self.params.mutation_rate)) for _ in range(self.params.population)]

    def visualise(self, generation):
        grid = [[0 for _ in range(self.params.size_y)] for _ in range(self.params.size_x)]
        for indiv in self.population:
            if indiv.alive:
                x, y = indiv.loc.x, indiv.loc.y
                if 0 <= x < self.params.size_x and 0 <= y < self.params.size_y:
                    grid[x][y] = 1
        combined_grid = [[grid[x][y] + 0.5 * self.signals.grid[x][y] for y in range(self.params.size_y)] for x in range(self.params.size_x)]
        plt.imshow(combined_grid, cmap='hot', interpolation='nearest')
        plt.title(f'Simulation Generation {generation}')
        plt.show()

    def log_stats(self, generation):
        alive_count = sum(1 for indiv in self.population if indiv.alive)
        print(f"Generation {generation}: Alive {alive_count}/{self.params.population}")

# --- Entry Point ---
if __name__ == "__main__":
    sim = Simulation()
    for gen in range(10):
        sim.run_generation()
        sim.log_stats(gen)
        if gen % sim.params.visualise_interval == 0:
            sim.visualise(gen)
        sim.reproduce()

