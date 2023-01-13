import pygame, socket, threading, time
from pygame.math import Vector2 as vec
import math
import os

from domain.utils import constants, enums
from domain.services import menu_controller, resources

screen_size: vec = vec(0,0)
map_size: vec = vec(0,0)

bullet_target_groups = []
enemy_target_groups = []

enemies_count = 0
bullets_count = 0

_enemy_netdata_keys = None
_bullet_netdata_keys = None
_waveresult_netdata_keys = None

def get_enemy_id():
    global enemies_count
    enemies_count += 1
    return enemies_count

def get_bullet_id():
    global bullets_count
    bullets_count += 1
    return bullets_count


def handle_events(game, events: list[pygame.event.Event]):
    """Iterates through each event and call it's appropriate function.
    Args:
        game (Game): The currently running game.
    """
    for event in events:
        if event.type == pygame.QUIT:
             menu_controller.quit_app()
        elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and game.focused:
            game.pressed_keys.append("mouse_0")
            
        elif event.type == pygame.MOUSEBUTTONUP and not pygame.mouse.get_pressed()[0]:
            if "mouse_0" in game.pressed_keys:
                game.pressed_keys.remove("mouse_0")
                
        elif event.type == pygame.MOUSEWHEEL and event.y != 0:
            if f"wheel_{event.y}" not in game.pressed_keys:
                game.pressed_keys.append(f"wheel_{1 if event.y > 0 else -1}")
                
        
        
                
        elif event.type == pygame.KEYDOWN and game.focused:
            handle_keydown(event.key, game)
        elif event.type == pygame.KEYUP and game.focused:
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
    menu_controller.pages_history = menu_controller.pages_history[:-1]
    menu_controller.pages_history[-1].start_game(game.client_type)
    
def load_sounds(folder_path: str, volume: int = 1):
    """Loads all mp3 files from the specified folter into a list of mixer.Sound.

    Args:
        folder_path (str): The path to the folder containing the images.

    Returns:
        list[mixer.Sound]: A list of the sounds.
    """    
    _path = resources.ROOT_PATH + folder_path
    if not os.path.exists(_path):
        return
    
    sounds = [pygame.mixer.Sound(_path + "\\" + img) for img in os.listdir(_path) if img.endswith('.mp3')]
    if volume != 1:
        for s in sounds:
            s.set_volume(volume)
    return sounds
    
def load_sprites(folder_path: str, scale = 1, convert_type: enums.ConvertType = enums.ConvertType.CONVERT):
    """Loads all png files from the specified folter into a list of pygame.Surface.

    Args:
        folder_path (str): The path to the folder containing the images.

    Returns:
        list[pygame.Surface]: A list of the images.
    """    
    _path = resources.ROOT_PATH + folder_path
    if not os.path.exists(_path):
        return
    
    if scale != 1:
        images = [scale_image(pygame.image.load(_path + "\\" + img), scale) for img in os.listdir(_path) if img.endswith('.png')]
    else:
        images = [pygame.image.load(_path + "\\" + img) for img in os.listdir(_path) if img.endswith('.png')]
    
    match convert_type:
        case enums.ConvertType.CONVERT:
            return [x.convert() for x in images]
        case enums.ConvertType.CONVERT_ALPHA:
            return [x.convert_alpha() for x in images]
        case _:
            return images
    
def scale_image(image: pygame.Surface, scale: float, convert_type: enums.ConvertType = enums.ConvertType.NO_CONVERT):
    """Scales a image to the given float size.

    Args:
        image (pygame.Surface): The image to be scaled.
        scale (float): The scale proportional to the original image (1.5, 2.0, 0.5...)

    Returns:
        pygame.Surface: The scaled image.
    """    
    img = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))
    
    match convert_type:
        case enums.ConvertType.CONVERT:
            return img.convert()
        case enums.ConvertType.CONVERT_ALPHA:
            return img.convert_alpha()
        case _:
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
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))
    # server started #
    
    # waiting for client connection attempt
    message, client_address = server.recvfrom(8)
    
    message = message.decode('utf-8')
    # if the message is a connection attempt
    if message == "CONNECT":
        # return ok and start the game
        server.sendto('OK'.encode('utf-8'), client_address)
        threading.Thread(target=handle_connection, args=(game, server, client_address)).start()
    
    
def try_enter_game(game, host: str, port: int, timeout = 2):
    """Joins a server from specified address and port.

    Args:
        game (domain.engine.game): The game to enter.
        host (str): The IP address of the server.
        port (int): The port number of the server.
    """   
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(timeout)
    # trying to connect to host
    client.sendto('CONNECT'.encode('utf-8'), (host, port))
    
    try:
        # check for response
        message, host_address = client.recvfrom(8)
        message = message.decode('utf-8')
        
        # if response is ok, start the game
        if message == "OK":
            threading.Thread(target=handle_connection, args=(game, client, host_address)).start()
            return True
        else:
            client.close()
            return False
    except (ConnectionResetError, TimeoutError):
        client.close()
        return False
       

send_count = 0
receive_count = 0

def handle_connection(game, client: socket.socket, remote_address: tuple[str, int]):
    """Function executing on a different thread, sending and receiving data from players.

    Args:
        game (domain.engine.game): The game object.
        client (socket.socket): The client object.
        player_id (int): The ID of the player executing this function.
    """ 
    client.settimeout(2)
    
    while menu_controller.playing:
        
        #sending
        net_data = game.get_net_data()
        data_to_send = net_data._get_buffer()
        client.sendto(data_to_send, remote_address)
        
        #receiving
        received_buffer = client.recvfrom(4096)[0]
        net_data._load_buffer(received_buffer)
        # print(len(received_buffer))
        
        game.handle_received_data(net_data)
            
        time.sleep(0.01)
              
    
    print("closing connection")
    client.close()
    
