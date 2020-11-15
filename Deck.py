from Card import Card

# =====================================================
#    Deck.py
#    Basic class to represent a deck of cards
# =====================================================

class Deck:
    def __init__(self):
        self.Reset()

    def __repr__(self):
        SummaryString = f"  Deck of {len(self.Cards)} cards, {self.GetPointTotal()} points" 
        for Card in self.Cards:
            print(Card)
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

    # Populates a deck with the standard set of Cards in a Rook deck. 
    #
    def Populate(self, RookDecks = 1):  
        for CurrentDeck in range(0, RookDecks):
            for Color in Deck.GetColors():
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