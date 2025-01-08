from typing import List
import tkinter as tk
import random

# Constants for the Minesweeper game
GRID_SIZE = 16       # Number of rows and columns
NUM_MINES = 40       # Total number of mines
TILE_SIZE = 30       # Tile size in pixels


class Tile:
    """Represents a single tile on the Minesweeper board."""
    def __init__(self):
        self.is_mine = False
        self.adjacent_mines = 0
        self.is_revealed = False
        self.is_flagged = False


class Minesweeper:
    def __init__(self, root: tk.Tk):
        self.root: tk.Tk = root
        self.root.title("Minesweeper")
        self.grid: List[List[Tile]] = [[Tile() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.buttons: List[List[tk.Button | None]] = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.is_game_over: bool = False

        # Initialize the game
        self.setup_ui()
        self.place_mines()
        self.calculate_adjacent_mines()

    def setup_ui(self):
        """Setup the user interface with buttons and a header."""
        # Add a header for game status
        self.status_label = tk.Label(
            self.root, text="Minesweeper - Click to Begin", font=("Arial", 16), pady=10
        )
        self.status_label.pack()

        # Create a frame to hold the grid
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack()

        # Create buttons for the grid
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                button = tk.Button(
                    self.grid_frame,
                    width=2,
                    height=1,
                    font=("Arial", 12, "bold"),
                    command=lambda r=row, c=col: self.on_left_click(r, c),
                    relief=tk.RAISED,
                    bg="lightgray",
                )
                button.grid(row=row, column=col, padx=1, pady=1)
                button.bind(
                    "<Button-3>", lambda e, r=row, c=col: self.on_right_click(e, r, c)
                )
                self.buttons[row][col] = button

        # Add a restart button below the grid
        self.restart_button = tk.Button(
            self.root, text="Restart Game", font=("Arial", 14), command=self.restart_game
        )
        self.restart_button.pack(pady=10)

    def place_mines(self):
        """Randomly place mines on the grid."""
        mines_placed = 0
        while mines_placed < NUM_MINES:
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - 1)
            if not self.grid[row][col].is_mine:
                self.grid[row][col].is_mine = True
                mines_placed += 1

    def calculate_adjacent_mines(self):
        """Calculate the number of adjacent mines for each tile."""
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1), (1, 0), (1, 1)]
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col].is_mine:
                    continue
                count = 0
                for dr, dc in directions:
                    r, c = row + dr, col + dc
                    if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                        if self.grid[r][c].is_mine:
                            count += 1
                self.grid[row][col].adjacent_mines = count

    def on_left_click(self, row, col):
        """Handle left-click to reveal a tile."""
        if self.is_game_over or self.grid[row][col].is_flagged:
            return

        tile = self.grid[row][col]
        if tile.is_revealed:
            return

        tile.is_revealed = True
        if tile.is_mine:
            self.buttons[row][col].config(text="M", bg="red", fg="black")
            self.end_game(False)
        else:
            self.buttons[row][col].config(
                text=str(tile.adjacent_mines) if tile.adjacent_mines > 0 else "",
                state="disabled",
                relief=tk.SUNKEN,
                bg="white",
            )
            if tile.adjacent_mines == 0:
                self.reveal_adjacent_tiles(row, col)

        if self.check_win():
            self.end_game(True)

    def reveal_adjacent_tiles(self, row, col):
        """Recursively reveal adjacent tiles if they are blank."""
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1), (1, 0), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                if not self.grid[r][c].is_revealed and not self.grid[r][c].is_flagged:
                    self.on_left_click(r, c)

    def on_right_click(self, event, row, col):
        """Handle right-click to flag a tile."""
        if self.is_game_over or self.grid[row][col].is_revealed:
            return

        button = self.buttons[row][col]
        assert isinstance(button, tk.Button)
        tile = self.grid[row][col]
        tile.is_flagged = not tile.is_flagged
        button.config(
            text="F" if tile.is_flagged else "",
            bg="yellow" if tile.is_flagged else "lightgray",
        )

    def check_win(self):
        """Check if the player has won the game."""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                tile = self.grid[row][col]
                if not tile.is_mine and not tile.is_revealed:
                    return False
        return True

    def end_game(self, is_win):
        """Handle the end of the game."""
        self.is_game_over = True
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                button = self.buttons[row][col]
                assert isinstance(button, tk.Button)
                tile = self.grid[row][col]
                if tile.is_mine:
                    button.config(
                        text="M",
                        bg="red" if not is_win else "green",
                        fg="black",
                    )
        self.status_label.config(
            text="You Won!" if is_win else "You Lost!", fg="green" if is_win else "red"
        )

    def restart_game(self):
        """Restart the game."""
        self.is_game_over = False
        self.grid = [[Tile() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.place_mines()
        self.calculate_adjacent_mines()
        self.status_label.config(text="Minesweeper - Click to Begin", fg="black")
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                button = self.buttons[row][col]
                assert isinstance(button, tk.Button)
                button.config(
                    text="",
                    state="normal",
                    relief=tk.RAISED,
                    bg="lightgray",
                )


# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    Minesweeper(root)
    root.mainloop()
