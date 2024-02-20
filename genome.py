from dataclasses import dataclass
import random

class Allele:
    def __init__(self, value, mutation_value=0.05, mutable=False):
        self.value = value #value (any value)
        self.mutation_value = mutation_value #chance that it mutates (0~1)
        if type(self.value)==bool:
            self.dominant=dominant
        if type(self.value)==int:
            self.value=float(self.value)
        if type(self.value)==tuple:
            self.value=list(self.value)
        self.mutable = mutable

    def update(self, value):
        if self.mutable==False:
            return -1
        self.value=value

    def combine_allele(float1: float, float2: float, mut1: float, mut2: float) -> float:
        min_percent = 0.95 * (1 - mut1 + 1 - mut2) / 2
        max_percent = 1.05 * (1 - mut1 + 1 - mut2) / 2
        if float1 < float2:
            min_val = min_percent * float1
            max_val = max_percent * float2
        else:
            min_val = min_percent * float2
            max_val = max_percent * float1
        mode = random.uniform(min_percent, max_percent) * (float1 + float2) / 2
        value = random.triangular(min_val, max_val, mode)
        if (mut1 + mut2) / 2 > random.random():
            value = random.triangular((float1 + float2) / 2 * 0.3, (float1 + float2) / 2 * 1.1, (float1 + float2) / 2 * 0.95)
        return value
        
    def __mul__(allele1, allele2):
        if type(allele1.value) != type(allele2.value):
            return -1
        elif type(allele1.value) == bool:
            value = allele1.value or allele2.value
            if (mut1 + mut2) / 2 > random.random():
                value = not value
        elif type(allele1.value) == float:
            value = Allele.combine_allele(allele1.value, allele2.value, allele1.mutation_value, allele2.mutation_value)
        else:
            value = list()
            for al1, al2 in zip(allele1.value, allele2.value):
                if type(al1)==list or type(al2)==list:
                    val = list()
                    for all1, all2 in zip(al1, al2):
                        val.append(Allele.combine_allele(all1, all2, allele1.mutation_value, allele2.mutation_value))
                    value.append(val)
                else: value.append(Allele.combine_allele(al1, al2, allele1.mutation_value, allele2.mutation_value))
            value = type(allele1.value)(value)
    
        mutation_value = random.triangular(allele1.mutation_value,
                                           allele2.mutation_value,
                                           random.uniform(allele1.mutation_value,
                                                          allele2.mutation_value
                                            )
        )
        return Allele(value, mutation_value=mutation_value, mutable=allele1.mutable or allele2.mutable)
     
class Genome:
    def __init__(self,
                 speed=10,
                 size=(1, 1),
                 color=(0, 0, 0, 0),
                 damage=10,
                 health=100,
                 energy=1000,
                 reproduction_num=1,
                 vision_range=10,
                 vision_span=90,
                 vision_resolution=10,
                 vision_color=[(0, 0, 0, 0), (255, 255, 255, 255)],
                 eats_meat = True,
                 eats_plant = True,
                 ):
        #do not use tuples because everything must be mutable
        self.speed = Allele(speed, mutable=True) #pixels it can travel in 1 frame
        self.size = Allele(size, mutable=True) #width and height of object
        self.color = Allele(color, mutation_value=0.1) #color of animal
        self.damage = Allele(damage, mutable=True) #damage dealt per pixel^2 of host size
        self.health = Allele(health, mutable=True) #maximum health
        self.energy = Allele(energy) #maximum energy
        self.reproduction_num = Allele(reproduction_num) #number of babies that can be produced per litter  
        self.vision_range = Allele(vision_range) #how far can see
        self.vision_span = Allele(vision_span) #degree of vision
        self.vision_resolution = Allele(vision_resolution) #number of rays to find color
        self.vision_color = Allele(vision_color) #color range that can be seen
        self.eats_meat = eats_meat #if it can eat meat
        self.eats_plant = eats_plant #if it can eat meat
        for i in range(len(self.color.value)):
            if self.color.value[i]<0: self.color.value[i]=0
            if self.color.value[i]>255: self.color.value[i]=255
            

    def __add__(genome1, genome2):
        g = Genome()
        g.speed = genome1.speed * genome2.speed
        g.size = genome1.size * genome2.size
        g.color = genome1.color * genome2.color
        g.damage = genome1.damage * genome2.damage
        g.health = genome1.health * genome2.health
        g.eats_meat = genome1.eats_meat or genome1.eats_meat
        g.eats_plant = genome1.eats_plant or genome1.eats_plant
        for i in range(len(g.color.value)):
            if g.color.value[i]<0: g.color.value[i]=0
            if g.color.value[i]>255: g.color.value[i]=255
        return g

    def __str__(self):
        return '\n'.join([f"{attr}: {vars(self)[attr].value}" for attr in vars(self) if type(vars(self)[attr])==Allele])+"\n\n\n"
