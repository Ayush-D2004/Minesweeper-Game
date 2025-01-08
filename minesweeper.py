import tkinter as tk
from tkinter import messagebox
from typing import List

class Tile:
    def __init__(self):
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0

class Minesweeper:
    def __init__(self, root: tk.Tk):
        self.root: tk.Tk = root
        self.root.title("Minesweeper")
        
        # Maximize window without overlapping taskbar
        self.root.state('zoomed')  # This works better than full screen
        
        # Add setup frame for initial configuration
        self.setup_frame = tk.Frame(self.root)
        self.setup_frame.pack(expand=True, pady=20)
        
        # Add input fields for grid size and mines
        tk.Label(self.setup_frame, text="Grid Size (8-30):", font=("Arial", 12)).pack()
        self.size_var = tk.StringVar(value="16")
        tk.Entry(self.setup_frame, textvariable=self.size_var, font=("Arial", 12)).pack()
        
        tk.Label(self.setup_frame, text="Number of Mines:", font=("Arial", 12)).pack()
        self.mines_var = tk.StringVar(value="40")
        tk.Entry(self.setup_frame, textvariable=self.mines_var, font=("Arial", 12)).pack()
        
        tk.Button(self.setup_frame, text="Start Game", font=("Arial", 12), 
                 command=self.start_game).pack(pady=10)

    def start_game(self):
        # Validate and set grid size and mines
        try:
            grid_size = int(self.size_var.get())
            num_mines = int(self.mines_var.get())
            
            if not (8 <= grid_size <= 30):
                messagebox.showerror("Error", "Grid size must be between 8 and 30!")
                return
                
            if not (1 <= num_mines <= (grid_size * grid_size) - 1):
                messagebox.showerror("Error", "Invalid number of mines!")
                return
                
            # Remove setup frame
            self.setup_frame.destroy()
            
            # Set game parameters
            global GRID_SIZE, NUM_MINES
            GRID_SIZE = grid_size
            NUM_MINES = num_mines
            
            # Initialize game
            self.grid: List[List[Tile]] = [[Tile() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
            self.buttons: List[List[tk.Button | None]] = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
            self.is_game_over: bool = False
            
            # Setup game UI
            self.setup_ui()
            self.place_mines()
            self.calculate_adjacent_mines()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")

    def setup_ui(self):
        """Setup the user interface with buttons and a header."""
        # Create main container
        self.game_container = tk.Frame(self.root)
        self.game_container.pack(expand=True)

        # Add a header for game status
        self.status_label = tk.Label(
            self.game_container, text="Minesweeper - Click to Begin", font=("Arial", 16), pady=10
        )
        self.status_label.pack()

        # Create a frame to hold the grid and controls
        game_area = tk.Frame(self.game_container)
        game_area.pack()

        # Create a frame to hold the grid
        self.grid_frame = tk.Frame(game_area)
        self.grid_frame.pack(side=tk.LEFT, padx=20)

        # Create a frame for controls (restart button)
        controls_frame = tk.Frame(game_area)
        controls_frame.pack(side=tk.LEFT, padx=20, fill=tk.Y)

        # Calculate button size based on screen size
        screen_height = self.root.winfo_screenheight()
        max_button_size = min(40, (screen_height - 200) // GRID_SIZE)
        button_size = max(20, max_button_size)

        # Create buttons for the grid
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                button = tk.Button(
                    self.grid_frame,
                    width=2,
                    height=1,
                    font=("Arial", int(button_size/2.5), "bold"),
                    command=lambda r=row, c=col: self.on_left_click(r, c),
                    relief=tk.RAISED,
                    bg="lightgray",
                )
                button.grid(row=row, column=col, padx=1, pady=1)
                button.bind(
                    "<Button-3>", lambda e, r=row, c=col: self.on_right_click(e, r, c)
                )
                self.buttons[row][col] = button

        # Add a restart button to the right of the grid
        self.restart_button = tk.Button(
            controls_frame,
            text="Restart Game (R)",
            font=("Arial", 14, "bold"),
            command=self.restart_game,
            bg="white",
            padx=20,
            pady=10
        )
        self.restart_button.pack(pady=20)
        
        # Add keyboard shortcut for restart
        self.root.bind("<r>", lambda e: self.restart_game())
        self.root.bind("<R>", lambda e: self.restart_game())

    def calculate_adjacent_mines(self):
        """Calculate the number of adjacent mines for each tile."""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if not self.grid[row][col].is_mine:
                    count = 0
                    # Check all 8 adjacent cells
                    for r in range(max(0, row-1), min(GRID_SIZE, row+2)):
                        for c in range(max(0, col-1), min(GRID_SIZE, col+2)):
                            if self.grid[r][c].is_mine:
                                count += 1
                    self.grid[row][col].adjacent_mines = count

    def place_mines(self):
        """Randomly place mines on the grid."""
        from random import randint
        mines_placed = 0
        while mines_placed < NUM_MINES:
            row = randint(0, GRID_SIZE - 1)
            col = randint(0, GRID_SIZE - 1)
            if not self.grid[row][col].is_mine:
                self.grid[row][col].is_mine = True
                mines_placed += 1

    def on_left_click(self, row: int, col: int):
        """Handle left click to reveal tiles."""
        if self.is_game_over or self.grid[row][col].is_flagged:
            return

        tile = self.grid[row][col]
        if tile.is_mine:
            self.game_over(False)
            return

        self.reveal_tile(row, col)
        if self.check_win():
            self.game_over(True)

    def reveal_tile(self, row: int, col: int):
        """Reveal a tile and its adjacent empty tiles."""
        tile = self.grid[row][col]
        if tile.is_revealed or tile.is_flagged:
            return

        tile.is_revealed = True
        button = self.buttons[row][col]
        if not button:
            return
            
        if tile.adjacent_mines == 0:
            button.configure(relief=tk.SUNKEN, text="", bg="white")
            # Reveal adjacent tiles
            for r in range(max(0, row-1), min(GRID_SIZE, row+2)):
                for c in range(max(0, col-1), min(GRID_SIZE, col+2)):
                    if not self.grid[r][c].is_revealed:
                        self.reveal_tile(r, c)
        else:
            button.configure(relief=tk.SUNKEN, text=str(tile.adjacent_mines), bg="white")

    def on_right_click(self, event, row: int, col: int):
        """Handle right click to flag/unflag tiles."""
        if self.is_game_over or self.grid[row][col].is_revealed:
            return

        tile = self.grid[row][col]
        button = self.buttons[row][col]
        if not button:
            return
        
        tile.is_flagged = not tile.is_flagged
        button.configure(text="🚩" if tile.is_flagged else "", bg="red" if tile.is_flagged else "lightgray")

    def restart_game(self):
        """Reset the game to initial state."""
        # Clear existing widgets
        self.game_container.destroy()
        
        # Create new setup frame
        self.setup_frame = tk.Frame(self.root)
        self.setup_frame.pack(expand=True, pady=20)
        
        # Re-add input fields
        tk.Label(self.setup_frame, text="Grid Size (8-30):", font=("Arial", 12)).pack()
        tk.Entry(self.setup_frame, textvariable=self.size_var, font=("Arial", 12)).pack()
        
        tk.Label(self.setup_frame, text="Number of Mines:", font=("Arial", 12)).pack()
        tk.Entry(self.setup_frame, textvariable=self.mines_var, font=("Arial", 12)).pack()
        
        tk.Button(self.setup_frame, text="Start Game", font=("Arial", 12), 
                 command=self.start_game).pack(pady=10)

    def game_over(self, won: bool):
        """Handle game over state."""
        self.is_game_over = True
        if won:
            self.status_label.configure(text="Congratulations! You Won!", fg="green")
        else:
            self.status_label.configure(text="Game Over! You Hit a Mine!", fg="red")
            # Reveal all mines
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    button = self.buttons[row][col]
                    if button and self.grid[row][col].is_mine:
                        button.configure(text="💣", bg="red")

    def check_win(self) -> bool:
        """Check if all non-mine tiles are revealed."""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                tile = self.grid[row][col]
                if not tile.is_mine and not tile.is_revealed:
                    return False
        return True

if __name__ == "__main__":
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()