# Pathfinder by Brigham Aldrich

import random, pygame, sys, math
from pygame.locals import *
from array import *
from numpy import *

####################################################################################################
############################################ CONSTANTS #############################################
####################################################################################################

# COLOR       R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
YELLOW    = (255, 255,   0)
PURPLE    = (255,   0, 255)
DARKGREEN = (  0, 155,   0)
DARKRED   = (155,   0,   0)
BLUE      = (  0,   0, 255)
DARKBLUE  = (  0,   0, 155)
DARKGRAY  = ( 40,  40,  40)
LIGHTGRAY = (220, 220, 220)
BGCOLOR   = WHITE

####################################################################################################
######################################### GAME PARAMETERS ##########################################
####################################################################################################

FPS          = 600
WINDOWWIDTH  = 1200
WINDOWHEIGHT = 800
CELLSIZE     = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH  = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

####################################################################################################
############################################# CLASSES ##############################################
####################################################################################################

class Spot:
    def __init__ (this, x, y, f, g, h, cellType):
        this.x = x
        this.y = y
        this.f = f
        this.g = g
        this.h = h
        this.cellType = cellType
        this.previous = None

####################################################################################################
############################################### MAIN ###############################################
####################################################################################################

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, START, END, GRID, PATH

    pygame.init()
    FPSCLOCK    = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT   = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('pathfinder')

    START = getRandomLocation()
    END   = getRandomLocation()
    GRID = generateBlankStartGrid()
    PATH = []
    
    setRandomStartGrid(30)
    AStar()

####################################################################################################
############################################ ALGORITHMS ############################################
####################################################################################################

# The AStar algorithm finds an optimal path from START to END very quickly by biasing its search
# with an idealized heuristic path
def AStar():
    openSet = []
    closedSet = []
    openSet.append(START)
    closedSet.append(START)
    current = START
    GRID[START['y']][START['x']].g = 0

    while(True):
        if(checkQuit()): return
        if(len(openSet) == 0 or closedSet[-1] == END):
            drawUpdate(openSet, closedSet)
            break

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawUpdate(openSet, closedSet)

        bestIndex = 0
        for i in range(len(openSet)):
            if(getSpot(openSet[i]).f < getSpot(openSet[bestIndex]).f):
                bestIndex = i

        current = openSet[bestIndex]
        openSet.pop(bestIndex)
        closedSet.append(current)

        neighbors = findNeighbors(current)
        for n in neighbors:
            if(n in closedSet):
                continue
            if(n not in openSet):
                openSet.append(n)
            GRID[n['y']][n['x']].g = min(getSpot(n).g, getSpot(current).g + 1)
            GRID[n['y']][n['x']].h = heuristic(n)
            GRID[n['y']][n['x']].f = min(getSpot(n).f, getSpot(n).g + getSpot(n).h)
            GRID[n['y']][n['x']].previous = current


        PATH.clear()
        temp = current
        while(getSpot(temp).previous):
            PATH.append(getSpot(temp).previous)
            temp = getSpot(temp).previous
        pygame.display.update()
        FPSCLOCK.tick(FPS)
    
    while(True):
        if(checkQuit()): return
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

####################################################################################################
######################################## UTILITY FUNCTIONS #########################################
####################################################################################################

# Checks to see if the game has been quit or reset
def checkQuit():
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        if(event.type == KEYDOWN):
            if event.key == K_RETURN:
                return True
    return False

# Closes the window
def terminate():
    pygame.quit()
    sys.exit()

####################################################################################################
########################################## GRID FUNCTIONS ##########################################
####################################################################################################

# Returns a random coord on the GRID
def getRandomLocation():
    return {
        'x' : random.randint(0, CELLWIDTH - 1),
        'y' : random.randint(0, CELLHEIGHT - 1)
    }

# Returns the spot on the GRID that corresponds to the input coord
def getSpot(coord):
    return GRID[coord['y']][coord['x']]

# Returns the coordinates of all of the neighbors of the input coord
def findNeighbors(coord):
    neighbors = []
    n1 = {'x': coord['x'] + 1, 'y': coord['y']    }
    n2 = {'x': coord['x'] - 1, 'y': coord['y']    }
    n3 = {'x': coord['x'],     'y': coord['y'] + 1}
    n4 = {'x': coord['x'],     'y': coord['y'] - 1}

    if(coord['x'] < CELLWIDTH - 1 and getSpot(n1).cellType != BLACK):
        neighbors.append(n1)
    if(coord['x'] > 0 and getSpot(n2).cellType != BLACK):
        neighbors.append(n2)
    if(coord['y'] < CELLHEIGHT - 1 and getSpot(n3).cellType != BLACK):
        neighbors.append(n3)
    if(coord['y'] > 0 and getSpot(n4).cellType != BLACK):
        neighbors.append(n4)
    return neighbors

# Returns and idealized path (heuristic) from the input coord to the END coord
def heuristic(coord):
    return abs(END['x'] - coord['x']) + abs(END['y'] - coord['y'])
    # return math.dist([coord['x'], coord['y']], [END['x'], END['y']])

# Returns a new blank game grid
def generateBlankStartGrid():
    grid = [[0 for x in range(CELLWIDTH)] for y in range(CELLHEIGHT)]
    for i in range(0, CELLHEIGHT):
        for j in range(0, CELLWIDTH):
            grid[i][j] = Spot(j, i, 100000, 100000, 100000, WHITE)
            if(i == START['y'] and j == START['x']):
                grid[i][j] = Spot(j, i, 100000, 100000, 100000, GREEN)
            if(i == END['y'] and j == END['x']):
                grid[i][j] = Spot(j, i, 100000, 100000, 100000, RED)
    return grid

# Sets the game GRID to a randomly generated map based on difficulty
def setRandomStartGrid(difficulty):
    for i in range(0, CELLHEIGHT):
        for j in range(0, CELLWIDTH):
            rand = random.randint(0, 100)
            if(rand < difficulty):
                GRID[i][j] = Spot(j, i, 100000, 100000, 100000, BLACK)
            else:
                GRID[i][j] = Spot(j, i, 100000, 100000, 100000, WHITE)
            if(i == START['y'] and j == START['x']):
                GRID[i][j] = Spot(j, i, 100000, 100000, 100000, GREEN)
            if(i == END['y'] and j == END['x']):
                GRID[i][j] = Spot(j, i, 100000, 100000, 100000, RED)


####################################################################################################
######################################## DRAWING FUNCTIONS #########################################
####################################################################################################

# Updates the color of squares in the openSet, closedSet, and PATH accordingly
def drawUpdate(openSet, closedSet):
    for s in openSet:
        if(s == START or s == END): continue
        GRID[s['y']][s['x']].cellType = YELLOW

    for s in closedSet:
        if(s == START or s == END): continue
        GRID[s['y']][s['x']].cellType = BLUE

    for s in PATH:
        if(s == START or s == END): continue
        GRID[s['y']][s['x']].cellType = PURPLE

# Draws a square on the GRID at location: coord with color: color
def drawSquare(coord, color):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    Rect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, color, Rect)

# Draws the entire game GRID using the game size parameters
def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, LIGHTGRAY, (x, 0), (x, WINDOWHEIGHT))

    for y in range(0, WINDOWHEIGHT, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, LIGHTGRAY, (0, y), (WINDOWWIDTH, y))

    for i in range(CELLHEIGHT):
        for j in range(CELLWIDTH):
            drawSquare({'x': j, 'y': i}, GRID[i][j].cellType)





if __name__ == '__main__':
    while True:
        main()
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        pygame.display.update()
        FPSCLOCK.tick(FPS)