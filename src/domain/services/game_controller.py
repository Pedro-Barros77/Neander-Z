import pygame, sys, socket, threading, time, jsonpickle

from domain.models.network_data import Data as NetData


playing = False

def handle_events(game):
    """Iterates through each event and call it's appropriate function.
    Args:
        game (Game): The currently running game.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_app()
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
    game.pressed_keys = []
    game.command_id = 0
    game.reset_players()
    
def scale_image(image: pygame.Surface, scale):
    img = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))
    return img

    
def host_game(game, host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)
    client, addr = server.accept()
    
    #define game objects
    
    #implementar handle connection
    threading.Thread(target=handle_connection, args=(game, client, int(game.player.net_id))).start()
    
def enter_game(game, host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    
    #define game objects
    
    #implementar handle connection
    threading.Thread(target=handle_connection, args=(game, client, int(game.player.net_id))).start()
    
def handle_connection(game, client: socket.socket, player_id):
    while playing:
        
        player = game.player
        
        data_to_send = NetData(
                net_id = player_id,
                message = f"Hello from player {player_id}",
                player_pos = (player.pos.x, player.pos.y),
                player_size = player.size,
                player_color = player.color,
                player_speed = (player.speed.x, player.speed.y),
                player_acceleration = (player.acceleration.x, player.acceleration.y),
                player_last_rect = player.last_rect,
                command_id = game.command_id
            )
        
        client.send(class_to_json(data_to_send))
        data: NetData = json_to_class(client.recv(1024))
        
        if not data:
            continue
        else:
            # print(f"P1: {player.pos}, P2: {data.player_pos}")
            game.handle_received_data(data)
            
        time.sleep(0.01)
        # print('while:', player_id)
                
    client.close()
    
    
def class_to_json(data):
    return jsonpickle.encode(data).encode('utf-8')

def json_to_class(data):
    return jsonpickle.decode(data.decode('utf-8'))