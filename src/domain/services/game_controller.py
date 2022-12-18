import pygame, sys, socket, threading, time, jsonpickle
from pygame.math import Vector2 as vec
import math
import os

from domain.models.network_data import Data as NetData
from domain.engine import enemies_controller
from domain.utils import colors, constants


playing = False
screen_size: vec = vec(0,0)
map_size: vec = vec(0,0)

bullet_groups = []

def handle_events(game):
    """Iterates through each event and call it's appropriate function.
    Args:
        game (Game): The currently running game.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_app()
        elif event.type == pygame.MOUSEBUTTONDOWN:
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

def quit_app():
    """Stops the game and closes application.
    """
    pygame.display.quit()
    pygame.quit()
    sys.exit()
    
def restart_game(game):
    """Reset game properties to start a new round.

    Args:
        game (domain.engine.game): The game to be restarted.
    """    
    game.pressed_keys = []
    game.command_id = 0
    game.map.rect.left = 0
    game.map.update_pos()
    game.enemies_group.empty()
    game.reset_players()
    screen_size: vec = vec(0,0)
    map_size: vec = vec(0,0)
    enemies_controller.spawn_random_enemy(game)
    
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
    threading.Thread(target=handle_connection, args=(game, client, game.player.net_id)).start()
    
def enter_game(game, host: str, port: int):
    """Joins a server from specified address and port.

    Args:
        game (domain.engine.game): The game to enter.
        host (str): The IP address of the server.
        port (int): The port number of the server.
    """   
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    
    #define game objects
    
    #implementar handle connection
    threading.Thread(target=handle_connection, args=(game, client, game.player.net_id)).start()
    
def handle_connection(game, client: socket.socket, player_id: int):
    """Function executing on a different thread, sending and receiving data from players.

    Args:
        game (domain.engine.game): The game object.
        client (socket.socket): The client object.
        player_id (int): The ID of the player executing this function.
    """    
    while playing:
        
        player = game.player
        
        data_to_send = NetData(
                net_id = player_id,
                message = f"Hello from player {player_id}",
                player_rect = (player.rect.left, player.rect.top, player.rect.width, player.rect.height),
                player_last_rect = (player.last_rect.left, player.last_rect.top, player.last_rect.width, player.last_rect.height),
                player_speed = (player.speed.x, player.speed.y),
                player_health = player.health,
                player_acceleration = (player.acceleration.x, player.acceleration.y),
                command_id = game.command_id,
                player_mouse_pos = pygame.mouse.get_pos(),
                player_offset_camera = player.offset_camera,
                player_aim_angle = player.weapon_aim_angle,
                player_falling_ground = player.falling_ground,
                player_running = player.running,
                player_jumping = player.jumping,
                player_turning_dir = player.turning_dir,
                player_firing = player.firing
            )
        
        client.send(class_to_json(data_to_send))
        data: NetData = json_to_class(client.recv(1024))
        
        if not data:
            continue
        else:
            game.handle_received_data(data)
            
        time.sleep(0.01)
                
    client.close()
    
    
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
    return jsonpickle.decode(data.decode('utf-8'))