
#Basics
RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = (255,255,0)
BLUE = (0,0,255)
WHITE = (255,255,255)
BLACK = (0,0,0)


LIGHT_GRAY = (150,150,150)
DARK_GRAY = (30, 30, 30)
SCROLL_GRAY = (99, 99, 99)
LIGHT_BLUE = (19, 92, 209)

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

def add(color1: tuple[int,int,int], color2: tuple[int,int,int]):
    if len(color1) == 4 or len(color2) == 4:
        color1 = alpha_or_default(color1, 255)
        color2 = alpha_or_default(color2, 255)
        return (color1[0] + color2[0], color1[1] + color2[1], color1[2] + color2[2], color1[3] + color2[3])
    return (color1[0] + color2[0], color1[1] + color2[1], color1[2] + color2[2])
