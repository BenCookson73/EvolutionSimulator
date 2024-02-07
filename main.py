import pygame
import sys, math, random

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,

)

WIDTH = 1200
HEIGHT = 700

class Creature(pygame.sprite.Sprite):
    def __init__(self, x, y):
        """"""
        super().__init__() 
        self.alleles = { #do not use tuples because everything must be mutable
            "speed": 10, #pixels it can travel in 1 frame
            "size": [10, 10], #width and height of object
            "color": [0, 255, 0],
            #"": ,
        }
        self.image = pygame.Surface(self.alleles["size"])
        self.image.fill(self.alleles["color"])
        self.rect = self.image.get_rect()
        
        self.pos = [x, y]
        self.angle = 0

    def rotate(self, angle):
        self.angle += angle

    def move(self, distance):
        delta_x = math.sin(self.angle)*distance
        delta_y = math.sqrt(distance**2 - delta_x**2)
        if self.angle>90 and self.angle<270:
            delta_x = -delta_x
        if self.angle>180 and self.angle<360:
            delta_y = -delta_y

        self.pos[0] += delta_x
        self.pos[1] += delta_y
        #boundary conditions
        if self.pos[0]<self.alleles["size"][0]: self.pos[0] = self.alleles["size"][0]
        if self.pos[0]>WIDTH-self.alleles["size"][0]: self.pos[0] = WIDTH-self.alleles["size"][0]
        if self.pos[1]<self.alleles["size"][1]: self.pos[1] = self.alleles["size"][1]
        if self.pos[1]>HEIGHT-self.alleles["size"][1]: self.pos[1] = HEIGHT-self.alleles["size"][1]

        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
            
    def update(self):
        self.rotate(2)
        self.move(random.uniform(0, self.alleles["speed"]))
        
        
        
        

class Simulation:
    def __init__(self):
        self.BG = (0, 0, 0)
        self.NUM_TICKS = 0
        self.n_species_1 = 1
        self.SPEED = 1
        
        self.all_container = pygame.sprite.Group()
        self.species_1_container = pygame.sprite.Group()

    def start(self):
        pygame.init()
        pygame.display.set_icon(pygame.image.load("assets/icon.png"))
        pygame.display.set_caption("Ben's evolution simulator")
    
        screen = pygame.display.set_mode([WIDTH, HEIGHT])
        for _ in range(self.n_species_1):
            creature = Creature(random.randint(0, WIDTH), random.randint(0, HEIGHT))
            self.species_1_container.add(creature)
            self.all_container.add(creature)

        clock = pygame.time.Clock()
        tick = 0
        while tick<self.NUM_TICKS or self.NUM_TICKS==0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 0
            screen.fill(self.BG)
            self.all_container.update()
            self.all_container.draw(screen)
            pygame.display.flip()
            tick+=1
            #__import__("time").sleep(1)
            clock.tick(30/self.SPEED)





    
if __name__ == "__main__":
    simulation = Simulation()
    simulation.start()
    pygame.quit()
    sys.exit(0)
