from pygame import Rect

class Panel:
    def __init__(self, left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.right = self.left + self.width
        self.bottom = self.top + self.height
    
    def get_coord_by_percent(self, widthPercent, heightPercent):
        return [round(self.left + self.width * widthPercent), round(self.top + self.height * heightPercent)]
    
    def to_rect(self):
        return Rect(self.left, self.top, self.width, self.height)