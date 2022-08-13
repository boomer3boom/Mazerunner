from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
from PIL import Image,ImageTk

from a3_support import AbstractGrid
from constants import GAME_FILE, TASK

from a2_solution import *
from a2_support import *

from typing import Union

class Grid(AbstractGrid):
    def draw(self):

        
        image = Image.open('images/apple.png')
        image = image.resize((120, 120))
        self._photoimg = ImageTk.PhotoImage(image)

        self.create_image(400, 200, image = self._photoimg)
        self.create_image(300, 200, image = self._photoimg)

def test_grid():
    root = tk.Tk()
    grid = Grid(root,(5, 5), (500, 500))
    grid.draw()
    grid.pack()
    root.mainloop()

if __name__ == '__main__':
    test_grid()
    
