from Card import *
from Deck import *
from Player import *

Paul = Player("Dreadful")
GameDeck = Deck()
GameDeck.Populate()

Paul.DealHand(GameDeck)
Paul.AddToPile(GameDeck.Deal(25))

print(Paul)
print("")
print(GameDeck)
