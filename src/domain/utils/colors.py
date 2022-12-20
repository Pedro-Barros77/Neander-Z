
#Basics
RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = (255,255,0)
BLUE = (0,0,255)
WHITE = (255,255,255)
BLACK = (0,0,0)


LIGHT_GRAY = (150,150,150)

SELECTION_BLUE = (10,103,214)

def add_alpha(color: tuple[int,int,int], value = 255):
    return (color[0], color[1], color[2], value)