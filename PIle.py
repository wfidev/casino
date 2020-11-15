from Utils import *
from Card import Card

# =====================================================
#    Pile.py
#    Basic class to represent a pile of cards.
# =====================================================

class Pile:
    def __init__(self):
        self.Reset()

    def __repr__(self):
        SummaryString = f"  Pile of {len(self.Cards)} cards, {self.GetPointTotal()} points" 
        for Card in self.Cards:
            Output(Card)
        return SummaryString

    def Reset(self):
        self.Cards = []

    def GetCards(self):
        return self.Cards

    def GetPointTotal(self):
        Points = 0
        for Card in self.Cards:
            Points += Card.GetPoints()
        return Points

    # Populates a Pile with the standard set of Cards in a Rook Deck. 
    #
    def Populate(self, Decks = 1):  
        for PileIndex in range(0, Decks):
            for Color in Pile.GetColors():
                for Value in range(1, 14):
                    self.AddCard(Card(Value, Color))

    def GetColors():
        return ['red', 'black', 'green', 'orange']

    def Shuffle(self):
        return              # TODO: implement this function

    def Deal(self, CardCount = 1):
        Cards = []
        if len(self.Cards) < CardCount:
            return None
        for i in range(0, CardCount):
            Cards.append(self.Cards.pop())
        return Cards

    def AddCard(self, Card):
        self.Cards.append(Card)

    def AddCards(self, Cards):
        for Card in Cards:
            self.AddCard(Card)