from Utils import *
from Pile import Pile
from Card import Card

# =====================================================
#    Game.py
#      Class to represent a game
# =====================================================
class Game:
    def __init__(self):
        self.Players = []
        self.CurrentPlayer = None
        self.Board = []                 # The game board is represented as a list of Piles