import pygame, socket, threading, time, jsonpickle
from pygame.math import Vector2 as vec
import math
import os

from domain.models.network_data import Data as NetData
from domain.engine import enemies_controller
from domain.utils import constants
from domain.services import menu_controller


playing = False
screen_size: vec = vec(0,0)
map_size: vec = vec(0,0)

bullet_groups = []

def handle_events(game, events: list[pygame.event.Event]):
    """Iterates through each event and call it's appropriate function.
    Args:
        game (Game): The currently running game.
    """
    for event in events:
        if event.type == pygame.QUIT:
             menu_controller.quit_app()
        elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
            _bullet = game.player.shoot()
            game.projectiles.append(_bullet)
        elif event.type == pygame.KEYDOWN:
            handle_keydown(event.key, game)
        elif event.type == pygame.KEYUP:
            handle_keyup(event.key, game)
                
                
def handle_keydown(key, game):
    """Decides what to do with the key pressed by the user.
    Args:
        key (int): The pygame keycode of the key.
        game (Game): The currently running game.
    """
    if key not in game.pressed_keys:
        game.pressed_keys.append(key)
    

def handle_keyup(key, game):
    """Decides what to do with the key released by the user.
    Args:
        key (int): The pygame keycode of the key.
        game (Game): The currently running game.
    """
    if key in game.pressed_keys:
        game.pressed_keys.remove(key)


    
def restart_game(game):
    """Reset game properties to start a new round.

    Args:
        game (domain.engine.game): The game to be restarted.
    """
    game.pressed_keys = []
    game.command_id = 0
    game.map.rect.left = 0
    game.enemies_group.empty()
    game.reset_players()
    
def load_sprites(folder_path: str):
    """Loads all png files from the specified folter into a list of pygame.Surface.

    Args:
        folder_path (str): The path to the folder containing the images.

    Returns:
        list[pygame.Surface]: A list of the images.
    """    
    _path = constants.ROOT_PATH + folder_path
    if not os.path.exists(_path):
        return
    
    images = [pygame.image.load(_path + "\\" + img) for img in os.listdir(_path) if img.endswith('.png')]
    return images
    
def scale_image(image: pygame.Surface, scale: float):
    """Scales a image to the given float size.

    Args:
        image (pygame.Surface): The image to be scaled.
        scale (float): The scale proportional to the original image (1.5, 2.0, 0.5...)

    Returns:
        pygame.Surface: The scaled image.
    """    
    img = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))
    return img

def angle_to_mouse(pos: vec, mouse_pos: vec):
    rel_x, rel_y = mouse_pos.x - pos.x, mouse_pos.y - pos.y
    return (180 / math.pi) * -math.atan2(rel_y, rel_x)
    
def rotate_to_angle(image: pygame.Surface, pos:vec, angle: float):
    _image = pygame.transform.rotate(image, int(angle))
    _rect = _image.get_rect(center= pos)
    return _image, _rect

def rotate_image(image: pygame.Surface, angle: float):
    rotated_image = pygame.transform.rotate(image, angle)
    # new_rect = rotated_image.get_rect(center = image.get_rect().center)
    return rotated_image

def point_to_angle_distance(pos: vec,distance: float, angle_in_radians: float):
    x = pos.x + (distance*math.cos(angle_in_radians))
    y = pos.y + (distance*math.sin(angle_in_radians))
    return vec(x, y)
    
def host_game(game, host: str, port: int):
    """Creates a server on the specified address and port.

    Args:
        game (domain.engine.game): The game to host the game.
        host (str): The IP address of the server.
        port (int): The port number of the server.
    """    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)
    client, addr = server.accept()
    
    #define game objects
    
    #implementar handle connection
    threading.Thread(target=handle_connection, args=(game, client)).start()
    
def try_enter_game(game, host: str, port: int, timeout = 2):
    """Joins a server from specified address and port.

    Args:
        game (domain.engine.game): The game to enter.
        host (str): The IP address of the server.
        port (int): The port number of the server.
    """   
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(timeout)
    result = client.connect_ex((host, port))
    if result == 0:
        threading.Thread(target=handle_connection, args=(game, client)).start()
        return True
    else:
        client.close()
        return False

send_count = 0
receive_count = 0

def handle_connection(game, client: socket.socket):
    """Function executing on a different thread, sending and receiving data from players.

    Args:
        game (domain.engine.game): The game object.
        client (socket.socket): The client object.
        player_id (int): The ID of the player executing this function.
    """  
    while playing:
        
        player = game.player
        
        data_to_send = game.get_net_data()
        
        
        
        client.send(class_to_json(data_to_send))
        
        
        json_string: str = client.recv(2048).decode('utf-8')
        
        if json_string[0] != "{":
            continue
        
        final_json = validate_json(json_string)
        
        data: NetData = json_to_class(final_json)
        
        if not data:
            continue
        else:
            game.handle_received_data(data)
            
        time.sleep(0.01)
                
    client.close()
    
    
    
def validate_json(value):
    i = value.index("_json_size_") + 17
    # extra = value[i:]
    # print('\nvalue:\n\n',value)
    # print('\extra:\n\n',extra)
    # print(len(extra))
    return value[:i]
    
def class_to_json(data):
    """Encodes the class object to a json object.

    Args:
        data (class): The object to be converted.

    Returns:
        list[byte]: A array of bytes containing a json string version of the class.
    """    
    return jsonpickle.encode(data).encode('utf-8')

def json_to_class(data):
    """Decodes the json string to a class object.

    Args:
        data (list[byte]): A array of bytes containing a json string version of the class.

    Returns:
        class: The converted class object.
    """  

    return jsonpickle.decode(data)
