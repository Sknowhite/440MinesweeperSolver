import random
import minesweeper_csp
from FieldButton import *
from cspbase import *
from propagators import *


class Minesweeper:
    """Minesweeper Class:
        The game board is a list of lists:

        [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

        such that board[i][i] is the FieldButton (object) that built to represent
        the button in cell i,j of the game board. (by default indexed from (0,0) to (10,10))"""

    def __init__(self, master):

        self.frame = Frame(master)
        self.frame.pack()

        # Number of games played and won
        self.game_times = 0
        self.win_times = 0

        # Board: 10x10 with 10 mines
        self.row_size = 10
        self.col_size = 10
        self.mines_amount = 10
        self.remaining_mines = self.mines_amount
        self.flags = 0
        self.is_over = False
        self.buttons = []
        self.mines = []
        self.board = []

        self.first_click = True
        self.first_click_button = None

        # Initialize images for newGame button.
        self.img_sun_normal = PhotoImage(file="images/img_sun_normal.gif")
        self.img_sun_normal_press = PhotoImage(file="images/img_sun_normal_press.gif")
        self.img_sun_move = PhotoImage(file="images/img_sun_move.gif")
        self.img_sun_win = PhotoImage(file="images/img_sun_win.gif")
        self.img_sun_lose = PhotoImage(file="images/img_sun_lose.gif")

        # Initialize images for cell button.
        self.images = {'blank': PhotoImage(file="images/img_blank.gif"), 'mine': PhotoImage(file="images/img_mine.gif"),
                       'hit_mine': PhotoImage(file="images/img_hit_mine.gif"),
                       'flag': PhotoImage(file="images/img_flag.gif"),
                       'wrong': PhotoImage(file="images/img_wrong_mine.gif"), 'no': []}

        for i in range(0, 9):
            self.images['no'].append(PhotoImage(file="images/img_" + str(i) + ".gif"))

        # Read test boards if it's not empty
        if not board:
            self.init_board()
            # self.init_random_mines()

        else:
            self.import_board(board)

        # Initialize newGame button.
        self.newGameButton = Button(self.frame, image=self.img_sun_normal)
        self.newGameButton.grid(row=0, column=0, columnspan=self.col_size)
        self.newGameButton.bind("<Button-1>", lambda Button: self.newGame())

        # Initialize remaining mines labels.
        self.remain_label = Label(self.frame, text="remaining mines: ")
        self.remain_label.grid(row=self.row_size + 1, column=0, columnspan=4, sticky=W)
        self.remain_label2 = Label(self.frame, text=self.mines_amount)
        self.remain_label2.grid(row=self.row_size + 1, column=4, columnspan=self.row_size, sticky=W)

        # Initialize solve by step button.
        self.solveButton = Button(self.frame, text="Solve by Step")
        self.solveButton.grid(row=self.row_size + 2, column=0, columnspan=self.col_size, sticky=E)
        self.solveButton.bind("<Button-1>", lambda Button: self.solve_step())

        # Initialize solve complete button.
        self.solveButton = Button(self.frame, text="Solve Complete")
        self.solveButton.grid(row=self.row_size + 2, column=0, columnspan=self.col_size, sticky=W)
        self.solveButton.bind("<Button-1>", lambda Button: self.solve_complete())

        # Initialize test solve complete button.
        self.solveButton = Button(self.frame, text="Solve Complete x times")
        self.solveButton.grid(row=self.row_size + 3, column=0, columnspan=self.col_size, sticky=W)
        self.solveButton.bind("<Button-1>", lambda Button: self.solve_complete_multiple(1000))

    def newGame(self):
        """Initialize all attributes for new game."""
        self.game_times += 1
        self.first_click = True
        self.first_click_button = None
        self.is_over = False
        self.flags = 0
        self.remaining_mines = self.mines_amount
        self.mines = []

        # Reset all buttons.
        for button in self.buttons:
            button.reset()
            button.bind('<Button-1>', self.lmbWrapper(button))
            button.bind('<Button-3>', self.rmbWrapper(button))

        # Reset remaining mines label and newGame button.
        self.remain_label2.config(text=self.remaining_mines)
        self.newGameButton.config(image=self.img_sun_normal)

    def init_board(self):
        """Initialize game board with buttons.
        The board is a list of lists, inner lists' elements are FieldButton object.
        [[ ],
        [ ]]"""
        for row in range(self.row_size):
            lis = []
            for col in range(self.col_size):
                button = FieldButton(row, col, self.frame, self.images)

                # first row grid for new game button
                button.grid(row=row + 1, column=col)
                lis.append(button)
                self.buttons.append(button)
            self.board.append(lis)

        # Bind LMB and RMB actions to button.
        for button in self.buttons:
            button.bind('<Button-1>', self.lmbWrapper(button))
            button.bind('<Button-3>', self.rmbWrapper(button))

    def init_random_mines(self):
        """Initialize mines randomly."""
        mines = self.mines_amount
        while mines:
            buttons = self.get_surrounding_buttons(self.first_click_button.x, self.first_click_button.y)
            buttons.append(self.first_click_button)

            # flag to check if random coordinates matches the initial click's 9 grids
            match = True
            row = None
            col = None
            while match:
                row = random.choice(range(self.row_size))
                col = random.choice(range(self.col_size))
                match = False
                for b in buttons:
                    if (row == b.x) and (col == b.y):
                        match = True
                        break

            if self.board[row][col].place_mine():
                self.mines.append(self.board[row][col])
                self.update_surrounding_buttons(row, col, 1)
                mines -= 1

    def get_surrounding_buttons(self, row, col):
        """Return a list of surrounding buttons of button at row and col in board."""
        SURROUNDING = ((-1, -1), (-1, 0), (-1, 1),
                       (0, -1), (0, 1),
                       (1, -1), (1, 0), (1, 1))

        neighbours = []

        for pos in SURROUNDING:
            temp_row = row + pos[0]
            temp_col = col + pos[1]
            if 0 <= temp_row < self.row_size and 0 <= temp_col < self.col_size:
                neighbours.append(self.board[temp_row][temp_col])

        return neighbours

    def update_surrounding_buttons(self, row, col, value):
        """Update surrounding buttons' value adding given value."""
        cells = self.get_surrounding_buttons(row, col)
        for cell in cells:
            if not cell.is_mine():
                cell.value += value

    def lmbWrapper(self, button):
        return lambda Button: self.lmbClicked(button)

    def rmbWrapper(self, button):
        return lambda Button: self.rmbClicked(button)

    def lmbClicked(self, button):
        """Left click action on given button."""
        if self.first_click:
            self.first_click_button = button
            self.init_random_mines()
            self.first_click = False

        # Do nothing if it's visible or it's flagged.
        if button.is_show() or button.is_flag():
            return

        # Case0: hits a number button, show the button.
        button.show()

        # Case1: hits a mine, game over.
        if button.is_mine():
            button.show_hit_mine()
            self.newGameButton.config(image=self.img_sun_lose)
            self.gameOver()

        # Case2: hits an empty button, keep showing surrounding buttons until all not empty.
        elif button.value == 0:
            buttons = [button]
            while buttons:
                temp_button = buttons.pop()
                surrounding = self.get_surrounding_buttons(temp_button.x, temp_button.y)
                for neighbour in surrounding:
                    if not neighbour.is_show() and neighbour.value == 0:
                        buttons.append(neighbour)
                    neighbour.show()

        # Check whether the game wins or not.
        if self.is_win():
            self.gameOver()

    def rmbClicked(self, button):
        """Right click action on given button."""

        # Do nothing if it's visible.
        if button.is_show():
            return

        # Flag/Unflag a button.
        if button.is_flag():
            button.flag()
            self.flags -= 1
        else:
            button.flag()
            self.flags += 1

        # Update remaining mines label.
        self.remaining_mines = (self.mines_amount - self.flags) if self.flags < self.mines_amount else 0
        self.remain_label2.config(text=self.remaining_mines)

        if self.is_win():
            self.gameOver()

    def gameOver(self):
        """Disable all buttons and show all mines."""
        self.is_over = True
        for button in self.buttons:
            if button.is_mine():
                if not button.is_flag() and not self.is_win():
                    button.show()
            elif button.is_flag():
                button.show_wrong_flag()

            button.unbind('<Button-1>')
            button.unbind('<Button-3>')

    def is_win(self):
        """Return True if game wins; False otherwise. The game wins if all buttons are either visible or flagged, and
        the amount of flags equals the amount of mines."""
        for button in self.buttons:
            if not button.is_show() and not button.is_mine():
                return False
        self.newGameButton.config(image=self.img_sun_win)
        return True

    def solve_complete(self):
        """Solve current game completely."""
        if self.is_over:
            return

        # Unflag all buttons.
        for button in self.buttons:
            if button.is_flag():
                button.flag()
                self.flags -= 1
        while not self.is_over:
            assigned = self.solve_step()

            # No variable assigned by CSP.
            if not assigned:
                choose_button = self.guess_move()
                self.lmbClicked(choose_button)

    def solve_complete_multiple(self, times):
        self.win_times = 0
        self.game_times = 0
        print(
            "board size: {0}x{1}\nmines #: {2}\n{3}".format(self.row_size, self.col_size, self.mines_amount, "-" * 27))
        for i in range(times):
            self.solve_complete()
            if self.is_win():
                self.win_times += 1
            self.newGame()
            if (i + 1) % 100 == 0:
                print("solved: " + str(i + 1) + " times")

        print("-------Run results---------")
        print("Matches played: " + str(self.game_times))
        print("Wins: " + str(self.win_times))
        print("Win rate: " + str(self.win_times / self.game_times))
        self.win_times = 0
        self.game_times = 0

    def guess_move(self):
        """Return an unclick button."""
        buttons = []
        corners = [self.board[0][0], self.board[0][self.col_size - 1], self.board[self.row_size - 1][0],
                   self.board[self.row_size - 1][self.col_size - 1]]
        for button in self.buttons:
            if not button.is_show() and not button.is_flag():
                buttons.append(button)

        for button in corners:
            if not button.is_show() and not button.is_flag():
                return button

        return random.choice(buttons)

    def solve_step(self):
        """Solve parts of the game bases on current board's information by using CSP.
        Return the number of variables made."""
        is_assigned = False

        csp = minesweeper_csp.cspModel(self)

        solver = BT(csp)
        solver.backtrackingSearch(prop_BT)
        for var in csp.get_all_vars():

            # noinspection PyBroadException
            try:
                cell = var.name.split()
                row = int(cell[0])
                col = int(cell[1])
            except:
                # continue if it's not a variable in board.
                # in board variable name's format: row, col
                continue

            if var.get_assigned_value() == 1:
                if not self.board[row][col].is_flag():
                    self.rmbClicked(self.board[row][col])
                    is_assigned = True
            elif var.get_assigned_value() == 0:
                if not self.board[row][col].is_show():
                    self.lmbClicked(self.board[row][col])
                    is_assigned = True

        return is_assigned

    def import_board(self, board):
        """Import game from a list of lists with numbers."""
        self.row_size = len(board)
        self.col_size = len(board[0])

        self.mines_amount = 0

        self.flags = 0
        self.buttons = []
        self.mines = []
        self.board = []

        for row in range(self.row_size):
            lis = []
            for col in range(self.col_size):
                button = FieldButton(row, col, self.frame, self.images, board[row][col])
                if button.is_mine():
                    self.mines.append(button)
                    self.mines_amount += 1

                # first row grid for new game button
                button.grid(row=row + 1, column=col)
                button.bind('<Button-1>', self.lmbWrapper(button))
                button.bind('<Button-3>', self.rmbWrapper(button))
                lis.append(button)
                self.buttons.append(button)
            self.board.append(lis)

        self.remaining_mines = self.mines_amount


def setupMenu(root, minesweeper):
    menubar = Menu(root)

    fileMenu = Menu(menubar, tearoff=0)
    fileMenu.add_command(label="New Game", command=minesweeper.newGame)
    fileMenu.add_separator()
    fileMenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=fileMenu)

    root.config(menu=menubar)


def main():
    root = Tk()
    root.title("Minesweeper")
    minesweeper = Minesweeper(root)
    setupMenu(root, minesweeper)
    root.mainloop()


board = []

if __name__ == "__main__":
    main()
