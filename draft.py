from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
from PIL import Image,ImageTk

from a3_support import AbstractGrid
from constants import GAME_FILE, TASK

from a2_solution import *
from a2_support import *

from typing import Union
#Is this allowed?
import time

stats_row = 2
stats_column = 4
# Write your classes here
class LevelView(AbstractGrid):
    """
    The LevelView class inherits from AbstractGrid. It displays the maze (which is a bunch of tiles), along with the entities.
    The entities can split into player and the item. Each type of tiles have their own unique colour which can be accessed from
    constants.py. Each entity also have its own colour, and the annotation labelled on top of these entity is their ID.
    """

    def draw(self, tiles: list[list[Tile]], items: dict[tuple[int, int], Item], player_pos: tuple[int, int]) -> None:
        """
        Draws the maze which includes the tiles, items on that maze level, and player's position.

        Parameters:
        Tiles: This is a nested list. The outer list contains the row of tiles, while the inner list contains the instance of the tiles.
        items: This is a dictionary containing the items in this level of maze. The key is the position that the item is located in. The
                value is the instance of that item.
        player_pos: This is a tuple that has 2 integers. This is the player's position on the maze.
        """

        #Because of the structure of this assignment, the maze needs to be cleared before re-drawing.
        #This becomes a bit more logical at class Graphical Interface and Graphical MazeRunner
        self.clear() 

        #Since tiles is a list of tiles within another list.
        #The first for-loop will iterate through the outer list, and therefore access the rows.
        row_counter = 0
        for row in tiles:
            
            col_counter = 0

            #The second for-loop access the tiles inside the rows.
            for tile in row:
                
                #Access the bounding box(bbox) for that tile, and create a rectangle around it.
                bbox = self.get_bbox((row_counter, col_counter))
                #TILE_COLOUR is dictionary from constants that take tile ID as key to get colour.
                self.create_rectangle(bbox, fill = TILE_COLOURS[tile.get_id()])

                col_counter += 1

            row_counter += 1

        #Since items is a dictionary with a position as key, and instance of item as value.
        #For-loop through each key in items to access the position of item instance.
        for key in items:

            #Access bbox at that position, and create an oval. ENTITY_COLOURS is from constants.py
            #and it takes item's ID as key to get a colour.
            bbox = self.get_bbox(key)
            self.create_oval(bbox, fill = ENTITY_COLOURS[items[key].get_id()])

            #annotate that position with the item's ID.
            self.annotate_position(key, items[key].get_id())


        #Access bbox as player's position. Create an Oval, and label is with player ID.
        bbox = self.get_bbox(player_pos)
        self.create_oval(bbox, fill = ENTITY_COLOURS[PLAYER])
        self.annotate_position(player_pos, PLAYER)

class StatsView(AbstractGrid):
    """
    The StatsView class inherits from AbstractGrid which is from a3 support file. It displays the player's HP, health,
    thirst and the number of coins in player's inventory. However, drawing the coin will occur in a seperate function,
    since it reuiqres access to player's inventory while the other three does not. A StatView have 4 columns and two rows.
    The first row contains the header and the second row contains the value.
    """

    def __init__(self, master: Union[tk.Tk, tk.Frame], width: int, **kwargs) -> None:
        """
        Initiaite the StatView instance by calling the __init__ function from abstractgrid, and then giving it the value
        required.
        """
        super().__init__(master, (stats_row, stats_column), (width, STATS_HEIGHT), bg = THEME_COLOUR)

        #this is a tuple used to help set up the header name of the four titles.
        #this will be used in draw_stats and draw_coins.
        self._Title = ("HP", "Hunger", "Thirst", "Coins")

    def draw_stats(self, player_stats: tuple[int, int, int]) -> None:
        """

        """

        for col in range(len(player_stats)):
            self.annotate_position((0, col), self._Title[col])
            self.annotate_position((1, col), player_stats[col])

    def draw_coins(self, num_coins: int) -> None:

        self.annotate_position((0, 3), self._Title[3])
        self.annotate_position((1, 3), num_coins)

class InventoryView(tk.Frame):

    def __init__(self, master: Union[tk.Tk, tk.Frame], **kwargs) -> None:
        super().__init__(master, width = INVENTORY_WIDTH, height = MAZE_HEIGHT, **kwargs)
        self._InventHeader = tk.Label(self, text = 'Inventory', font = HEADING_FONT)
        self._InventHeader.pack(fill=tk.X)
        self._items = ['Potion', 'Honey', 'Apple', 'Water']

    def set_click_callback(self, callback: Callable[[str], None]) -> None:
        self._callback = callback

    def clear(self) -> None:
        name = self.winfo_children()
        for n in name:
            if n == self._InventHeader:
                pass
            else:
                n.destroy()

    #Fill the labels
    def _draw_item(self, name: str, num: int, colour: str) -> None:
        label = name + ': ' + str(num)
        item_label = tk.Label(self, text = label, bg = colour, font = TEXT_FONT)
        item_label.pack(side = tk.TOP, anchor = tk.CENTER, fill = tk.BOTH)
        #item_label.bind("<Button-1>", lambda e: self.set_click_callback(name))
        item_label.bind("<Button-1>", lambda e: self._callback(name))

    def draw_inventory(self, inventory: Inventory) -> None:
        self.clear()
        for item in inventory.get_items().keys():
            if str(item) in self._items:
                no_item = len(inventory.get_items()[item])
                colour = ENTITY_COLOURS[inventory.get_items()[item][0].get_id()]
                self._draw_item(item, no_item, colour)

class GraphicalInterface(UserInterface):

    def __init__(self, master: tk.Tk) -> None:
        self._GI = master
        self._Header = tk.Label(self._GI, text = 'MazeRunner', font = BANNER_FONT, bg = THEME_COLOUR)
        self._Header.pack(side = tk.TOP, fill = tk.BOTH)

    def create_interface(self, dimensions: tuple[int, int]) -> None:
        if TASK == 1:
            self._LevelView = LevelView(self._GI, dimensions, (MAZE_WIDTH, MAZE_HEIGHT))
        if TASK == 2:
            self._ILevelView = ImageLevelView(self._GI, dimensions, (MAZE_WIDTH, MAZE_HEIGHT))

        self._StatsView = StatsView(self._GI, MAZE_WIDTH + INVENTORY_WIDTH )
        self._InventoryView = InventoryView(self._GI)

        self._StatsView.pack(side=tk.BOTTOM)
        
        if TASK == 1:
            self._LevelView.pack(side=tk.LEFT)
        if TASK ==2:
            self._ILevelView.pack(side=tk.LEFT)
            
        self._InventoryView.pack(side=tk.LEFT, anchor = tk.N, fill=tk.BOTH, expand=True)

    def clear_all(self) -> None:
        if TASK == 1:
            self._LevelView.clear()
        if TASK == 2:
            self._ILevelView.clear()
        self._StatsView.clear()

    def set_maze_dimensions(self, dimensions: tuple[int, int]) -> None:
        if TASK == 1:
            self._LevelView.set_dimensions(dimensions)
        if TASK == 2:
            self._ILevelView.set_dimensions(dimensions)
    def bind_keypress(self, command: Callable[[tk.Event], None]) -> None:
        self._GI.bind('<Key>', command)
        
    def set_inventory_callback(self, callback: Callable[[str], None]) -> none:
        self._InventoryView.set_click_callback(callback)

    def draw_inventory(self, inventory: Inventory) -> None:
        self._InventoryView.draw_inventory(inventory)

    def draw(self, maze: Maze, items: dict[tuple[int, int], Item], player_position: tuple[int, int], inventory: Inventory, player_stats: tuple[int, int, int]) -> None:
        self.clear_all()
        self._draw_level(maze, items, player_position)
        self.draw_inventory(inventory)
        self._draw_player_stats(player_stats)
        self._draw_inventory(inventory)
        
    def _draw_inventory(self, inventory: Inventory) -> None:
        if 'Coin' in inventory.get_items().keys():
            no_coins = len(inventory.get_items()['Coin'])
            self._StatsView.draw_coins(no_coins)
        else:
            no_coins = 0
            self._StatsView.draw_coins(no_coins)

    def _draw_level(self, maze: Maze, items: dict[tuple[int, int], Item], player_position: tuple[int, int]) -> None:
        if TASK == 1:
            self._LevelView.draw(maze.get_tiles(), items, player_position)
        if TASK ==2:
            self._ILevelView.draw(maze.get_tiles(), items, player_position)

    def _draw_player_stats(self, player_stats: tuple[int, int, int]) -> None:
        self._StatsView.draw_stats(player_stats)

class GraphicalMazeRunner(MazeRunner):

    def __init__(self, game_file: str, root: tk.Tk) -> None:
        super().__init__(game_file, root)
        self._GI = GraphicalInterface(root)
        self._GI.create_interface(self._model.get_level().get_dimensions())

        
                
    def _handle_keypress(self, e: tk.Event) -> None:
        if e.char in (UP, DOWN, RIGHT, LEFT):
            super()._handle_move(e.char)
            if self._model.did_level_up():
                self._GI.set_maze_dimensions(self._model.get_current_maze().get_dimensions())
            if self._model.has_won():
                #self._GI.unbind()
                tk.messagebox.showinfo(title=None, message=WIN_MESSAGE)
                
                
            elif self._model.has_lost():
                tk.messagebox.showinfo(title=None, message=LOSS_MESSAGE)
                
            if not self._model.has_won() and not self._model.has_lost():
                self._GI.clear_all()
                self._GI.draw(self._model.get_current_maze(), self._model.get_current_items(), self._model.get_player().get_position(), self._model.get_player_inventory(), self._model.get_player_stats())
            
            
    def _apply_item(self, item_name: str) -> None:
        super()._handle_move("i {}".format(item_name))
        self._GI.draw(self._model.get_current_maze(), self._model.get_current_items(), self._model.get_player().get_position(), self._model.get_player_inventory(), self._model.get_player_stats())


    def play(self) -> None:
        self._GI.draw(self._model.get_current_maze(), self._model.get_current_items(), self._model.get_player().get_position(), self._model.get_player_inventory(), self._model.get_player_stats())

        self._GI.bind_keypress(self._handle_keypress)
        self._GI.set_inventory_callback(self._apply_item)
        
class ImageLevelView(LevelView):

    def draw(self, tiles: list[list[Tile]], items: dict[tuple[int, int], Item], player_pos: tuple[int, int]) -> None:

        self._images = list()
        row_counter = 0
        for row in tiles:
            col_counter = 0
            for tile in row:
                bbox = self.get_bbox((row_counter, col_counter))
                height = bbox[3] - bbox[1]

                self.set_images(tile.get_id(), height, (row_counter, col_counter))

                col_counter += 1

            row_counter += 1

        for key in items:
            bbox = self.get_bbox(key)
            height = bbox[3] - bbox[1]

            self.set_images(items[key].get_id(), height, key)

        bbox = self.get_bbox(player_pos)
        self.set_images(PLAYER, height, player_pos)

    def  set_images(self, ID: str, height: int, pos: tuple[int, int]) -> None:
        midpoints = self.get_midpoint((pos))

        if ID in TILE_COLOURS.keys():
            image = Image.open('images/' + TILE_IMAGES[ID])
        else:
            image = Image.open('images/' + ENTITY_IMAGES[ID])

        image = image.resize((height, height))
        self._photoimg = ImageTk.PhotoImage(image)
        self._images.append(self._photoimg)
        self.create_image(midpoints[0], midpoints[1], image =self._photoimg)

class ControlsFrame(tk.Frame):

    def __init__(self, master: Union[tk.Tk, tk.Frame], **kwargs) -> None:
        super().__init__(master, width = MAZE_WIDTH + INVENTORY_WIDTH, **kwargs)
        self._current_time = 0
        self._time_label = tk.Label(self, text="0m 0s", font=TEXT_FONT)
        self._restart_button = tk.Button(self, text = "Restart game", command = self.restart_button, font=TEXT_FONT)
        self._new_game_button = tk.Button(self, text = "New game", font=TEXT_FONT)


        self._restart_button.pack(side = tk.LEFT, padx = 100)
        self._new_game_button.pack(side = tk.LEFT, padx = 100)
        self._time_label.pack(side = tk.LEFT, padx = 100)
        
        self.update_clock()
        

    def restart_button(self) -> None:
        destroy_window()
        main()

    def new_game_button(self) -> None:
        pass

    def update_clock(self) -> None:
        self._current_time += 1
        self.display_clock()
        self.after(1000, self.update_clock)

    def display_clock(self) -> None:
        minutes = self._current_time // 60
        seconds = self._current_time % 60
        timer = str(minutes) +'m ' + str(seconds) + 's'
        self._time_label.configure(text = timer)


def destroy_window():
    root.destroy()

def play_game(root: tk.Tk):
    game = GraphicalMazeRunner(GAME_FILE, root)
    game.play()
    root.mainloop()

def main():   
    root = tk.Tk()
    play_game(root)

def main2():
    root = tk.Tk()
##    ILevelView = ImageLevelView(root, (5,5), (MAZE_WIDTH, MAZE_HEIGHT))
##    ILevelView.draw([[Wall(), Wall(), Wall(), Wall(), Wall()],
##                     [Wall(), Empty(), Empty(), Empty(), Door()],
##                     [Wall(), Empty(), Empty(), Empty(), Wall()],
##                     [Empty(), Empty(), Empty(), Empty(), Wall()],
##                     [Wall(), Wall(), Wall(), Wall(), Wall()]],
##                    {(1, 2): Coin((1, 2)), (2, 2): Coin((2, 2)), (3, 2): Coin((3, 2)), (2, 3): Potion((2, 3))}, (3, 0))
##    ILevelView.pack()
    control = ControlsFrame(root)
    control.pack()
    

if __name__ == '__main__':
    #main2()
    main()
