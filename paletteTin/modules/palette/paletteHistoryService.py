# stacklimit is not working, is unding n-1 not n
class PaletteHistoryService:
    def __init__(self, stackLimit=5):
        self.history = []
        self.currentIndex = -1  # Tracks where we are in the history
        self.stackLimit = stackLimit

    def appendPalette(self, palette):
        if len(self.history) >= self.stackLimit:
            self.history.pop(0)  # Remove the oldest palette
            self.currentIndex = self.stackLimit - 2
        
        self.history.append(palette)
        self.currentIndex += 1 

    def updateStackLimit(self, newLimit: int):
        self.stackLimit = newLimit

    def getLastPalettes(self):
        return self.history
    
    def toString(self):
        print(self.currentIndex)

    def reset(self):
        self.history = []
        self.currentIndex = -1

    def returnPreviousPalette(self):
        if len(self.history) <= 1:
            return None  # No palettes in history
        self.history.pop(self.currentIndex)
        self.currentIndex -= 1
        palette = self.history[self.currentIndex]
        return palette