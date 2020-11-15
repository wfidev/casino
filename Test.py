from Card import Card
from Pile import Pile
from Player import Player

Paul = Player("Dreadful")
GamePile = Pile()
GamePile.Populate()

Paul.DealHand(GamePile)
Paul.AddToPile(GamePile.Deal(25))

Output(Paul)
Output("")
Output(GamePile)
