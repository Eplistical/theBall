# pylint: disable=maybe-no-member

import random
import pygame
from pygame.locals import *
import colors
import math
import os
import sys
from pathlib import Path
from enum import Enum
from ball import Ball, Charactor, SPECIAL_CHARACTORS
from panel import Panel
from pygame.time import set_timer

class LocationToPlayGround(Enum):
    INSIDE          = 1
    CROSSING        = 2
    OUTSIDE         = 3
    LEFT_OUTSIDE    = 4
    RIGHT_OUTSIDE   = 5
    TOP_OUTSIDE      = 6
    BOTTOM_OUTSIDE    = 7


class App:
    def __init__(self):
        # basic 
        self._running                           = True
        self._clockTickNumber                   = 24
        self._appDir                            = Path(os.path.dirname(os.path.realpath(__file__)))
        self._recordFileName                    = 'record.dat'

        # screen 
        self._screenWidth                       = 1280
        self._screenHeight                      = 720
        self._screenSize                        = (self._screenWidth, self._screenHeight)
        self._displayMode                       = pygame.HWSURFACE | pygame.DOUBLEBUF

        # playground
        self._playGroundWidthRatio              = (0.0, 0.8)
        self._playGroundHeightRatio             = (0.0, 1.0)
        self._playGroundPanel = Panel(  self._playGroundWidthRatio[0] * self._screenWidth, 
                                        self._playGroundHeightRatio[0] * self._screenHeight,
                                        (self._playGroundWidthRatio[1] - self._playGroundWidthRatio[0]) * self._screenWidth,
                                        (self._playGroundHeightRatio[1] - self._playGroundHeightRatio[0]) * self._screenHeight)

        # scoreboard
        self._scoreBoardWidthRatio              = (0.8, 1.0)
        self._scoreBoardHeightRatio             = (0.0, 1.0)
        self._scoreBoardPanel = Panel(  self._scoreBoardWidthRatio[0] * self._screenWidth, 
                                        self._scoreBoardHeightRatio[0] * self._screenHeight,
                                        (self._scoreBoardWidthRatio[1] - self._scoreBoardWidthRatio[0]) * self._screenWidth,
                                        (self._scoreBoardHeightRatio[1] - self._scoreBoardHeightRatio[0]) * self._screenHeight)

        # images
        self._statusImgWidthRatio               = 0.06
        self._statusImgHeightRatio              = 0.06
        self._statusImgSize                     = (int(self._statusImgWidthRatio * self._screenWidth), int(self._statusImgHeightRatio * self._screenHeight))

        # heroBall
        self._initialHeroRadius                 = 16
        self._initialHeroVelocity               = 8
        self._heroBallVelocityRange             = (2, 24)
        self._heroBallRadiusRange               = (5, 32)

        # other balls
        self._genBallInterval                   = 1000 # ms
        self._genBallStdDev                     = 0.1 # in normal dist
        self._initialVelocityMagnitudeRange     = (4, 8)
        self._initialThetaRange                 = (-15/90*math.pi, 15/90*math.pi)
        self._initialRadiusRange                = (5, 10)

        self._genBallCharactorProb              = { 
            Charactor.ENEMY                 : 0.67,
            Charactor.SPECIAL_SPEED_UP      : 0.06,
            Charactor.SPECIAL_SPEED_DOWN    : 0.06,
            Charactor.SPECIAL_SMALLER       : 0.06,
            Charactor.SPECIAL_BIGGER        : 0.06,
            Charactor.SPECIAL_GODLIKE       : 0.03,
            Charactor.SPECIAL_FROZEN        : 0.03,
            Charactor.SPECIAL_RANDOM        : 0.03,
        }
        self._toAddQueue                        = list()
        self._toAddBatchSize                    = 20
        self._statusGodlikePeriod               = 4000 # ms
        self._statusFrozenPeriod                = 2000 # ms

        # events
        self._GEN_BALL_EVENT                    = pygame.USEREVENT + 1
        self._SPECIAL_GODLIKE_EXPIRE            = pygame.USEREVENT + 2
        self._SPECIAL_FROZEN_EXPIRE             = pygame.USEREVENT + 3

        # level up
        self._levelUpTimeInterval               = 15000 # ms
        self._levelUpGenBallIntervalRatio       = 0.8
        self._levelUpVelocityRatio              = 1.08
        self._levelUpRadiusRatio                = 1.08

        # score
        self._collideScoreCoef                  = { 
            Charactor.ENEMY                 : 4,
            Charactor.SPECIAL_BIGGER        : 4,
            Charactor.SPECIAL_SMALLER       : 2,
            Charactor.SPECIAL_SPEED_DOWN    : 4,
            Charactor.SPECIAL_SPEED_UP      : 2,
            Charactor.SPECIAL_GODLIKE       : 8,
            Charactor.SPECIAL_FROZEN        : 32,
        }



    def on_init(self):
        # initialization
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode(self._screenSize, self._displayMode)
        self.screen.fill(colors.BGCOLOR)
        self.clock = pygame.time.Clock()
        self.gameLevel = 1
        self.heroBall = Ball(
                self._playGroundPanel.get_coord_by_percent(0.5, 0.5),
                self._initialHeroRadius,
                self._initialHeroVelocity,
                Charactor.HERO)
        self.otherBalls = set()
        set_timer(self._GEN_BALL_EVENT, int(self._genBallInterval * max(0.0, random.gauss(1.0, self._genBallStdDev))))
        self.score = 0.0
        # images
        self.imgs = {
            'statusGodlike' : pygame.transform.scale(pygame.image.load('img/SPECIAL_GODLIKE.png'), self._statusImgSize),
            'statusFrozen' : pygame.transform.scale(pygame.image.load('img/SPECIAL_FROZEN.png'), self._statusImgSize),
        }
        # record
        try:
            with open(self._appDir / self._recordFileName, 'r') as recf:
                self.levelRecord = int(next(recf))
                self.scoreRecord = float(next(recf))
        except FileNotFoundError:
            self.levelRecord = 1
            self.scoreRecord = 0.0
            

        return True
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            # resolve keyboard control
            pressedKeys = pygame.key.get_pressed()
            self.heroBall.moveUpDown = 0
            self.heroBall.moveLeftRight = 0
            if pressedKeys[K_UP] or pressedKeys[K_w]:
                self.heroBall.moveUpDown -= 1
            if pressedKeys[K_DOWN] or pressedKeys[K_s]:
                self.heroBall.moveUpDown += 1
            if pressedKeys[K_LEFT] or pressedKeys[K_a]:
                self.heroBall.moveLeftRight -= 1
            if pressedKeys[K_RIGHT] or pressedKeys[K_d]:
                self.heroBall.moveLeftRight += 1
        elif event.type == self._GEN_BALL_EVENT:
            if len(self._toAddQueue) == 0:
                self._toAddQueue = random.choices(list(self._genBallCharactorProb.keys()), weights=list(self._genBallCharactorProb.values()), k=self._toAddBatchSize)
            self.otherBalls.add(self.generate_ball(self._toAddQueue[-1]))
            self._toAddQueue.pop()
            set_timer(self._GEN_BALL_EVENT, int(self._genBallInterval * max(0.0, random.gauss(1.0, self._genBallStdDev))))
        elif event.type == self._SPECIAL_GODLIKE_EXPIRE:
            if self.heroBall.status == Charactor.SPECIAL_GODLIKE and (pygame.time.get_ticks() - self.heroBall.statusBeginTick) >= self._statusGodlikePeriod - 10:
                self.heroBall.status = None
                self.heroBall.statusBeginTick = None
        elif event.type == self._SPECIAL_FROZEN_EXPIRE:
            if self.heroBall.status == Charactor.SPECIAL_FROZEN and (pygame.time.get_ticks() - self.heroBall.statusBeginTick) >= self._statusFrozenPeriod - 10:
                self.heroBall.status = None
                self.heroBall.statusBeginTick = None
        
    def on_loop(self):
        # update the heroBall
        if self.heroBall.event is not None:
            self.heroBall.event = None

        if self.heroBall.status != Charactor.SPECIAL_FROZEN:
            if self.heroBall.moveLeftRight == 0 and self.heroBall.moveUpDown == 0:
                velocity = 0
            elif self.heroBall.moveLeftRight != 0 and self.heroBall.moveUpDown != 0:
                velocity = self.heroBall.velocity / math.sqrt(2.0)
            else:
                velocity = self.heroBall.velocity
            if velocity > 0.0:
                self.heroBall.position[0] += self.heroBall.moveLeftRight * velocity
                self.heroBall.position[1] += self.heroBall.moveUpDown * velocity
                self.heroBall.position[0] = max(self._playGroundPanel.left + self.heroBall.radius, min(self._playGroundPanel.right - self.heroBall.radius, self.heroBall.position[0]))
                self.heroBall.position[1] = max(self._playGroundPanel.top + self.heroBall.radius, min(self._playGroundPanel.bottom - self.heroBall.radius, self.heroBall.position[1]))

        # update/delete other balls
        toRemove = set()
        toRemoveCollide = set()
        for ball in self.otherBalls:
            ball.position[0] += ball.velocity[0]
            ball.position[1] += ball.velocity[1]
            # out of boundary
            if (ball.position[0] + ball.radius < self._playGroundPanel.left and ball.velocity[0] < 0.0):
                toRemove.add(ball)
            elif (ball.position[0] - ball.radius > self._playGroundPanel.right and ball.velocity[0] > 0.0):
                toRemove.add(ball)
            elif (ball.position[1] + ball.radius < self._playGroundPanel.top and ball.velocity[1] < 0.0):
                toRemove.add(ball)
            elif (ball.position[1] - ball.radius > self._playGroundPanel.bottom and ball.velocity[1] > 0.0):
                toRemove.add(ball)
            # collision
            if self.heroBall.collide(ball):
                self.collid_handler(ball)
                toRemoveCollide.add(ball)
        # remove balls
        if len(toRemove) > 0:
            self.otherBalls -= toRemove
            self.scoreUp(toRemove, collide=False)

        if len(toRemoveCollide) > 0:
            self.otherBalls -= toRemoveCollide
            self.scoreUp(toRemoveCollide, collide=True)

        # level up 
        if pygame.time.get_ticks() // self._levelUpTimeInterval > self.gameLevel:
            self.levelUp()
        

    def on_render(self):
        # background
        self.screen.fill(colors.BGCOLOR)
        # playground panel
        self.render_playground()
        # scoreboard panel
        self.render_scoreboard()
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
        
        self.render_gameOver()
        self.on_cleanup()
    
    def generate_ball(self, charactor):
        # choose side
        initailLocationList = (LocationToPlayGround.LEFT_OUTSIDE, LocationToPlayGround.RIGHT_OUTSIDE, LocationToPlayGround.TOP_OUTSIDE, LocationToPlayGround.BOTTOM_OUTSIDE)
        side = random.choice(initailLocationList)
        # choose velocity
        velocityMagnitude = random.uniform(self._initialVelocityMagnitudeRange[0], self._initialVelocityMagnitudeRange[1])
        theta = random.uniform(self._initialThetaRange[0], self._initialThetaRange[1])
        velocity = [velocityMagnitude * math.cos(theta), velocityMagnitude * math.sin(theta)]
        # choose relative position
        positionPercent = random.uniform(0.0, 1.0)
        # choose radius
        radius = random.uniform(self._initialRadiusRange[0], self._initialRadiusRange[1])
        # construct ball
        if side == LocationToPlayGround.LEFT_OUTSIDE:
            position = [self._playGroundPanel.left - radius, self._playGroundPanel.top + self._playGroundPanel.height * positionPercent]
            velocity = [velocity[0], velocity[1]]
        elif side == LocationToPlayGround.RIGHT_OUTSIDE:
            position = [self._playGroundPanel.right + radius, self._playGroundPanel.top + self._playGroundPanel.height * positionPercent]
            velocity = [-velocity[0], velocity[1]]
        elif side == LocationToPlayGround.TOP_OUTSIDE:
            position = [self._playGroundPanel.left + self._playGroundPanel.width * positionPercent, self._playGroundPanel.top - radius]
            velocity = [velocity[1], velocity[0]]
        elif side == LocationToPlayGround.BOTTOM_OUTSIDE:
            position = [self._playGroundPanel.left + self._playGroundPanel.width * positionPercent, self._playGroundPanel.bottom + radius]
            velocity = [velocity[1], -velocity[0]]
        return Ball(position, radius, velocity, charactor)
    
    def get_ball_relative_location(self, ball):
        leftMost = ball.position[0] - ball.radius
        rightMost = ball.position[0] + ball.radius
        upMost = ball.position[1] - ball.radius
        downMost = ball.position[1] + ball.radius
        if leftMost >= 0.0 and rightMost <= self._playGroundWidth and upMost >= 0.0 and downMost <= self._playGroundHeight:
            return LocationToPlayGround.INSIDE, None
        elif rightMost < 0.0 or leftMost > self._playGroundWidth or downMost < 0.0 or upMost > self._playGroundHeight:
            details = set()
            if rightMost < 0.0:
                details.add(LocationToPlayGround.LEFT_OUTSIDE)
            if leftMost > self._playGroundWidth:
                details.add(LocationToPlayGround.RIGHT_OUTSIDE)
            if downMost < 0.0:
                details.add(LocationToPlayGround.TOP_OUTSIDE)
            if upMost > self._playGroundHeight:
                details.add(LocationToPlayGround.BOTTOM_OUTSIDE)
            return LocationToPlayGround.OUTSIDE, details
        else:
            return LocationToPlayGround.CROSSING, None
    
    def render_playground(self):
        pygame.draw.rect(self.screen, colors.PLAYGROUND_BGCOLOR, self._playGroundPanel.to_rect())
        # draw balls
        self.draw_ball(self.heroBall)
        for ball in self.otherBalls:
            self.draw_ball(ball)

    def render_scoreboard(self):
        # draw scoreboard
        pygame.draw.rect(self.screen, colors.SCOREBOARD_BGCOLOR, self._scoreBoardPanel.to_rect())
        myfont = pygame.font.SysFont('Calibri', 30)
        textsurf = myfont.render(f'Level : {self.gameLevel}', False, colors.BLACK)
        self.screen.blit(textsurf, self._scoreBoardPanel.get_coord_by_percent(0.02, 0.0))
        textsurf = myfont.render(f'Score : ', False, colors.BLACK)
        self.screen.blit(textsurf, self._scoreBoardPanel.get_coord_by_percent(0.02, 0.24))
        textsurf = myfont.render(f'{self.score:.1f}', False, colors.BLACK)
        self.screen.blit(textsurf, self._scoreBoardPanel.get_coord_by_percent(0.1, 0.4))
        # baisc info
        textsurf = myfont.render(f'Radius : {self.heroBall.radius}', False, colors.BLACK)
        self.screen.blit(textsurf, self._scoreBoardPanel.get_coord_by_percent(0.02, 0.5))
        textsurf = myfont.render(f'Velocity : {self.heroBall.velocity}', False, colors.BLACK)
        self.screen.blit(textsurf, self._scoreBoardPanel.get_coord_by_percent(0.02, 0.6))
        # status
        textsurf = myfont.render(f'Status', False, colors.BLACK)
        self.screen.blit(textsurf, self._scoreBoardPanel.get_coord_by_percent(0.02, 0.7))
        if self.heroBall.status is not None:
            width = self._scoreBoardPanel.width * 0.8
            height = self._scoreBoardPanel.width * 0.1

            if self.heroBall.status == Charactor.SPECIAL_GODLIKE:
                width *= (1.0 - (pygame.time.get_ticks() - self.heroBall.statusBeginTick) / (self._statusGodlikePeriod))
                self.screen.blit(self.imgs['statusGodlike'], self._scoreBoardPanel.get_coord_by_percent(0.5, 0.69))
            elif self.heroBall.status == Charactor.SPECIAL_FROZEN:
                width *= (1.0 - (pygame.time.get_ticks() - self.heroBall.statusBeginTick) / (self._statusFrozenPeriod))
                self.screen.blit(self.imgs['statusFrozen'], self._scoreBoardPanel.get_coord_by_percent(0.5, 0.69))

            pygame.draw.rect(self.screen, colors.BALL_COLOR_DICT[self.heroBall.status], Rect(*self._scoreBoardPanel.get_coord_by_percent(0.1, 0.8), width, height))

    def render_gameOver(self):
        # update record
        newRecFlag = False
        if self.score > self.scoreRecord and self.score > 0.0:
            with open(self._appDir / self._recordFileName, 'w') as recf:
                print('%d' % self.gameLevel, file=recf)
                print('%.1f' % self.score, file=recf)
            newRecFlag = True

        # render
        self.screen.fill(colors.GAMEOVER_BGCOLOR)
        myfont = pygame.font.SysFont('Calibri', 50)
        textsurf = myfont.render(f'Your Final Level: {self.gameLevel}', False, colors.BLACK)
        self.screen.blit(textsurf, (self._screenWidth * 0.16, self._screenHeight * 0.2))
        textsurf = myfont.render(f'Your Final Score: {self.score:.1f}', False, colors.BLACK)
        self.screen.blit(textsurf, (self._screenWidth * 0.16, self._screenHeight * 0.4))

        if newRecFlag:
            textsurf = myfont.render(f'New Record!', False, colors.BLACK)
        else:
            textsurf = myfont.render(f'Best Score Record: {self.scoreRecord}', False, colors.BLACK)
        self.screen.blit(textsurf, (self._screenWidth * 0.16, self._screenHeight * 0.6))

        textsurf = myfont.render(f'Press Enter to Exit', False, colors.BLACK)
        self.screen.blit(textsurf, (self._screenWidth * 0.16, self._screenHeight * 0.8))
        # update display
        pygame.display.update()
        # wait for an quit signal
        while True:
            event = pygame.event.wait()
            if event.type in (MOUSEBUTTONDOWN, QUIT):
                break
            elif event.type == KEYDOWN and event.key not in (K_DOWN, K_UP, K_LEFT, K_RIGHT, K_w, K_s, K_a, K_d):
                break

    def draw_ball(self, ball):
        if ball.event is not None:
            color = colors.BALL_COLOR_DICT[ball.event]
        elif ball.status is not None:
            color = colors.BALL_COLOR_DICT[ball.status]
        elif ball.charactor == Charactor.SPECIAL_RANDOM:
            color = colors.BALL_COLOR_DICT[random.choice(SPECIAL_CHARACTORS)]
        else:
            color = colors.BALL_COLOR_DICT[ball.charactor]
        pygame.draw.circle(self.screen, color, [int(x) for x in ball.position], int(ball.radius))
    
    def levelUp(self):
        self.gameLevel += 1
        self._genBallInterval *= self._levelUpGenBallIntervalRatio
        self._initialVelocityMagnitudeRange = tuple(x * self._levelUpVelocityRatio for x in self._initialVelocityMagnitudeRange)
        self._initialRadiusRange = tuple(x * self._levelUpRadiusRatio for x in self._initialRadiusRange)
    
    def collid_handler(self, ball):
        if ball.charactor == Charactor.ENEMY:
            if self.heroBall.status != Charactor.SPECIAL_GODLIKE:
                self._running = False
        else:
            # resolve random
            if ball.charactor == Charactor.SPECIAL_RANDOM:
                ball.charactor = random.choice(SPECIAL_CHARACTORS)
            # apply 
            self.heroBall.event = ball.charactor
            if ball.charactor == Charactor.SPECIAL_BIGGER:
                if self.heroBall.radius > self._heroBallRadiusRange[0]:
                    self.heroBall.radius += 1
            elif ball.charactor == Charactor.SPECIAL_SMALLER:
                if self.heroBall.radius < self._heroBallRadiusRange[1]:
                    self.heroBall.radius -= 1
            elif ball.charactor == Charactor.SPECIAL_SPEED_UP:
                if self.heroBall.velocity < self._heroBallVelocityRange[1]:
                    self.heroBall.velocity += 1
            elif ball.charactor == Charactor.SPECIAL_SPEED_DOWN:
                if self.heroBall.velocity > self._heroBallVelocityRange[0]:
                    self.heroBall.velocity -= 1
            elif ball.charactor == Charactor.SPECIAL_GODLIKE:
                self.heroBall.status = Charactor.SPECIAL_GODLIKE
                self.heroBall.statusBeginTick = pygame.time.get_ticks()
                set_timer(self._SPECIAL_GODLIKE_EXPIRE, self._statusGodlikePeriod - 1)
            elif ball.charactor == Charactor.SPECIAL_FROZEN:
                self.heroBall.status = Charactor.SPECIAL_FROZEN
                self.heroBall.statusBeginTick = pygame.time.get_ticks()
                set_timer(self._SPECIAL_FROZEN_EXPIRE, self._statusFrozenPeriod - 1)
    
    def scoreUp(self, balls, collide):
        basePoint = math.sqrt(self.gameLevel)
        if not collide:
            self.score += basePoint * len(balls)
        else:
            for ball in balls:
                self.score += basePoint * self._collideScoreCoef[ball.charactor]
    
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()
