from Deck import Deck
from Card import Card

# =====================================================
#    Player.py
#      Class to represent a player in the game
# =====================================================
class Player:
    def __init__(self, Name):
        self.Name = Name
        self.Hand = Deck()
        self.Pile = Deck()

    def __repr__(self):
        print(f"Player: {self.Name}")
        print("  Current Hand")
        print("  ------------")
        print(self.Hand)
        print("")
        print("  Current Pile")
        print("  ------------")
        print(self.Pile)
        return ""

    def GetName(self):
        return self.Name

    def GetPile(self):
        return self.Pile

    def GetHand(self):
        return self.Hand

    # Deal a hand to this player based on the deck for the game which 
    # is provided as an input
    #
    def DealHand(self, GameDeck):
        Cards = GameDeck.Deal(4)
        self.Hand.Reset()
        for Card in Cards:
            self.Hand.AddCard(Card)

    # Add cards to a player's pile that were taken down from board.  The piles on the 
    # board will be represented as Decks as will the player's pile.
    #
    def AddToPile(self, Cards):
        self.Pile.AddCards(Cards) 

