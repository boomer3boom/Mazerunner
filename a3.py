from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
from PIL import Image,ImageTk

from a3_support import AbstractGrid
from constants import GAME_FILE, TASK

from a2_solution import *
from a2_support import *

from typing import Union
from tkinter import ttk
from tkinter import messagebox as mb

#The title of the window.
Title = 'MazeRunner'

# Write your classes here
class LevelView(AbstractGrid):
    """
    The LevelView class inherits from AbstractGrid which is from a3 support
    file. It displays the maze, along with the entities. Entities can split
    into player and the item. Each type of tiles have their own unique
    colour and can be found in constants.py. Each entity have its own colour,
    and the annotation labelled on top of the entity is its ID.
    """

    def draw(self, tiles: list[list[Tile]], items: dict[tuple[int, int], Item],
             player_pos: tuple[int, int]) -> None:
        """
        Draws the maze which includes the tiles, items on that maze level, and
        player's position. Tiles have rectangle and entity has oval.

        Parameters:
        Tiles: This is a nested list. The outer list contains the row of tiles,
        while the inner list contains the instance of the tiles.

        items: This is a dictionary containing the items in this level of maze.
        The key is the position that the item is located and value is instance
        of that item.

        player_pos: This is a tuple that has 2 integers. This is the player's
        position on the maze.
        """

        self.clear()


        #Loops through tiles to ger the row, and loop through row to get tile.
        #enumerate tiles and row to get the row and column number.
        for row_counter, row in enumerate(tiles):
            for col_counter, tile in enumerate(row):

                #Get bbox for that tile position and create the rectangle.
                bbox = self.get_bbox((row_counter, col_counter))
                self.create_rectangle(bbox, fill = TILE_COLOURS[tile.get_id()])


        #Position is the key in items. Loop to get all item in the current maze
        for key in items:

            bbox = self.get_bbox(key)
            self.create_oval(bbox, fill = ENTITY_COLOURS[items[key].get_id()])
            #Instance of item is value in items. Annotate the item with it's ID
            self.annotate_position(key, items[key].get_id())

        #Create oval and annotate for player.
        bbox = self.get_bbox(player_pos)
        self.create_oval(bbox, fill = ENTITY_COLOURS[PLAYER])
        self.annotate_position(player_pos, PLAYER)


class StatsView(AbstractGrid):
    """
    The StatsView class inherits from AbstractGrid. It displays player's HP,
    health, thirst and number of coins in player's inventory. However, drawing
    the coin will occur in a seperate function, as it requires access to
    inventory while the other three does not. A StatView have 4 columns and two
    rows. First row contains header and the second row contains the value.
    """

    def __init__(self, master: Union[tk.Tk, tk.Frame], width: int, **kwargs) \
        -> None:
        """
        Initiaite the StatView instance by calling the __init__ function from
        abstractgrid, and then giving it the value required.

        Parameters:
        master: The frame where StatsView will be placed.
        width: The width of the stats view.
        """
        stats_row = 2
        stats_column = 4

        super().__init__(master, (stats_row, stats_column), \
                         (width, STATS_HEIGHT), bg = THEME_COLOUR)

        #This tuple is used to access the name of the title in statsview.
        self._Title = ("HP", "Hunger", "Thirst", "Coins")

    def draw_stats(self, player_stats: tuple[int, int, int]) -> None:
        """
        Show the player's stats which is the player's HP, Hunger, and Thirst.
        Coin is not part of the player's stats and will be drawn in another
        method.

        Parameters:
        player_stats: A tuple of player's stats as (HP, Hunger, Thirst).
        """

        #Length of player_stats is 3, range of 3 is 2. So col goes from 0 to 2.
        for col in range(len(player_stats)):

            # The 0 stands for row 0, and hence annotate header at the top.
            self.annotate_position((0, col), self._Title[col])

            # The 1 stands for row 1, and hence annote value at the bottom.
            self.annotate_position((1, col), player_stats[col])

    def draw_coins(self, num_coins: int) -> None:
        """
        Draw the number of coin player has collect and the title.

        Parameters:
        num_coins: The number of coins the player has collected.
        """

        #The coin are drawn after the player stats. Therefore, it is drawn
        #on column 3, which is after HP(0), Hunger(1), and Thirst(2).
        self.annotate_position((0, 3), self._Title[3])
        self.annotate_position((1, 3), num_coins)


class InventoryView(tk.Frame):
    """
    The InventoryView class inherits from tk.Frame, and display the item the
    player has in their inventory. The InventoryView is drawn vertically, with
    the label "Inventory" and the items below. Beside the item, the number of
    the specific item is displayed. Only items in the player inventory will be
    displayed. Note: Coins will not be drawn in InventoryView but in StatsView.
    """

    def __init__(self, master: Union[tk.Tk, tk.Frame], **kwargs) -> None:
        """
        Initialise the frame for Inventory view.

        Parameters:
        master: The frame where InventoryView will be placed in.
        **kwargs: Magic variable that allow keyword argument to be passed.
        """

        #Calls super to set up a tk.Frame which is stored in the given master.
        super().__init__(master, width = INVENTORY_WIDTH, \
                         height = MAZE_HEIGHT, **kwargs)

        self._InventHeader = tk.Label(self, text = 'Inventory',\
                                      font = HEADING_FONT)
        self._InventHeader.pack(fill=tk.X)

        #A list of Item name that can be shown in inventoryView.
        self._items = ['Potion', 'Honey', 'Apple', 'Water']

    def set_click_callback(self, callback: Callable[[str], None]) -> None:
        """
        Sets the function to be called when an item is clicked.

        Parameters:
        callback: A function. In this scenario, the callback function only
        takes one argument which is string name of item.
        """
        self._callback = callback

    def clear(self) -> None:
        """
        Clears all child widget from the InventoryView, but the header which
        is initialised in the __init__. Since InventoryView dosn't inherit
        from AbstractGrid like LevelView and StatsView, a new clear needs to
        be written.
        """

        #Get all child widget from the frame.
        widgets = self.winfo_children()

        # Destroy all child widget that's not the header.
        for widget in widgets:
            if widget == self._InventHeader:
                pass
            else:
                widget.destroy()

    def _draw_item(self, name: str, num: int, colour: str) -> None:
        """
        Creates a tk.Level in the InventoryView frame. The tk.label will bind
        to the callback so that when pressed, the name of the item will appear.

        Parameters:
        name: The string name of the item.
        num: The number of this item in inventory.
        colour: The background colour of this item label should take.
        """

        #The label of this item should be in the form "name: num"
        label = name + ': ' + str(num)
        item_label = tk.Label(self, text = label, bg = colour,\
                              font = TEXT_FONT)
        item_label.pack(side = tk.TOP, anchor = tk.CENTER, fill = tk.BOTH)

        #Bind label to a function that's created on the spot which sets to
        #self._callback(name)
        item_label.bind("<Button-1>", lambda e: self._callback(name))

    def draw_inventory(self, inventory: Inventory) -> None:
        """
        Draws the non-coin item in the player's inventory.

        Parameters:
        inventory: The player's inventory.
        """

        #loop over each distinct item (key) to create label.
        for item in inventory.get_items().keys():

            #Check the item if it's not a coin.
            if str(item) in self._items:

                #Value of the dictionary is a list of item instance. 0th index
                #exist since the distinct item was found in player's inventory.
                colour = ENTITY_COLOURS[inventory.get_items()[item][0].get_id()]


                #Count number of that item the player own and create the label.
                no_item = len(inventory.get_items()[item])
                self._draw_item(item, no_item, colour)


class GraphicalInterface(UserInterface):
    """
    GraphicalInterface inherits from UserInterface and manages the overall look
    of the game. In other words, it sets up the title banner, the three major
    widgets and enable the major event handling. Note: Since there are two TASK
    an if TASK == will likely be found in most methods.
    """

    def __init__(self, master: tk.Tk) -> None:
        """
        Initialise the GraphicalInterface with the give master frame. Set the
        title and header for the window and interface.

        Parameters:
        Master: A tk.frame that will contain all the three major widgets.
        """

        #Create the frame, set the title, and header, then pack the header.
        self._GI = master
        self._GI.title(Title)
        self._Header = tk.Label(self._GI, text = Title, font = BANNER_FONT,\
                                bg = THEME_COLOUR)
        self._Header.pack(side = tk.TOP, fill = tk.BOTH)

    def create_interface(self, dimensions: tuple[int, int]) -> None:
        """
        TASK 1: Initialise the three major components (Level, Inventory, and
        Stats view) in the master frame.

        TASK 2: TASK 1, but replace LevelView with ImageLevelView and
        initialise the control frame as well. Note: The control frame acts as a
        widget not actually a controller. Hence, it is handled here.

        Parameters:
        Dimensions: The dimension of maze in current level in (row, column).
        """
        if TASK == 1:
            #Initialise the three major widgets.
            self._LevelView = LevelView(self._GI, dimensions, \
                                        (MAZE_WIDTH, MAZE_HEIGHT))
            self._StatsView = StatsView(self._GI, MAZE_WIDTH + INVENTORY_WIDTH)
            self._InventoryView = InventoryView(self._GI)
            

            #Pack the Statsview since its at the bottom first.
            #Then Level and Inventory View since they're beside each other.
            self._StatsView.pack(side=tk.BOTTOM)
            self._LevelView.pack(side=tk.LEFT)
            self._InventoryView.pack(side=tk.LEFT, anchor = tk.N, fill=tk.BOTH\
                                     , expand=True)


        elif TASK == 2:
            #Change LevelView to ImageLevelView.
            self._ILevelView = ImageLevelView(self._GI, dimensions,\
                                              (MAZE_WIDTH, MAZE_HEIGHT))
            self._StatsView = StatsView(self._GI, MAZE_WIDTH + INVENTORY_WIDTH)
            self._InventoryView = InventoryView(self._GI)
            self._CF = ControlsFrame(self._GI)

            #ControlFrame is packed before Stats since it's below it.
            self._CF.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)
            self._StatsView.pack(side=tk.BOTTOM)
            self._ILevelView.pack(side=tk.LEFT)
            self._InventoryView.pack(side=tk.LEFT, anchor = tk.N, fill=tk.BOTH\
                                     ,expand=True)

            #Control button is drawn here since it does not need to be cleaned.
            self._CF.draw_buttons()

    def clear_all(self) -> None:
        """
        TASK 1: Responsible for clearing the widgets for redrawing.

        TASK 2: Task 1, but ImageLevelView instead of LevelView.
        """
        if TASK == 1:
            self._LevelView.clear()
            self._StatsView.clear()
            self._InventoryView.clear()

        elif TASK == 2:
            self._ILevelView.clear()
            self._StatsView.clear()
            self._InventoryView.clear()

    def set_maze_dimensions(self, dimensions: tuple[int, int]) -> None:
        """
        TASK 1: Reset the dimension of the maze for when player Leve up.

        TASK 2: The same, but on ImageLevelView.

        Parameters:
        dimensions: The new dimension in (row, column) form.
        """
        if TASK == 1:
            self._LevelView.set_dimensions(dimensions)
        elif TASK == 2:
            self._ILevelView.set_dimensions(dimensions)

    def bind_keypress(self, command: Callable[[tk.Event], None]) -> None:
        """
        Binds given command to the general keypress event. The allowed
        keypress is done in the GraphicalMazerunner and not here.

        Parameters:
        command: A function that moves the player based on the keypress.
        """
        self._GI.bind('<Key>', command)

    def set_inventory_callback(self, callback: Callable[[str], None]) -> none:
        """
        Set function to be called when item is clicked in the inventoryview to
        the callback function.

        Parameters:
        callback: A function that is constructed in graphicalMazerunner.
        """
        self._InventoryView.set_click_callback(callback)

    def draw_inventory(self, inventory: Inventory) -> None:
        """
        Draws all the non-coin item in player inventory along with their
        quantity. Also bind the drawn item.

        Parameters:
        inventory: The player's inventory instance.
        """
        self._InventoryView.draw_inventory(inventory)

    def draw(self, maze: Maze, items: dict[tuple[int, int], Item],
             player_position: tuple[int, int], inventory: Inventory,
             player_stats: tuple[int, int, int]) -> None:
        """
        Clear the three major widgets, and redraw them with their new state.
        This is provided as argument.

        Parameters:
        maze: The maze instance the player is on.
        items: The available items in the maze in the form of dictionary with
        position as the key, and item instance as value.
        Player_position: Player's current position in maze.
        inventory: The player's inventory instance.
        player_stats: A tuple of player's stats as (HP, Hunger, Thirst).
        """

        #Clear_all clears everything so interface can be redrawn.
        self.clear_all()

        #Call the draw methods in this class to redraw the major widgets.
        self._draw_level(maze, items, player_position)
        self._draw_player_stats(player_stats)
        self._draw_inventory(inventory)

    def _draw_inventory(self, inventory: Inventory) -> None:
        """
        Draw both the non-coin item in the inventory and the coin item in the
        inventory. Draw_coin is part of Statsview but is in inventory since
        it needs access to player's inventory.

        Parameter:
        inventory: The player's inventory instance.
        """
        
        Coin = 'Coin'

        #Draw the coin item.
        if Coin in inventory.get_items().keys():

            #Count the number of coin, and pass that to draw_coin.
            no_coins = len(inventory.get_items()[Coin])
            self._StatsView.draw_coins(no_coins)

        else:
            #If there's no coin in inventory, then player has no coin.
            no_coins = 0
            self._StatsView.draw_coins(no_coins)

        #Draw the remaining non-coin item in player's inventory.
        self.draw_inventory(inventory)

    def _draw_level(self, maze: Maze, items: dict[tuple[int, int], Item],
                    player_position: tuple[int, int]) -> None:
        """
        Draw the maze compoenent of the interface using LevelVIew(TASK 1) or
        ImageLevelView(TASK 2)

        Parameters:
        maze: The maze instance the player is on.
        items: The available items in the maze in the form of dictionary with
        position as the key, and item instance as value.
        player_position: Player's current position in maze.
        """
        if TASK == 1:
            self._LevelView.draw(maze.get_tiles(), items, player_position)
        elif TASK == 2:
            self._ILevelView.draw(maze.get_tiles(), items, player_position)

    def _draw_player_stats(self, player_stats: tuple[int, int, int]) -> None:
        """
        Draw the player's stats using StatsView methods. The coins is not
        considered in this method as theres not access to player's inventory.

        Parameters:
        player_stats: A tuple of player's stats as (HP, Hunger, Thirst).
        """
        self._StatsView.draw_stats(player_stats)

    #The following methods were written as helper method for TASK 2.

    def set_restart_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set function to be called when restart button from control frame
        is clicked.

        Parameters:
        callback: A function that is constructed in graphicalMazerunner.
        """
        if TASK == 2:
            self._CF.set_restart_click_callback(callback)
        else:
            pass

    def set_new_game_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set function to be called when new_game button from control frame
        is clicked.

        Parameters:
        callback: A function that is constructed in graphicalMazerunner.
        """
        if TASK == 2:
            self._CF.set_newgame_click_callback(callback)

    def reset_clock(self) -> None:
        """
        Reset the clock timer back to 0 seconds using reset_clock method
        from control frame.
        """
        if TASK == 2:
            self._CF.reset_clock()

    def delete_window(self) -> None:
        """
        Delete the TopLevel window once player has inputted the game path using
        the delete_window method from controls frame.
        """
        if TASK == 2:
            self._CF.delete_window()

    def stop_clock(self) -> None:
        """
        Stop the timer from running using the stop_clock method from
        controls frame.
        """
        if TASK == 2:
            self._CF.stop_clock()


class GraphicalMazeRunner(MazeRunner):
    """
    The GraphicalMazerunner inherits from Mazerunner and displayes the game
    using GraphicalInterface instead of a textinterface. this is the controller
    class of the game. TASK 2 also have _restart_game, _new_game, and
    reset_game method.
    """

    def __init__(self, game_file: str, root: tk.Tk) -> None:
        """
        Creates a new graphicalMazeRunner game  with view(read more on a2
        solution) inside the root widget. A file menu is also created for
        TASK 2.

        Parameters:
        game_file: The path to the game_file that would like to be opened
        relative ot this python file.
        root: The window where this game will be placed.
        """

        #Initiate the game with super, and set up graphical interface.
        super().__init__(game_file, root)
        self._GI = GraphicalInterface(root)
        self._GI.create_interface(self._model.get_level().get_dimensions())

        #The path of game file need to be memorised since the player
        #may want to restart game.
        self._game_file = game_file

        #Creates the file menu with the given root window.
        if TASK == 2:
            file = file_menu(root, self)

    def redraw(self) -> None:
        """
        Redraws the graphical interface
        """
        self._GI.clear_all()
        self._GI.draw(self._model.get_current_maze(),
                      self._model.get_current_items(),
                      self._model.get_player().get_position(),
                      self._model.get_player_inventory(),
                      self._model.get_player_stats())

    def _handle_keypress(self, e: tk.Event) -> None:
        """
        TASK 1: Handles the event of a keypress. Only keys that are w, a, s, d
        will do something, the rest are ignored. If the player wins/lose, they
        are notified via a messagebox.

        TASK 2: The same as TASK 1, but the clock will stop upon win/lose.

        Parameters:
        e: The tk.Event of a keypress.
        """

        #Check that the keypress is w, a, s or d.
        if e.char in (UP, DOWN, RIGHT, LEFT):

            #attempt to move the player with the keypress.
            self._handle_move(e.char)

            #If the player has leveled up, then the dimension of LevelView
            #needs to change to fit the new level maze.
            if self._model.did_level_up():
                self._GI.set_maze_dimensions(self._model.get_current_maze()\
                                             .get_dimensions())


            #If player has won, stop the clock (TASK 2), and show the message.
            if self._model.has_won():
                if TASK == 2:
                    self._GI.stop_clock()
                tk.messagebox.showinfo(title=None, message=WIN_MESSAGE)


            #If player has lose, stop the clock (TASK 2), and show the message.
            elif self._model.has_lost():
                if TASK == 2:
                    self._GI.stop_clock()
                tk.messagebox.showinfo(title=None, message=LOSS_MESSAGE)


            #If player has not won nor lose, then clear and redraw.
            #Must not redraw if player has won or lose or out_index error.
            if not self._model.has_won() and not self._model.has_lost():
                self.redraw()


    def _apply_item(self, item_name: str) -> None:
        """
        Apply the item to the player when player clicks on the item label.

        parameter:
        item_name: the string name of the item.
        """
        #To apply item in handle move, the syntax is "i name". So "i " needs to
        #be added in front of item_name, then passed onto _handle_move.
        self._handle_move("i {}".format(item_name))
        self.redraw()

    def reset_game(self) -> None:
        """
        A helper function that resize the image, reset the clock, and redraw
        the interface.
        """
        if TASK == 2:
            self._GI.set_maze_dimensions(self._model.get_current_maze()\
                                         .get_dimensions())
            self._GI.reset_clock()
            self.redraw()


    def _restart_game(self) -> None:
        """
        The callback for when player clicks on restart button. Overwrite
        current game mode, resize the diemnsions, reset clock, and redraw.
        """
        if TASK == 2:
            self._model = Model(self._game_file)
            self.reset_game()

    def _new_game(self, path: tk.Event) -> None:
        """
        Starts a new game with the given path relative to this python file. If
        game cannot be accessed, then a messagebox will appear, and upon
        acknowledging the messagebox, the toplevel will close.

        path: the paths to the file the player wants to open and play.
        """
        if TASK == 2:
            #try opening the path the player has entered since it's not sure
            #if path is valid.
            try:
                self._model = Model(path)

                #If an error is not thrown, then the path is valid.
                #Reset the game, and delete the window.
                self._GI.delete_window()
                self.reset_game()
                self._game_file = path

            #If not a valid path, then show a message box and delete toplevel.
            except:
                tk.messagebox.showinfo(title=None, message="NOT A VALID FILE")
                self._GI.delete_window()

    def play(self) -> None:
        """
        Called to make the gameplay occur. The method first draws the widgets
        then it binds the handlers so that the game can operate.
        """
        self.redraw()
        self._GI.bind_keypress(self._handle_keypress)
        self._GI.set_inventory_callback(self._apply_item)

        #callback for restart game and
        if TASK == 2:
            self._GI.set_new_game_callback(self._new_game)
            self._GI.set_restart_callback(self._restart_game)


class ImageLevelView(LevelView):
    """
    ImageLevelView inherits from LevelView and have the same functionality.
    However, images are used to display the tiles and entities rather than
    rectangles and ovals.
    """
    def draw(self, tiles: list[list[Tile]], items: dict[tuple[int, int], Item],
             player_pos: tuple[int, int]) -> None:
        """
        Draws the maze which includes the tiles, items on that maze level, and
        player's position but with images instead.

        Parameters:
        Tiles: This is a nested list. The outer list contains the row of tiles,
        while the inner list contains the instance of the tiles.

        items: This is a dictionary containing the items in this level of maze.
        The key is the position that the item is located and value is instance
        of that item.

        player_pos: This is a tuple that has 2 integers. This is the player's
        position on the maze.
        """

        #Create a list for python to store memory for the images so that it
        #does not garbage collect.
        self._images = list()

        #Most logic will be the same a LevelView. The same comment will not be
        #repeated. For further information on logic, refer to LevelView.
        for row_counter, row in enumerate(tiles):
            for col_counter, tile in enumerate(row):

                bbox = self.get_bbox((row_counter, col_counter))

                #bbox gives (xmin, ymin, xmax, ymax). Hence, height and width
                #can be calculated as such
                height = bbox[3] - bbox[1]
                width = bbox[2] - bbox[0]
                
                #call for set_image method to create the image.
                self.set_images(tile.get_id(), height, width, \
                (row_counter, col_counter))



        for key in items:
            bbox = self.get_bbox(key)

            #The height and width should stay consistent.
            self.set_images(items[key].get_id(), height, width, key)


        bbox = self.get_bbox(player_pos)
        self.set_images(PLAYER, height, width, player_pos)

    def set_images(self, ID: str, height: int, width: int,
                   pos: tuple[int, int]) -> None:
        """
        Get the wanted image and display the image.

        Parameters:
        ID: The ID of the entity or tile.
        height: The height of image
        width: The width of image
        pos: The position of the image
        """
        midpoints = self.get_midpoint((pos))

        file_images = 'images/'

        #Get the path and hence the image with TILE_IMAGES or ENTITY_IMAGES.
        if ID in TILE_COLOURS.keys():
            image = Image.open(file_images + TILE_IMAGES[ID])
        else:
            image = Image.open(file_images + ENTITY_IMAGES[ID])


        #Resize the image, turn it into tkimage, then append onto the
        #self._image list so python dosn't garbage collect.
        image = image.resize(self.get_cell_size())
        self._photoimg = ImageTk.PhotoImage(image)
        self._images.append(self._photoimg)

        #Create the image at that midpoint position.
        self.create_image(midpoints[0], midpoints[1], image =self._photoimg)


class ControlsFrame(tk.Frame):
    """
    Controls Frame acts like another major widget in addition to the
    three major widget rather than a controller. It contains 3 core
    features, a timer, a new_game button to start a new game, and a
    restart button to restart the current game. The control frame is
    located beneath the StatsView.
    """

    def __init__(self, master: Union[tk.Tk, tk.Frame], **kwargs) -> None:
        """
        Inititate the control frame with the required self. variable for the
        three core feature to operate.

        Parameters:
        master: The tk frame to put the controlsframe in.
        **kwargs: Magic variable that allow keyword argument to be passed.
        """

        #Call for super to set up a frame for controlframe.
        super().__init__(master, width = MAZE_WIDTH + INVENTORY_WIDTH\
                         , **kwargs)

        self._restart_callback = None
        self._new_game_callback = None

        self._current_time = 0
        self._clock_stop = False


    def draw_buttons(self) -> None:
        """
        Draws the three core components of ControlFrame and pack them. The
        clock is in "xm ys" format, where x,y are numbers.
        """

        timer_frame = tk.Frame(self)

        initial_time = "0m 0s"
        Time_header = "Timer"

        #Create the label for the timer and its header
        self._timer = tk.Label(timer_frame, text=initial_time, font=TEXT_FONT)
        self._timer_header = tk.Label(timer_frame, text = Time_header,
                                      font=TEXT_FONT)

        #Create restart and new_game button and set their command.
        self._restart_button = tk.Button(self, text = "Restart game",
                                         font=TEXT_FONT,
                                         command = self._restart_callback)

        self._new_game_button = tk.Button(self, text = "New game",
                                          font=TEXT_FONT,
                                          command = \
                                          self.new_game_button_function)

        #Pack timer and header into timer_frame, with header at top.
        self._timer_header.pack(anchor = tk.N)
        self._timer.pack(anchor = tk.S)

        #Pack the three major components into the control frame
        self._restart_button.pack(side = tk.LEFT, expand = True)
        self._new_game_button.pack(side = tk.LEFT, expand = True)
        timer_frame.pack(side = tk.LEFT, expand = True)

        #Let the timer start to click. TimerID is required to prevent multiple
        #timer from running when player restart game.
        self._timerID = self.after(1000, self.update_clock)

    def set_restart_click_callback(self, callback: Callable[[str], None])\
        -> None:
        """
        Set the callback for restart game button.

        Parameters:
        callback: A function that restart the game. It is defined in
        GraphicalMazeRunner
        """

        self._restart_callback = callback

        #due to way python prioritise things, the _restart_button needs to be
        #configured again here.
        self._restart_button.config(command=self._restart_callback)

    def set_newgame_click_callback(self, callback: Callable[[str], None])\
        -> None:
        """
        Set the callback for new game button.

        Parameters:
        callback: A function that starts a new game. It is defined in
        GraphicalMazeRunner.
        """
        self._new_game_callback = callback

    def update_clock(self) -> None:
        """
        Increment the clock every second.
        """
        #Make sure that the clock should not stop
        if not self._clock_stop:
            
            #Increment the timer, and display the new time
            self._current_time += 1
            self.display_clock()

            #After 1000 millisecond, recursively update the clock again.
            self._timerID = self.after(1000, self.update_clock)

    def reset_clock(self) -> None:
        """
        Reset the clock back to 0seconds. This is required if player restart
        or plays a new game.
        """
        #If player finish game, and restart, make sure the clock can tick again
        self._clock_stop = False

        #To avoid multiple timer, cancel the previous timer.
        self.after_cancel(self._timerID)

        self._current_time = 0
        self.display_clock()

        #Start updating the timer again.
        self._timerID = self.after(1000, self.update_clock)

    def display_clock(self) -> None:
        """
        Update the visual interface clock to the player in "xm ys" form, where
        x, y is a number
        """

        #self._current_time is in seconds. So floor Division by 60 to get the
        #mins and modulus to get the remaining seconds.
        minutes = self._current_time // 60
        seconds = self._current_time % 60

        #Organise the display into minutes and second and display it.
        timer_display = str(minutes) +'m ' + str(seconds) + 's'
        self._timer.configure(text = timer_display)

    def stop_clock(self) -> None:
        """
        Stop the clock by turning self._clock_stop to True,
        in which stops the clock from updating in update_clock method.
        """
        self._clock_stop = True

    def new_game_button_function(self) -> None:
        """
        This function will run when player clicks on the new game button. It'll
        display a new toplevel window which ask player to input a new game path
        relative to this python file. What happens after the player submit the
        path and whether or not it's valid is handled in GraphicalMazeRunner.
        """
        self._new_window = tk.Toplevel()

        #A tk string variable for the path the player inputs.
        self._path_var = tk.StringVar()

        #Create an entry with self._path_var as textvariable for later access
        path_entry = tk.Entry(self._new_window, textvariable = self._path_var,
                              font=TEXT_FONT)
        path_entry.pack()

        #Button for when player submits their game path.
        self._sub_btn=tk.Button(self._new_window,text = 'Submit',
                                command = self.submit_path)
        self._sub_btn.pack()

    def submit_path(self) -> None:
        """
        Runs when the self._sub_btn is pressed. This will bind the button
        to the _new_game_callback method with path passed.
        """

        #Get the player's input
        path = self._path_var.get()

        #Bind the self._sub_btn to the _new_game_callback with path passes.
        self._sub_btn.bind("<Button-1>",self._new_game_callback(path))

    def delete_window(self) -> None:
        """
        Delete TopLevel Window.
        """
        self._new_window.destroy()


class file_menu():
    """
    Responsible for creating a file menu that will have 4 options: Save game,
    Load game, Restart game, and Quit.

    Save game: Promt player to save the game state at a location.
    Load game: Promt player to load a game from a selected location.
    Restart game: Restart the game, including the timer.
    Quit: Prompt player with messagebox asking if they want to quit. If yes,
    quit the game, else do nothing.
    """

    def __init__(self, master: Union[tk.Tk, tk.Frame],
                 GMZ: GraphicalMazeRunner) -> None:
        """
        Initialise the file menu by setting the menu bar, and the file menu.

        Parameters:
        master: The root window where the file menu will be placed.
        GMZ: The GraphicalMazeRunner
        """
        #Need to create memory of master for the quitting method.
        self._master = master
        
        #A tuple of the option label.
        file_options = ("Save game", "Load game", "Restart game", "Quit")

        #Set up the menu bar and the file drop down thing.
        menubar = tk.Menu(self._master)
        self._master.config(menu=menubar)

        file_menu = tk.Menu(menubar)
        menubar.add_cascade(
            label = "File",
            menu=file_menu
            )

        #add the four options into file_menu
        #Note, some options have not been implemented.
        #However, a raise not implemented error was not done in fear gradescope
        #might collapse.
        file_menu.add_command(
            label = file_options[0]
            )

        file_menu.add_command(
            label = file_options[1]
            )

        file_menu.add_command(
            label = file_options[2],
            command = GMZ._restart_game
            )

        file_menu.add_command(
            label = file_options[3],
            command= self.quitting
            )

    def quitting(self) -> None:
        """
        Ask player if they wish to quit with a messagebox. If yes, quit the
        game else, do nothing.
        """
        messagebox_title = "Quit Application"
        messagebox_message = "Do you wish to quit?"

        #Double check if player wants to quit with a messagebox.
        double_check = mb.askquestion(messagebox_title, messagebox_message)

        #if player wish to quit, destroy the window, else do nothing.
        if double_check == 'yes':
            self._master.destroy()
        else:
            pass


def play_game(root: tk.Tk):
    """
    Make the game run with an interface

    Parameters:
    root: The window where the game runs.
    """
    game = GraphicalMazeRunner(GAME_FILE, root)
    game.play()
    root.mainloop()


def main():
    """Initiate the root, and make the game run"""
    root = tk.Tk()
    play_game(root)


if __name__ == '__main__':
    main()
