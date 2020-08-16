# pylint: disable=maybe-no-member

import pygame
from pygame.locals import *
import colors
from ball import Ball, Charactor
import math


class App:
    def __init__(self):
        # configurations 
        self._running = True
        self._clockTickNumber = 20
        self._screenWidth = 960
        self._screenHeight = 540
        self._screenSize = (self._screenWidth, self._screenHeight)
        self._displayMode = pygame.HWSURFACE | pygame.DOUBLEBUF

        self._initialRadius = 20
        self._initialVelocity = 5

        # debug
        self.bb = 0
    
    def on_init(self):
        # initialization
        pygame.init()
        self.screen = pygame.display.set_mode(self._screenSize, self._displayMode)
        self.screen.fill(colors.BGCOLOR)
        self.clock = pygame.time.Clock()
        self.heroBall = Ball(
                [self._screenWidth / 2, self._screenHeight / 2], 
                self._initialRadius,
                self._initialVelocity,
                Charactor.HERO)
        self.otherBalls = set()
        self.otherBalls.add(self.generate_ball(Charactor.ENEMY))
        return True
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            pressedKeys = pygame.key.get_pressed()
            self.heroBall.moveUpDown = 0
            self.heroBall.moveLeftRight = 0
            if pressedKeys[K_UP]:
                self.heroBall.moveUpDown -= 1
            if pressedKeys[K_DOWN]:
                self.heroBall.moveUpDown += 1
            if pressedKeys[K_LEFT]:
                self.heroBall.moveLeftRight -= 1
            if pressedKeys[K_RIGHT]:
                self.heroBall.moveLeftRight += 1
        
    def on_loop(self):
        # move the heroBall
        if self.heroBall.moveLeftRight == 0 and self.heroBall.moveUpDown == 0:
            velocity = 0
        elif self.heroBall.moveLeftRight != 0 and self.heroBall.moveUpDown != 0:
            velocity = self.heroBall.velocity / math.sqrt(2.0)
        else:
            velocity = self.heroBall.velocity
        if velocity > 0.0:
            self.heroBall.position[0] += self.heroBall.moveLeftRight * velocity
            self.heroBall.position[1] += self.heroBall.moveUpDown * velocity

        # move/delete other balls
        toRemove = set()
        for ball in self.otherBalls:
            ball.position[0] += ball.velocity[0]
            ball.position[1] += ball.velocity[1]

            # remove useless ball
            if (ball.position[0] + ball.radius < 0 or 
                ball.position[0] - ball.radius > self._screenWidth or 
                ball.position[1] + ball.radius < 0 or 
                ball.position[1] - ball.radius > self._screenHeight):
                toRemove.add(ball)
        if len(toRemove) > 0:
            self.otherBalls -= toRemove
        
        # check collision
        for ball in self.otherBalls:
            if self.heroBall.collide(ball):
                print('collide!')

    def on_render(self):
        # background
        self.screen.fill(colors.BGCOLOR)
        # draw balls
        self.draw_ball(self.heroBall)
        for ball in self.otherBalls:
            self.draw_ball(ball)
        # update display
        pygame.display.update()

    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if not self.on_init():
            self._running = False
 
        while(self._running):
            self.clock.tick(self._clockTickNumber)
            for event in pygame.event.get():
                self.on_event(event)

            self.on_loop()
            self.on_render()
        self.on_cleanup()
    
    def draw_ball(self, ball):
        if ball.charactor == Charactor.HERO:
            color = colors.HERO_COLOR
        elif ball.charactor == Charactor.ENEMY:
            color = colors.ENEMY_COLOR
        pygame.draw.circle(self.screen, color, [int(x) for x in ball.position], int(ball.radius))
    
    def generate_ball(self, charactor):
        position = [0, 0]
        radius = 12
        velocity = [3, 3]
        return Ball(position, radius, velocity, charactor)


if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()