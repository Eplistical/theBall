import math
from enum import Enum

class Charactor(Enum):
    HERO                    = 1
    ENEMY                   = 2
    SPECIAL_SPEED_UP        = 3
    SPECIAL_SPEED_DOWN      = 4
    SPECIAL_SMALLER         = 5
    SPECIAL_BIGGER          = 6
    SPECIAL_GODLIKE         = 7
    SPECIAL_FROZEN          = 8
    SPECIAL_RANDOM          = 9


SPECIAL_CHARACTORS = (
    Charactor.SPECIAL_SPEED_UP,
    Charactor.SPECIAL_SPEED_DOWN,
    Charactor.SPECIAL_SMALLER,
    Charactor.SPECIAL_BIGGER,
    Charactor.SPECIAL_FROZEN,
    Charactor.SPECIAL_GODLIKE,
)


class Ball:
    def __init__(self, position, radius, velocity, charactor):
        self.position = position
        self.radius = radius
        self.velocity = velocity
        self.charactor = charactor

        self.moveUpDown = 0
        self.moveLeftRight = 0

        self.status = None
        self.statusBeginTick = None

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