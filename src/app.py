from domain.engine.game import Game
from domain.utils import math_utillity as math
from domain.utils.enums import ClientType

client_type = ClientType.UNDEFINED
while client_type == ClientType.UNDEFINED:
    client_type = ClientType(math.try_parse_int(input("Deseja hospedar (1) ou entrar em um jogo? (2) ou (3) para singlePLayer")))
    if client_type == ClientType.UNDEFINED:
        print("Valor inválido!")


game = Game(client_type)
game.start()
