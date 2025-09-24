BOARD_SIZE = 24

import random

# Set up board
board = []
for i in range(BOARD_SIZE):
    for j in range(BOARD_SIZE):
        if not ((i == 0 or i == BOARD_SIZE - 1) and (j == 0 or j == BOARD_SIZE - 1)):
            board.append((i, j))

# Assign a direction to each colour
def direction(colour):
    if colour == "r":
        return 1
    else:
        return 0

# Class for pegs of the grid
class Peg:
    def __init__(self, position):
        self.position = position # tuple containing coordinates of the peg
        self.links = [] # list of links it is connected to

# Check if two pegs can form a link
def knight_check(peg1, peg2):
    return ({abs(peg1.position[0] - peg2.position[0]), abs(peg1.position[1] - peg2.position[1])} == {1, 2})

# Class for links of the grid
class Link:
    def __init__(self, pegs):
        self.pegs = pegs # tuple containing the two pegs which the link connects

# Check if two links intersect
def intersect_check(link1, link2):

    # Check the orientation of three pegs
    def anticlockwise_check(peg1, peg2, peg3):
        return peg1.position[0]*peg2.position[1] + peg2.position[0]*peg3.position[1] + peg3.position[0]*peg1.position[1] - peg1.position[1]*peg2.position[0] - peg2.position[1]*peg3.position[0] - peg3.position[1]*peg1.position[0] > 0
    
    link1peg1 = link1.pegs[0]
    link1peg2 = link1.pegs[1]
    link2peg1 = link2.pegs[0]
    link2peg2 = link2.pegs[1]
    return (anticlockwise_check(link1peg1, link1peg2, link2peg1) != anticlockwise_check(link1peg1, link1peg2, link2peg2)) and (anticlockwise_check(link2peg1, link2peg2, link1peg1) != anticlockwise_check(link2peg1, link2peg2, link1peg2))

# Class for a state of the entire grid
class Gamestate:
    def __init__(self):
        self.emptyholes = board[:] # List of empty holes of the grid
        self.redpegs = [] # List of red pegs
        self.bluepegs = [] # List of blue pegs
        self.redlinks = [] # List of red links
        self.bluelinks = [] # List of blue links
        self.turn = "r" # Indicate which player's turn it is
        self.lastpeg = None # The last peg placed down
    
    # Return data of a player and opponent
    def player_data(self, colour):
        if colour == "r":
            return (self.redpegs, self.redlinks, self.bluepegs, self.bluelinks, "b")
        else:
            return (self.bluepegs, self.bluelinks, self.redpegs, self.redlinks, "r")
    
    # Check if a move is valid
    def valid(self, move):
        return not (self.turn == "r" and (move[0] == 0 or move[0] == BOARD_SIZE - 1)) and not (self.turn == "b" and (move[1] == 0 or move[1] == BOARD_SIZE - 1))
    
    # Implement a move on the grid
    def play(self, move): # move is a tuple indicating coordinates of the peg placed
        self.emptyholes.remove(move)
        newpeg = Peg(move)
        data = self.player_data(self.turn)
        ownpegs = data[0]
        ownlinks = data[1]
        opponentlinks = data[3]
        opponentcolour = data[4]
        for ownpeg in ownpegs:
            if knight_check(ownpeg, newpeg):
                newlink = Link((ownpeg, newpeg))
                check = True
                for opponentlink in opponentlinks:
                    if intersect_check(newlink, opponentlink):
                        check = False
                if check:
                    ownlinks.append(newlink)
                    ownpeg.links.append(newlink)
                    newpeg.links.append(newlink)
        ownpegs.append(newpeg)
        self.turn = opponentcolour
        self.lastpeg = newpeg
    
    # Undo the latest move
    def undo(self, move): # move is a tuple indicating coordinates of the peg removed
        self.emptyholes.append(move)
        data = self.player_data(self.turn)
        ownpegs = data[2]
        ownlinks = data[3]
        owncolour = data[4]
        for ownpeg in ownpegs:
            if ownpeg.position == move:
                ownpegs.remove(ownpeg)
                for link in ownpeg.links:
                    ownlinks.remove(link)
                    if link.pegs[0] == ownpeg:
                        link.pegs[1].links.remove(link)
                    else:
                        link.pegs[0].links.remove(link)
                break
        self.turn = owncolour
    
    # Divide all the pegs of a colour into components connected by links
    def components(self, colour):
        data = self.player_data(colour)
        components = []
        ownpegs = data[0]
        ownlinks = data[1]
        for peg in ownpegs:
            components.append([peg])
        for link in ownlinks:
            peg1 = link.pegs[0]
            peg2 = link.pegs[1]
            for component in components:
                if peg1 in component:
                    component1 = component
                if peg2 in component:
                    component2 = component
            if component1 != component2:
                components.remove(component1)
                components.remove(component2)
                components.append(component1 + component2)
        return components
    
    # Check if a player has won
    def win_check(self, colour):
        for component in self.components(colour):
            startcheck = False
            endcheck = False
            for peg in component:
                if peg.position[direction(colour)] == 0:
                    startcheck = True
                if peg.position[direction(colour)] == BOARD_SIZE - 1:
                    endcheck = True
                if startcheck and endcheck:
                    return True
        return False
    
    # Return the path connecting the goal lines if a player has won
    def win_path(self, colour):
        for component in self.components(colour):
            startcheck = False
            endcheck = False
            for peg in component:
                if peg.position[direction(colour)] == 0:
                    startcheck = True
                if peg.position[direction(colour)] == BOARD_SIZE - 1:
                    endcheck = True
                if startcheck and endcheck:
                    return component
        return []
    
    # Return a list of possible moves for CPU to choose from
    def possible_moves(self, mode):
        moves = []
        data = self.player_data(self.turn)
        ownpegs = data[0]
        opponentpegs = data[2]
        if ownpegs == []:
            output = [(11, 11), (11, 12), (12, 11), (12, 12)]
            for peg in opponentpegs:
                if peg.position in output:
                    output.remove(peg.position)
            return output
        for peg in ownpegs:
            for distance in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                possible_move = (peg.position[0] + distance[0], peg.position[1] + distance[1])
                if possible_move in self.emptyholes:
                    if self.valid(possible_move):
                        if possible_move not in moves:
                            moves.append(possible_move)
        return moves
    
    # Evaluate a state
    def score(self, colour, mode):
        data = self.player_data(colour)
        ownpegs = data[0]
        ownlinks = data[1]
        opponentpegs = data[2]
        opponentlinks = data[3]
        opponentcolour = data[4]
        if self.win_check(colour):
            return float("inf")
        if self.win_check(opponentcolour):
            return float("-inf")
        score = 0
        for link in ownlinks:
            score += abs(link.pegs[0].position[direction(colour)] - link.pegs[1].position[direction(colour)])
        for link in opponentlinks:
            score -= abs(link.pegs[0].position[direction(opponentcolour)] - link.pegs[1].position[direction(opponentcolour)])
        for component in self.components(colour):
            vmax = 0
            vmin = BOARD_SIZE - 1
            hmax = 0
            hmin = BOARD_SIZE - 1
            for peg in component:
                if peg.position[direction(colour)] > vmax:
                    vmax = peg.position[direction(colour)]
                if peg.position[direction(colour)] < vmin:
                    vmin = peg.position[direction(colour)]
                if peg.position[direction(opponentcolour)] > hmax:
                    hmax = peg.position[direction(opponentcolour)]
                if peg.position[direction(opponentcolour)] < hmin:
                    hmin = peg.position[direction(opponentcolour)]
            score += 100*(vmax - vmin) + 10*(hmax - hmin)
        for component in self.components(opponentcolour):
            vmax = 0
            vmin = BOARD_SIZE - 1
            hmax = 0
            hmin = BOARD_SIZE - 1
            for peg in component:
                if peg.position[direction(opponentcolour)] > vmax:
                    vmax = peg.position[direction(opponentcolour)]
                if peg.position[direction(opponentcolour)] < vmin:
                    vmin = peg.position[direction(opponentcolour)]
                if peg.position[direction(colour)] > hmax:
                    hmax = peg.position[direction(colour)]
                if peg.position[direction(colour)] < hmin:
                    hmin = peg.position[direction(colour)]
            score -= 100*(vmax - vmin) + 10*(hmax - hmin)
        
        return score
    
    # Return the move CPU makes given a state
    def move(self, mode):
        def minimax(state, depth, alpha, beta, maximizing, colour, mode):
            if depth == 0 or state.win_check("r") or state.win_check("b"):
                return (state.score(colour, mode), None)
            best_move = None
            if maximizing:
                max_score = float("-inf")
                for move in state.possible_moves(mode):
                    lastpeg = state.lastpeg
                    state.play(move)
                    score = minimax(state, depth - 1, alpha, beta, False, colour, mode)[0]
                    state.undo(move)
                    state.lastpeg = lastpeg
                    if score > max_score:
                        max_score = score
                        best_move = move
                    if score > alpha:
                        alpha = score
                    if alpha >= beta:
                        break
                return (max_score, best_move)
            else:
                min_score = float("inf")
                for move in state.possible_moves(mode):
                    lastpeg = state.lastpeg
                    state.play(move)
                    score = minimax(state, depth - 1, alpha, beta, True, colour, mode)[0]
                    state.undo(move)
                    state.lastpeg = lastpeg
                    if score < min_score:
                        min_score = score
                        best_move = move
                    if score < beta:
                        beta = score
                    if alpha >= beta:
                        break
                return (min_score, best_move)
        depth = 2
        return minimax(self, depth, float("-inf"), float("inf"), True, self.turn, mode)[1]


# Implement GUI
import tkinter as tk

root = tk.Tk()
root.title("Twixt")
root.geometry("900x600")
canvas = tk.Canvas(root, width = 600, height = 600, bg = "gold")
canvas.pack(side = "left")
control_frame = tk.Frame(root, bg = "teal")
control_frame.pack(side = "right", fill = "both", expand = True)
title = tk.Label(control_frame, text = "Twixt", font = ("Times", 24, "italic"), bg = "teal", fg = "white")
title.pack(pady = 10)
p1_label = tk.Label(control_frame, text = "", fg = "red", bg = "white")
p2_label = tk.Label(control_frame, text = "", fg = "blue", bg = "white")
turn_label = tk.Label(control_frame, text = "", bg = "white")
mode_label = tk.Label(control_frame, text = "", fg = "lime", bg = "white")
restart_button = tk.Button(control_frame, text = "New Game", bg = "lime", width = 10, height = 2)
restart_button.pack(pady = 20)
rules_button = tk.Button(control_frame, text = "Rules", bg = "yellow", width = 10, height = 2)
rules_button.pack(pady = 20)
quit_button = tk.Button(control_frame, text = "Quit", bg = "red", fg = "white", width = 10, height = 2, command = root.quit)
quit_button.pack(pady = 20)

MARGIN = 70
SPACING = (600 - 2*MARGIN)/(BOARD_SIZE - 1)
TOP_LINE = MARGIN + SPACING/2
BOTTOM_LINE = 600 - TOP_LINE
WIDTH = 2
WIDER = 4
WIDEST = 5

# Draw the grid
def draw_board(gamestate, canvas, turn_label, user_colour):
    redwinpath = gamestate.win_path("r")
    bluewinpath = gamestate.win_path("b")
    canvas.delete("all")
    canvas.create_line(TOP_LINE, TOP_LINE, BOTTOM_LINE, TOP_LINE, fill = "red", width = WIDTH)
    canvas.create_line(TOP_LINE, BOTTOM_LINE, BOTTOM_LINE, BOTTOM_LINE, fill = "red", width = WIDTH)
    canvas.create_line(TOP_LINE, TOP_LINE, TOP_LINE, BOTTOM_LINE, fill = "blue", width = WIDTH)
    canvas.create_line(BOTTOM_LINE, TOP_LINE, BOTTOM_LINE, BOTTOM_LINE, fill = "blue", width = WIDTH)
    for (i, j) in gamestate.emptyholes:
        x = MARGIN + i*SPACING
        y = MARGIN + j*SPACING
        canvas.create_oval(x - WIDTH, y - WIDTH, x + WIDTH, y + WIDTH, fill = "black")
    for peg in gamestate.redpegs + gamestate.bluepegs:
        x = MARGIN + peg.position[0]*SPACING
        y = MARGIN + peg.position[1]*SPACING
        if peg in gamestate.redpegs:
            if peg in redwinpath:
                colour = "firebrick" # Draw winning path in bolder colour
            else:
                colour = "red"
        else:
            if peg in bluewinpath:
                colour = "mediumblue" # Draw winning path in bolder colour
            else:
                colour = "blue"
        if peg == gamestate.lastpeg:
            outline = "lime"
            size = WIDEST
        else:
            outline = ""
            size = WIDER
        canvas.create_oval(x - size, y - size, x + size, y + size, fill = colour, outline = outline)
    for link in gamestate.redlinks + gamestate.bluelinks:
        peg1 = link.pegs[0]
        peg2 = link.pegs[1]
        x1 = MARGIN + peg1.position[0]*SPACING
        y1 = MARGIN + peg1.position[1]*SPACING
        x2 = MARGIN + peg2.position[0]*SPACING
        y2 = MARGIN + peg2.position[1]*SPACING
        if link in gamestate.redlinks:
            if peg1 in redwinpath:
                colour = "firebrick" # Draw winning path in bolder colour
                width = WIDEST
            else:
                colour = "red"
                width = WIDTH
        else:
            if peg1 in bluewinpath:
                colour = "mediumblue" # Draw winning path in bolder colour
                width = WIDEST
            else:
                colour = "blue"
                width = WIDTH
        canvas.create_line(x1, y1, x2, y2, fill = colour, width = width)
    
    # Configurate turn label
    if gamestate.win_check("r"):
        if user_colour == "r":
            turn_label.config(text = "You Won!", fg = "firebrick")
        else:
            turn_label.config(text = "CPU Won", fg = "firebrick")
    elif gamestate.win_check("b"):
        if user_colour == "r":
            turn_label.config(text = "CPU Won", fg = "mediumblue")
        else:
            turn_label.config(text = "You Won!", fg = "mediumblue")
    else:
        if gamestate.turn == user_colour:
            if user_colour == "r":
                turn_label.config(text = "Your Turn", fg = "darkred")
            else:
                turn_label.config(text = "Your Turn", fg = "darkblue")
        else:
            if user_colour == "r":
                turn_label.config(text = "CPU's Turn", fg = "darkblue")
            else:
                turn_label.config(text = "CPU's Turn", fg = "darkred")

# Configurate popup when pressing New Game/Restart button
def new_game_popup():
    popup = tk.Toplevel(root, bg = "white")
    popup.title("New Game Options")
    popup.geometry("300x300")
    popup.transient(root)
    popup.grab_set()
    popup.focus_set()
    root.update_idletasks()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_w = root.winfo_width()
    root_h = root.winfo_height()
    popup_w = 300
    popup_h = 300
    x = root_x + (root_w // 2) - (popup_w // 2)
    y = root_y + (root_h // 2) - (popup_h // 2)
    popup.geometry(f"{popup_w}x{popup_h}+{x}+{y}")
    global difficulty
    difficulty = tk.StringVar(value = "None")
    player = tk.StringVar(value = "None")
    def start_game():
        global state
        global user_colour
        state = Gamestate()
        if player.get() == "P1":
            user_colour = "r"
        elif player.get() == "P2":
            user_colour = "b"
        elif player.get() == "Random":
            user_colour = random.choice(["r", "b"])
        else:
            return
        if difficulty.get() != "None":
            mode_label.config(text = difficulty.get())
        else:
            return
        if user_colour == "r":
            p1_label.config(text = "Player 1 (You)")
            p2_label.config(text = "Player 2 (CPU)")
        else:
            p1_label.config(text = "Player 1 (CPU)")
            p2_label.config(text = "Player 2 (You)")
        p1_label.pack(pady = 5)
        p2_label.pack(pady = 5)
        turn_label.pack(pady = 10)
        mode_label.pack(pady = 10)
        restart_button.config(text = "Restart")
        draw_board(state, canvas, turn_label, user_colour)
        popup.destroy()
        CPU_move()
    tk.Label(popup, text = "Select Difficulty").pack(pady = 5)
    tk.Radiobutton(popup, text = "Easy", variable = difficulty, value = "Easy").pack()
    tk.Radiobutton(popup, text = "Medium", variable = difficulty, value = "Medium").pack()
    tk.Radiobutton(popup, text = "Difficult", variable = difficulty, value = "Difficult").pack()
    tk.Label(popup, text = "Select Player").pack(pady = 5)
    tk.Radiobutton(popup, text = "Player 1 (Red)", variable = player, value = "P1").pack()
    tk.Radiobutton(popup, text = "Player 2 (Blue)", variable = player, value = "P2").pack()
    tk.Radiobutton(popup, text = "Random", variable = player, value = "Random").pack()
    tk.Button(popup, text = "Start", command = start_game).pack(pady = 10)
restart_button.config(text = "New Game", command = new_game_popup)

# Respond to user clicking on a peg
def click_board(event):
    global state

    SENSITIVITY = 0.35

    if not state.win_check("r") and not state.win_check("b"):
        if state.turn == user_colour:
            i = (event.x - MARGIN)/SPACING
            j = (event.y - MARGIN)/SPACING
            if abs(i - round(i)) < SENSITIVITY:
                i = round(i)
            else:
                i = BOARD_SIZE
            if abs(j - round(j)) < SENSITIVITY:
                j = round(j)
            else:
                j = BOARD_SIZE
            if (i, j) in state.emptyholes:
                if state.valid((i, j)):
                    state.play((i, j))
                    draw_board(state, canvas, turn_label, user_colour)
canvas.bind("<Button-1>", click_board)

# CPU move
def CPU_move():
    global state
    global difficulty
    if not state.win_check("r") and not state.win_check("b"):
        if state.turn != user_colour:
            state.play(state.move(difficulty))
            draw_board(state, canvas, turn_label, user_colour)
        root.after(1000, CPU_move)

# Configurate popup when pressing Rules button
def rules_popup():
    popup = tk.Toplevel(root)
    popup.title("Game Rules")
    popup.geometry("300x300")
    root.update_idletasks()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    popup.geometry(f"+{root_x+620}+{root_y+20}")
    frame = tk.Frame(popup, bg = "black")
    frame.pack(expand = True, fill = "both")
    text = tk.Text(frame, wrap = "word", bg = "#ffff80", fg = "black", font = ("Arial", 11))
    text.pack(expand = True, fill = "both", padx = 5, pady = 5)
    rules_text = """Twixt Rules:
1. The board is a 24x24 grid with the four corners removed.
2. Players take turns placing pegs on empty holes.
3. Pegs are connected by links in a knight's move pattern (2 by 1).
4. Links cannot cross opponent links.
5. The goal is to create a continuous path from your start edge to your goal edge.
6. Red player connects top to bottom; Blue player connects left to right.
7. You cannot place pegs behind your opponent's goal lines.
8. The most recent peg is highlighted with a lime ring.
"""
    text.insert("1.0",rules_text)
    text.tag_add("header", "1.0", "1.11")
    text.tag_config("header", foreground = "teal", font = ("Arial", 12, "bold"))
    text.tag_add("Red", "7.3", "7.6")
    text.tag_config("Red", foreground = "red", font = ("Arial", 11, "bold"))
    text.tag_add("Blue", "7.38", "7.42")
    text.tag_config("Blue", foreground = "blue", font = ("Arial", 11, "bold"))
    text.tag_add("lime", "9.45", "9.49")
    text.tag_config("lime", foreground = "lime", font = ("Arial", 11, "bold"))
    for i in range(2,10):
        text.tag_add(f"point{i}", f"{i}.0", f"{i}.1")
        text.tag_config(f"point{i}", foreground = "darkorange", font = ("Arial", 11, "bold"))
    text.config(state = "disabled")
    tk.Button(popup, text = "Close", command = popup.destroy, bg = "teal", fg = "white").pack(pady = 5)
rules_button.config(command = rules_popup)
tk.mainloop()