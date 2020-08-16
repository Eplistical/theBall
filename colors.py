from ball import Charactor

BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
BLUE    = (  0,   0, 255)
GREEN   = (  0, 255,   0)
RED     = (255,   0,   0)
YELLOW  = (255, 255,   0)
BROWN   = (102,  51,   0)
CYAN    = (  0, 255, 255)
PURPLE  = (127,   0, 255)



BGCOLOR                             = BLACK
PLAYGROUND_BGCOLOR                  = (128, 128, 128)
SCOREBOARD_BGCOLOR                  = (255, 128,   0)
GAMEOVER_BGCOLOR                    = (128, 128, 128)


HERO_COLOR                          = RED
ENEMY_COLOR                         = (  0, 102,   0)
SPECIAL_SPEED_UP_COLOR              = YELLOW
SPECIAL_SPEED_DOWN_COLOR            = BROWN
SPECIAL_SMALLER_COLOR               = CYAN
SPECIAL_BIGGER_COLOR                = BLUE
SPECIAL_GODLIKE_COLOR               = WHITE
SPECIAL_FROZEN_COLOR                = BLACK


BALL_COLOR_DICT = {
    Charactor.HERO : HERO_COLOR,
    Charactor.ENEMY : ENEMY_COLOR,
    Charactor.SPECIAL_SPEED_UP : SPECIAL_SPEED_UP_COLOR,
    Charactor.SPECIAL_SPEED_DOWN : SPECIAL_SPEED_DOWN_COLOR,
    Charactor.SPECIAL_SMALLER : SPECIAL_SMALLER_COLOR,
    Charactor.SPECIAL_BIGGER : SPECIAL_BIGGER_COLOR,
    Charactor.SPECIAL_GODLIKE : SPECIAL_GODLIKE_COLOR,
    Charactor.SPECIAL_FROZEN : SPECIAL_FROZEN_COLOR,
}