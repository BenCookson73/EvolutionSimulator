from dataclasses import dataclass
import random, math

def flatten(inputs: list): #flattens compound list to single array
        flat = list()
        for obj in inputs:
            if type(obj)==list or type(obj)==tuple:
                flat += flatten(obj)
            else:
                flat.append(obj)
        return flat




@dataclass
class Input:
    def __init__(self, value, weight):
        self.value = value
        self.weight = weight




class Neuron:
    def __init__(self, out_range, next_layer_n_neurons):
        self.bias = Input(1, 1)
        self.value = 1
        self.out_range = out_range
        self.weights = [1 for _ in range(next_layer_n_neurons)] #the weights used for output

    def random_weights(self):
        self.bias.value = random.uniform(0, 255) #just because most values are between this, no significance
        self.bias.weight = random.uniform(-1, 1)
        for n in range(len(self.weights)):
            self.weights[n] = random.uniform(-1, 1)

    def process(self, *inputs):
        self.value = 0
        self.value += self.bias.value * self.bias.weight
        for inp in inputs:
            self.value += inp.value*inp.weight  #adds up all of the inputs multiplied by their weights
        #activation function
        if self.out_range == (-1, 1):
            AllBetweenLimits = True
            for inp in inputs:
                if inp.value>1 or inp.value<-1:
                    AllBetweenLimits=False
                    break
            if AllBetweenLimits:
                self.value *= 10
            self.value = math.sin(math.radians(self.value)) #sine limits -1 ~ 1
        elif self.out_range == (0, 1):
            self.value /= len(inputs)
            self.value = 1 / (1 + math.e**-self.value) #logistic sigmoid function limits 0 ~ 1

    def __add__(n1, n2):
        neuron = Neuron(min(n1.out_range, n2.out_range), max([len(n1.weights), len(n2.weights)]))
        for n in range(min([len(n1.weights), len(n2.weights)])):
            neuron.weights[n] = (n1.weights[n]+n2.weights[n])/2
        if len(n1.weights)>len(n2.weights):
            for n in range(len(n2.weights), len(n1.weights)):
                neuron.weights[n] = n1.weights[n]
        elif len(n2.weights)>len(n1.weights):
            for n in range(len(n1.weights), len(n2.weights)):
                neuron.weights[n] = n2.weights[n]
        neuron.bias.value = random.uniform(0.8, 1.2) * ((n1.bias.value+n2.bias.value)/2) #adds bias and differentiates
        neuron.bias.weight = random.uniform(0.8, 1.2) * ((n1.bias.weight+n2.bias.weight)/2) #adds bias and differentiates
        for n in range(len(neuron.weights)):                 #adds differentiation
            neuron.weights[n] *= random.uniform(0.8, 1.2)
        return neuron
    
    def to_input(self, neuron_going_to):
        return Input(self.value, self.weights[neuron_going_to])

        
class Layer:
    def __init__(self, n_neurons, next_layer_n_neurons, out_range):
        self.out_range = out_range
        self.next_layer_n_neurons = next_layer_n_neurons
        self.neurons = [Neuron(out_range, next_layer_n_neurons) for _ in range(n_neurons)]

    def process(self, pre_layer):
        for i in range(len(self.neurons)):
            inputs = [pre_layer.neurons[j].to_input(i) for j in range(len(pre_layer.neurons))]
            self.neurons[i].process(*inputs)

    def randomise(self):
        for neuron in self.neurons:
            neuron.random_weights()

    def __add__(l1, l2):
        layer = Layer(max([len(l1.neurons), len(l2.neurons)]), max([l1.next_layer_n_neurons, l2.next_layer_n_neurons]), min(l1.out_range, l2.out_range))
        for n in range(min([len(l1.neurons), len(l2.neurons)])):
            layer.neurons[n] = l1.neurons[n]+l2.neurons[n]
        if len(l1.neurons)>len(l2.neurons):
            for n in range(len(l2.neurons), len(n1.neurons)):
                layer.neurons[n] = n1.neurons[n]
        elif len(l2.neurons)>len(l1.neurons):
            for n in range(len(l1.neurons), len(l2.neurons)):
                layer.neurons[n] = l2.neurons[n]
        return layer
        
class NeuralNetwork:
    def __init__(self, n_inputs, n_layers, layer_sizes, out_range):
        """used to create an array of layers"""
        self.out_range = out_range
        self.n_inputs = n_inputs
        self.layers = [Layer(n_inputs, layer_sizes[0], out_range)]
        for n in range(0, n_layers-1):
            self.layers.append(Layer(layer_sizes[n], layer_sizes[n+1], out_range))
        self.layers.append(Layer(layer_sizes[-1], 0, out_range))

    def randomise(self):
        for layer in self.layers:
            layer.randomise()

    def new_input_size(self, n_inputs):
        if n_inputs < self.n_inputs:
            self.layers[0].neurons = self.layers[0].neurons[:n_inputs]
        elif n_inputs > self.n_inputs:
            for _ in range(self.n_inputs, n_inputs):
                n = Neuron(len(self.layers[1].neurons))
                n.randomise()
                self.layers[0].neurons.append(n)
            
    def process(self, *inputs):
        for i in range(len(inputs)):
            self.layers[0].neurons[i].value = inputs[i]
        for i in range(1, len(self.layers)):
            self.layers[i].process(self.layers[i-1])
        outputs = []
        for i in range(len(self.layers[-1].neurons)):
            outputs.append(self.layers[-1].neurons[i].value)
        return self.output()

    def output(self):
        return [neuron.value for neuron in self.layers[-1].neurons]
    
    def __add__(n1, n2):
        layer_sizes = [None for _ in range(max([len(n1.layers), len(n2.layers)]))] #creates empty list size of the number of layers
        for layer in range(min([len(n1.layers), len(n2.layers)])): #loops through layers n1 and n2 have in common
            layer_sizes[layer] = max([len(n1.layers[layer].neurons), len(n2.layers[layer].neurons)]) #layer size will be size of biggest layer
        if len(n1.layers) > len(n2.layers): #if n1 has more layers than n2
            for layer in range(len(n2.layers), len(n1.layers)):
                layer_sizes[layer] = len(n1.layers[layer].neurons)
        elif len(n2.layers) > len(n1.layers): #if n2 has more layers than n1
            for layer in range(len(n1.layers), len(n2.layers)):
                layer_sizes[layer] = len(n2.layers[layer].neurons)
        network = NeuralNetwork(layer_sizes[0], len(layer_sizes)-1, layer_sizes[1:], min(n1.out_range, n2.out_range))
        network.layers[0] = n1.layers[0]+n2.layers[0]
        for layer in range(1, min([len(n1.layers), len(n2.layers)])):
            if layer!=len(network.layers)-1:
                network.layers[layer] = n1.layers[layer]+n2.layers[layer]
        if len(n1.layers) > len(n2.layers):
            for layer in range(len(n2.layers), len(n1.layers)):
                    network.layers[layer] = n1.layers[layer]
        elif len(n2.layers) > len(n1.layers):
            for layer in range(len(n1.layers), len(n2.layers)):
                network.layers[layer] = n2.layers[layer]
        return network
            
class Brain:
    "deep learning network"
    def __init__(self, vision_resolution, max_distance):
        self.vision_resolution = int(vision_resolution)
        self.max_distance = max_distance
        self.distance_neural_network = NeuralNetwork(int(vision_resolution)*5+3, 5, [128, 256, 256, 128, 1], (-1, 1))
        self.angle_neural_network = NeuralNetwork(int(vision_resolution)*5+3, 5, [128, 256, 256, 128, 1], (-1, 1))

    def randomise(self):
        self.distance_neural_network.randomise()
        self.angle_neural_network.randomise()
        
    def process(self, vision, health, energy, time_since_last_reproduction):
        """
        works out how far to move and how much to turn when moving
        distance to move can be -1 to 1     multiplied by max distance
        angle to turn    can be -1 to 1     multiplied by 180
        """
        inputs = flatten(vision + [health, energy, time_since_last_reproduction])
        self.distance_neural_network.process(*inputs)
        self.angle_neural_network.process(*inputs)
        distance = self.max_distance * self.distance_neural_network.layers[-1].neurons[0].value
        angle = 360 * self.angle_neural_network.layers[-1].neurons[0]
        return distance, angle
    

    def combine(b1, b2, vision_resolution, max_distance):
        b = Brain(vision_resolution, max_distance)
        b.distance_neural_network = b1.distance_neural_network+b2.distance_neural_network
        b.angle_neural_network = b1.angle_neural_network+b2.angle_neural_network
        b.distance_neural_network.new_input_size(max(b1.distance_neural_network.n_inputs, b2.distance_neural_network.n_inputs))
        b.angle_neural_network.new_input_size(max(b1.angle_neural_network.n_inputs, b2.angle_neural_network.n_inputs))
        return b
