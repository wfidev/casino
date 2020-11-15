# =====================================================
#    Card.py
#      Basic class to represent a card in the Pile
# =====================================================

class Card:
    def __init__(self, Value, Color):
        self.Value = Value
        self.Color = Color

    def __repr__(self):
        return F"  {self.Color} {self.Value} ({self.GetPoints()} points)"

    def GetValue(self):
        return self.Value

    def GetColor(self):
        return self.Color 
    
    def GetPoints(self):
        if self.Color == 'black':
            if self.Value == 2:
                return 5
            return 1
        elif self.Color == 'red' and self.Value == 10:
            return 10
        return 0
         
                
