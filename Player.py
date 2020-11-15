from Utils import *
from Pile import Pile
from Card import Card

# =====================================================
#    Player.py
#      Class to represent a player in the game
# =====================================================
class Player:
    def __init__(self, Name):
        self.Name = Name
        self.Hand = Pile()
        self.Pile = Pile()

    def __repr__(self):
        Output(f"Player: {self.Name}")
        Output("  Current Hand")
        Output("  ------------")
        Output(self.Hand)
        Output("")
        Output("  Current Pile")
        Output("  ------------")
        Output(self.Pile)
        return ""

    def GetName(self):
        return self.Name

    def GetPile(self):
        return self.Pile

    def GetHand(self):
        return self.Hand

    # Deal a hand to this player based on the Pile for the game which 
    # is provided as an input
    #
    def DealHand(self, GamePile):
        Cards = GamePile.Deal(4)
        self.Hand.Reset()
        for Card in Cards:
            self.Hand.AddCard(Card)

    # Add cards to a player's pile that were taken down from board.  The piles on the 
    # board will be represented as Piles as will the player's pile.
    #
    def AddToPile(self, Cards):
        self.Pile.AddCards(Cards) 

