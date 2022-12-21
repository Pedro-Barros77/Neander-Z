
#Basics
RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = (255,255,0)
BLUE = (0,0,255)
WHITE = (255,255,255)
BLACK = (0,0,0)


LIGHT_GRAY = (150,150,150)

SELECTION_BLUE = (10,103,214)

def set_alpha(color: tuple[int,int,int], value = 255):
    if color == None:
        return None
    return (color[0], color[1], color[2], value)

def alpha_or_default(color: tuple[int,int,int], value = 255):
    if color == None:
        return None
    alpha = value
    if len(color) > 3:
        alpha = color[3]
    return (color[0], color[1], color[2], alpha)