
import pygame
import sys, math, random, string, time, os, pickle
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,

)
from genome import *
from brain import *

DEBUG = False
if DEBUG:
    f = open('debug.txt','w')
    sys.stdout = f
    
WIDTH = 600
HEIGHT = 400
DIRECTION_LINE_LEN = 30
screen = None
ENERGY_DENSITY = 10 #amount energy goes up per pixel^2 of mass
ENERGY_HEALTH_GAIN = 0.15 #amount 1 energy increases health by
MAX_HEALTH_GAIN = 0.3 #percentage of health that can be regained in 1 tick (0~1)
CREATURE_DENSITY = 0.05
PLANT_DENSITY = 0.005



class Creature(pygame.sprite.Sprite):
    def __init__(self, x, y, genome=None, brain=None):
        """"""
        self.ID = ''.join([random.choice(string.ascii_uppercase) for _ in range(5)])
        super().__init__()
        if genome: self.genome = genome
        else: self.genome = Genome()
        self.brain = brain
        self.pos = [x, y]
        self.angle = 0
        self.image = pygame.Surface(self.genome.size.value)
        self.image.fill(self.genome.color.value)
        self.rect = self.image.get_rect()
        screen.blit(self.image, self.pos)

        self.age = 0 #age in ticks
        self.last_reproduction = 0 #number of ticks since last reproduction
        self.health = self.genome.health.value #current health (starts at max)
        
        self.energy = self.genome.energy.value #current energy (starts at max)

        self.damaged = 0 #number of ticks since last injured

    def make_brain(self):
        self.brain = Brain(self.genome.vision_resolution.value, self.genome.speed.value)
        self.brain.randomise()

    def get_vision_array(self) -> list:
        vision_array = [[(0, 0, 0, 0), 0] for _ in range(int(self.genome.vision_resolution.value))]
        for i in range(int(self.genome.vision_resolution.value)):
            angle = self.angle + self.genome.vision_span.value / self.genome.vision_resolution.value * i
            for pixel in range(int(max(self.genome.size.value)), int(max(self.genome.size.value)+int(self.genome.vision_range.value))): #max(self.genome.size.value) to avoid seeing self
                coords = (int(self.pos[0]+math.cos(angle)*pixel), int(self.pos[1]+math.sin(angle)*pixel))
                if coords[0] < 0: break       #left
                if coords[0] >= WIDTH: break   #right
                if coords[1] < 0: break       #top
                if coords[1] >= HEIGHT: break  #bottom
                color = screen.get_at(coords)
                if color[:3] != (0, 0, 0):
                    for j in range(4):
                        if color[j]<self.genome.vision_color.value[0][j]: color[j] = 0
                        elif color[j]>self.genome.vision_color.value[1][j]: color[j] = 255
                    vision_array[i] = [color, pixel] #adds the color and distance        return vision_array
                
    
    def can_mate(self) -> bool:
        if self.energy < self.genome.energy.value/100:
            return False
        if self.age < (self.genome.size.value[0]*self.genome.size.value[1]/10)**2:
            return False
        if self.last_reproduction < (self.genome.size.value[0]*self.genome.size.value[1]/20)**1.5*random.triangular(0.6, 1.4, 1):
            return False
        return True

    def rotate(self, angle):
        self.angle = (self.angle+angle)%360
        if self.angle:
            pass

    def move(self, distance):
        if self.energy > distance*0.1: #every 10 pixels moved reduces enrgy by 1
            self.energy -= distance * 0.1
        else:
            distance /= 5
            self.energy /= 2
        delta_x = math.sin(self.angle)*distance
        delta_y = math.sqrt(distance**2 - delta_x**2)
        if self.angle>90 and self.angle<270:
            delta_x = -delta_x
        if self.angle>180 and self.angle<360:
            delta_y = -delta_y

        self.pos[0] += delta_x
        self.pos[1] += delta_y
        #boundary conditions
        if self.pos[0] < self.genome.size.value[0]:          self.pos[0] = self.genome.size.value[0]+5           #left
        if self.pos[0] > WIDTH - self.genome.size.value[0]:  self.pos[0] = WIDTH - self.genome.size.value[0]-5   #right
        if self.pos[1] < self.genome.size.value[1]:          self.pos[1] = self.genome.size.value[1]+5           #top
        if self.pos[1] > HEIGHT - self.genome.size.value[1]: self.pos[1] = HEIGHT - self.genome.size.value[1]-5  #bottom

        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

    def eat(self, value: float):
        self.energy += value #add amount of energy
        if self.energy > self.genome.energy.value: self.energy = self.genome.energy.value #if over max energy then set to cap
        
    def update(self):
        screen.blit(self.image, self.pos)
        self.age += 1
        self.damaged += 1
        self.last_reproduction += 1
        if self.health <= 0  or self.energy <= 0:
            self.kill()
        
    def main(self):
        self.rotate(random.randint(0, 360))
        self.move(random.uniform(-self.genome.speed.value, self.genome.speed.value))
        if self.health != self.genome.health.value and self.damaged>math.sqrt(self.genome.size.value[0]*self.genome.size.value[1]/15): #if not on full health and not damaged in the last x ticks
            if self.health+self.energy*ENERGY_HEALTH_GAIN*MAX_HEALTH_GAIN > self.genome.health.value: #if have enough energy to restore fully
                self.energy -= self.energy*((self.genome.health.value-self.health)/self.genome.health.value)*ENERGY_HEALTH_GAIN
                self.health = self.genome.health.value
            else:
                self.health += self.energy*ENERGY_HEALTH_GAIN*MAX_HEALTH_GAIN
                self.energy -= (self.energy*MAX_HEALTH_GAIN)*ENERGY_HEALTH_GAIN
       
       

class Plant(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = [random.randrange(3, 10), random.randrange(3, 10)]
        self.image = pygame.Surface(self.size)
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
        screen.blit(self.image, self.pos)
        self.eaten = False

    def update(self):
        if self.eaten:
            self.kill()
        screen.blit(self.image, self.pos)




class Simulation:
    def __init__(self):
        self.BG = (0, 0, 0)
        self.NUM_TICKS = 0
        self.SPECIES_CAP = 400
        self.SPEED = 100
       
        self.all_container = pygame.sprite.Group()
        self.plants_container = pygame.sprite.Group()
        self.n_species = 3
        self.species_containers = [None for _ in range(self.n_species)]
    
    def start(self):
        pygame.init()
        pygame.display.set_icon(pygame.image.load("assets\\icon.png"))
        pygame.display.set_caption("Ben's evolution simulator")
        global screen
        screen = pygame.display.set_mode([WIDTH, HEIGHT])
        start = int(time.time())
        os.mkdir(f"{os.getcwd()}\\brains\\backup\\{start}") #backup brains dir

        for species in range(self.n_species):
            self.species_containers[species] = pygame.sprite.Group()
            print(f"creating species {species}...")
            try:
                brains = os.listdir(f"{os.getcwd()}\\brains\\species_{species}")
            except:
                os.mkdir(f"{os.getcwd()}\\brains\\species_{species}")
                brains = []
            print(f"\t{len(brains)} brains available")
            if os.path.exists(f"species_{species}_initial.txt"):
                data = eval(open(f"species_{species}_initial.txt").read())
            else:
                data = [30, [5, 5], [255, 0, 0], 2.5, 50, 2000, 5, 50, 90, 90, [(0, 0, 0, 0), (0, 0, 0, 0)], True, False]
            n_create = int(CREATURE_DENSITY/self.n_species/(data[1][0]*data[1][1]*4)*WIDTH*HEIGHT)
            print(f"creating {n_create} of species {species}")
            for _ in range(n_create ):
                creature = Creature(random.randint(0, WIDTH), random.randint(0, HEIGHT),Genome(speed=data[0], size=data[1], color=data[2], damage=data[3], health=data[4], energy=data[5], reproduction_num=data[6], vision_range=data[7], vision_span=data[8], vision_resolution=data[9], vision_color=data[10], eats_meat=data[11], eats_plant=[12]))
                if brains:
                    with open(f"{os.getcwd()}\\brains\\species_{species}\\{random.choice(brains)}", "rb") as file:
                        try:
                            creature.brain = pickle.load(file)
                            creature.genome = pickle.load(file)
                        except:
                            pass
                else:
                    creature.make_brain()
                self.species_containers[species].add(creature)
                self.all_container.add(creature)
            os.rename(f"{os.getcwd()}\\brains\\species_{species}", f"{os.getcwd()}\\brains\\backup\\{start}\\species_{species}")
            os.mkdir(f"{os.getcwd()}\\brains\\species_{species}")
        
        print(f"creating {int(WIDTH*HEIGHT*(PLANT_DENSITY/25))} plants...")
        for _ in range(int(WIDTH*HEIGHT*(PLANT_DENSITY/25))): #creates 0.2 density of plants   /25 because avg size is 25
                plant = Plant()
                self.plants_container.add(plant)
                self.all_container.add(plant)
                
        print("all sprites created")

        #first tick
        screen.fill(self.BG)
        self.all_container.update()
        self.all_container.draw(screen)
        pygame.display.flip()
        
        clock = pygame.time.Clock()
        tick = 1
        time_since_last_event = 0


        ##############
        #  main loop #
        ##############
        while (tick<self.NUM_TICKS or self.NUM_TICKS==0) and time_since_last_event<1000:
            if DEBUG or tick%50==0: print(f"\n\n############\ntick {tick}\n############\n\n") #prints tick
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 0
            for sprite in self.all_container.sprites(): #loops through all creatures and processes them
                if type(sprite)==Creature: #if it is a creature, not plant
                    sprite.main()
                    if sprite.age > 500: #if sprite brain "golden" save it
                        for species in range(self.n_species):
                            if self.species_containers[species] in sprite.groups():
                                if not os.path.isfile(f"{os.getcwd()}/brains/species_{species}/{sprite.ID}.brain"):
                                    print(f"dumping {sprite.ID}'s brain (group {species})")
                                    with open(f"{os.getcwd()}/brains/species_{species}/{sprite.ID}.brain", "wb") as file:
                                        pickle.dump(sprite.brain, file)
                                        pickle.dump(sprite.genome, file)
                    sprite.last_reproduction += 1
                collisions = pygame.sprite.spritecollide(sprite, self.all_container, False)
                if len(collisions)>1:
                    for i in range(len(collisions)-1):
                        for j in range(i+1, len(collisions)):
                            if len(collisions[i].groups())==2 and len(collisions[j].groups())==2: #error check incase not in 2 groups
                                if collisions[i].groups()==collisions[j].groups() and self.plants_container not in collisions[i].groups(): #if same-species collision
                                    if collisions[i].can_mate() and collisions[j].can_mate() and collisions[i]!=collisions[j]: #if not plants and they can all mate and not same creature
                                        num_produced = (collisions[i].genome.reproduction_num.value+collisions[i].genome.reproduction_num.value)/2 #number of offspring to make
                                        for _ in range(int(random.triangular(1, num_produced, int(num_produced/2)))): #loops creating offspring
                                            creature = Creature(collisions[i].pos[0], collisions[i].pos[1], collisions[i].genome+collisions[j].genome)
                                            creature.brain = Brain.combine(collisions[i].brain, collisions[j].brain, creature.genome.vision_resolution.value, creature.genome.speed.value)
                                            collisions[i].groups()[1].add(creature)
                                        collisions[i].last_reproduction = 0
                                        collisions[j].last_reproduction = 0
                                        collisions[i].energy -= collisions[i].genome.energy.value/100
                                        collisions[j].energy -= collisions[j].genome.energy.value/100
                                else: #if different-species collision
                                    if type(collisions[i])!=Plant or type(collisions[j])!=Plant: print(type(collisions[i]), type(collisions[j]))
                                    if type(collisions[i])==Plant and type(collisions[j])!=Plant: #plant collision
                                        print("plant collision")
                                        if collisions[j].genome.eats_plant:
                                            collisions[j].eat(collisions[i].size[0]*collisions[i].size[1]*ENERGY_DENSITY)
                                            collisions[i].eaten = True
                                            print("plant eaten")
                                    elif type(collisions[j])==Plant and type(collisions[i])!=Plant: #plant collision
                                        print("plant collision")
                                        if collisions[i].genome.eats_plant:
                                            collisions[i].eat(collisions[j].size[0]*collisions[j].size[1]*ENERGY_DENSITY)
                                            collisions[j].eaten = True
                                            print("plant eaten")
                                    elif type(collisions[i])==Creature and type(collisions[j])==Creature:
                                        print("non-plant collision")
                                        time_since_last_event = 0
                                        collisions[i].health -= collisions[j].genome.size.value[0]*collisions[j].genome.size.value[1]*collisions[j].genome.damage.value
                                        collisions[i].damaged = 0
                                        collisions[j].health -= collisions[i].genome.size.value[0]*collisions[i].genome.size.value[1]*collisions[i].genome.damage.value
                                        collisions[j].damaged = 0
                                        if collisions[i].health <= 0 and collisions[j].health > 0: #if creature[i] dead and creature[j] not
                                            if collisions[j].genome.eats_meat:
                                                collisions[j].eat(collisions[i].genome.size.value[0]*collisions[i].genome.size.value[1]*ENERGY_DENSITY)
                                        elif collisions[j].health <= 0 and collisions[i].health > 0: #if creature[j] dead and creature[i] not
                                            if collisions[i].genome.eats_meat:
                                                collisions[i].eat(collisions[j].genome.size.value[0]*collisions[j].genome.size.value[1]*ENERGY_DENSITY)


        
            screen.fill(self.BG)
            self.all_container.update()
            pygame.display.flip()
            tick+=1
            time_since_last_event+=1
            for _ in range(int(WIDTH*HEIGHT*(PLANT_DENSITY/25)/40)): #creates 0.2 density of plants   *25 because avg size is 25
                plant = Plant()
                self.plants_container.add(plant)
                self.all_container.add(plant)

            clock.tick(30*self.SPEED)





   
if __name__ == "__main__":
    i = 1
    try:
        while True:
            print(f"\n\n###############\n###############\n  iteration {i}\n###############\n###############\n\n\n")
            simulation = Simulation()
            simulation.start()
            i+=1
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)
