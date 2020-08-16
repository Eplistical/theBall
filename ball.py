import math
from enum import Enum

class Charactor(Enum):
    HERO        = 1
    ENEMY       = 2
    SPECIAL     = 3


class Ball:
    def __init__(self, position, radius, velocity, charactor):
        self.position = position
        self.radius = radius
        self.velocity = velocity
        self.charactor = charactor

        self.moveUpDown = 0
        self.moveLeftRight = 0

        self.active = True
    
    def __str__(self):
        return f'''Ball( position={self.position}, radius={self.radius}, velocity={self.velocity}, charactor=${self.charactor} )'''

    def distance(self, other):
        r2 = 0.0
        for xi, xj in zip(self.position, other.position):
            r2 += (xi - xj)**2
        return math.sqrt(r2)
    
    def collide(self, other):
        return self.distance(other) < (self.radius + other.radius)
    
    def apply(self, other):
        pass