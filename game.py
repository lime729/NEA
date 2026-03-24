BOARD_SIZE = 24

import random
import math

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
        self.position = position # Tuple containing coordinates of the peg
        self.links = [] # List of links it is connected to

# Check if two pegs can form a link
def knight_check(peg1, peg2):
    return ({abs(peg1.position[0] - peg2.position[0]), abs(peg1.position[1] - peg2.position[1])} == {1, 2})

# Class for links of the grid
class Link:
    def __init__(self, pegs):
        self.pegs = pegs # Tuple containing the two pegs which the link connects

# Check the orientation of three pegs
def anticlockwise_check(point1, point2, point3):
    a = point1[0]*point2[1] + point2[0]*point3[1] + point3[0]*point1[1] - point1[1]*point2[0] - point2[1]*point3[0] - point3[1]*point1[0]
    if a > 0:
        return 1
    if a < 0:
        return -1
    return 0

# Check if two points are on opposite sides of a link
def opposite_check(point1, point2, link):
    point3 = link.pegs[0].position
    point4 = link.pegs[1].position
    a = anticlockwise_check(point1, point2, point3)*anticlockwise_check(point1, point2, point4)
    b = anticlockwise_check(point3, point4, point1)*anticlockwise_check(point3, point4, point2)
    return a <= 0 and b <= 0 and a + b < 0

# Check if two links intersect
def intersect_check(link1, link2):
    point1 = link1.pegs[0].position
    point2 = link1.pegs[1].position
    return opposite_check(point1, point2, link2)

# Return the spaces where a virtual link can be disrupted by an opponent peg
# Any opponent peg in threats will disrupt the virtual link, while opponent pegs in centre can only disrupt the virtual link if they have a link attached
def threat_space(point1, point2):
    distance = (abs(point1[0] - point2[0]), abs(point1[1] - point2[1]))
    if distance == (0, 4):
        dx = 1
        dy = (point2[1] - point1[1])//4
        threats_displacement = [(-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4)]
        centre_displacement = [(0, 1), (0, 2), (0, 3)]
    if distance == (4, 0):
        dx = (point2[0] - point1[0])//4
        dy = 1
        threats_displacement = [(0, -1), (1, -1), (2, -1), (3, -1), (4, -1), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1)]
        centre_displacement = [(1, 0), (2, 0), (3, 0)]
    if distance == (3, 3):
        dx = (point2[0] - point1[0])//3
        dy = (point2[1] - point1[1])//3
        threats_displacement = [(-1, 1), (0, 1), (0, 2), (1, -1), (1, 0), (1, 2), (1, 3), (2, 0), (2, 1), (2, 3), (2, 4), (3, 1), (3, 2), (4, 2)]
        centre_displacement = [(1, 1), (2, 2)]
    if distance == (1, 3):
        dx = point2[0] - point1[0]
        dy = (point2[1] - point1[1])//3
        threats_displacement = [(-1, 1), (-1, 2), (0, 3), (1, 0), (2, 1), (2, 2)]
        centre_displacement = [(0, 1), (0, 2), (1, 1), (1, 2)]
    if distance == (3, 1):
        dx = (point2[0] - point1[0])//3
        dy = point2[1] - point1[1]
        threats_displacement = [(1, -1), (2, -1), (3, 0), (0, 1), (1, 2), (2, 2)]
        centre_displacement = [(1, 0), (2, 0), (1, 1), (2, 1)]
    if distance == (0, 2):
        dx = 1
        dy = (point2[1] - point1[1])//2
        threats_displacement = [(-2, 1), (2, 1)]
        centre_displacement = [(-1, 1), (0, 1), (1, 1)]
    if distance == (2, 0):
        dx = (point2[0] - point1[0])//2
        dy = 1
        threats_displacement = [(1, -2), (1, 2)]
        centre_displacement = [(1, -1), (1, 0), (1, 1)]
    if distance == (1, 1):
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        threats_displacement = [(-1, 2), (2, -1)]
        centre_displacement = [(0, 1), (1, 0)]
    
    threats = []
    centre = []
    for displacement in threats_displacement:
        x = point1[0] + dx*displacement[0]
        y = point1[1] + dy*displacement[1]
        if (x, y) in board:
            threats.append((x, y))
    for displacement in centre_displacement:
        x = point1[0] + dx*displacement[0]
        y = point1[1] + dy*displacement[1]
        if (x, y) in board:
            centre.append((x, y))
    return threats, centre

# Class for the graph used in max flow algorithm when evaluating a state
class Graph:
    def __init__(self):
        self.adjlist = {} # Dictionary representing the adjacency list of the graph
        self.source = "source" # Source vertex of the graph
        self.sink = "sink" # Sink vertex of the graph
        self.vertices = [] # List of vertices in the graph

    # Depth first search to find a path with available capacity from source to sink
    def dfs(self, start, end, visited, path):
        visited.append(start)
        path.append(start)
        if start == end:
            return path
        for neighbour in self.adjlist[start]:
            if neighbour not in visited and self.adjlist[start][neighbour] > 0:
                result_path = self.dfs(neighbour, end, visited, path.copy())
                if result_path is not None:
                    return result_path
        return None
    
    # Ford-Fulkerson algorithm to find the maximum flow from source to sink
    def max_flow(self):
        max_flow = 0
        path = self.dfs(self.source, self.sink, [], [])
        while path is not None:
            path_flow = float("inf")
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]
                if self.adjlist[u][v] < path_flow:
                    path_flow = self.adjlist[u][v]
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]
                self.adjlist[u][v] -= path_flow
                if u not in self.adjlist[v]:
                    self.adjlist[v][u] = 0
                self.adjlist[v][u] += path_flow
            max_flow += path_flow
            path = self.dfs(self.source, self.sink, [], [])
        return max_flow

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
        return not move[1 - direction(self.turn)] == 0 and not move[1 - direction(self.turn)] == BOARD_SIZE - 1
    
    # Implement a move on the grid
    def play(self, move):
        self.emptyholes.remove(move)
        newpeg = Peg(move)
        data = self.player_data(self.turn)
        ownpegs = data[0]
        ownlinks = data[1]
        opplinks = data[3]
        oppcolour = data[4]
        for ownpeg in ownpegs:
            if knight_check(ownpeg, newpeg):
                newlink = Link((ownpeg, newpeg))
                check = True
                for opplink in opplinks:
                    if intersect_check(newlink, opplink):
                        check = False
                if check:
                    ownlinks.append(newlink)
                    ownpeg.links.append(newlink)
                    newpeg.links.append(newlink)
        ownpegs.append(newpeg)
        self.turn = oppcolour
        self.lastpeg = newpeg
    
    # Undo the latest move
    def undo(self, move):
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
    
    # Check if the player to move has no valid moves left, resulting in a draw
    def draw_check(self):
        for move in self.emptyholes:
            if self.valid(move):
                return False
        return True
    
    # Return a list of possible moves for CPU to choose from
    def possible_moves(self, difficulty):
        data = self.player_data(self.turn)
        ownpegs = data[0]
        opppegs = data[2]

        moves = []

        # If CPU is guaranteed to win, only return moves which cross the start and goal lines
        for component in self.components(self.turn):
            startcheck = False
            endcheck = False
            for peg in component:
                if peg.position[direction(self.turn)] <= 1:
                    startcheck = True
                if peg.position[direction(self.turn)] >= BOARD_SIZE - 2:
                    endcheck = True
            if startcheck and endcheck:
                for peg in component:
                    for dx, dy in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                        move = (peg.position[0] + dx, peg.position[1] + dy)
                        if move in self.emptyholes and self.valid(move):
                            if move[direction(self.turn)] == 0 or move[direction(self.turn)] == BOARD_SIZE - 1:
                                if move not in moves:
                                    moves.append(move)
                return moves
        
        # Add moves which can possibly form links to existing pegs
        for peg in ownpegs:
            for dx, dy in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), 
                        (1, -2), (1, 2), (2, -1), (2, 1)]:
                move = (peg.position[0] + dx, peg.position[1] + dy)
                if move in self.emptyholes and self.valid(move):
                    if move not in moves:
                        moves.append(move)
        
        # If difficulty is not Difficult, add moves which can possibly prevent opponent links
        if difficulty != "Difficult":
            for peg in opppegs:
                for dx, dy in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                    move = (peg.position[0] + dx, peg.position[1] + dy)
                    if move in self.emptyholes and self.valid(move):
                        if move not in moves:
                            moves.append(move)
        
        # If difficulty is Difficult, add moves which can form effective virtual links to existing pegs
        if difficulty == "Difficult":
            for peg in ownpegs:
                for dx, dy in [(-4, 0), (4, 0), (0, -4), (0, 4), (-3, -3), (-3, 3), (3, -3), (3, 3), (-1, 3), (-1, -3), (1, 3), (1, -3), (-3, 1), (-3, -1), (3, 1), (3, -1)]:
                    move = (peg.position[0] + dx, peg.position[1] + dy)
                    if move in self.emptyholes and self.valid(move):
                        if self.safe(peg.position, move, self.turn):
                            if move not in moves:
                                moves.append(move)
        
        # If difficulty is not Easy, add safe defensive moves around opponent pegs
        if difficulty != "Easy":
            if self.turn == "r":
                displacements = [(-4, 0), (4, 0)]
            else:
                displacements = [(0, -4), (0, 4)]
            for peg in opppegs:
                for displacement in displacements:
                    move = (peg.position[0] + displacement[0], peg.position[1] + displacement[1])
                    if move in self.emptyholes and self.valid(move):
                        if move not in moves:
                            moves.append(move)
        
        # Sample random moves throughout the board
        for i in range(BOARD_SIZE//4):
            for j in range(BOARD_SIZE//4):
                region = []
                for k in range(4):
                    for l in range(4):
                        move = (i*4 + k, j*4 + l)
                        if move in self.emptyholes and self.valid(move):
                            if move not in moves:
                                region.append(move)
                if region != []:
                    moves.append(random.choice(region))
        return moves
    
    # Return a graph representing the state of the grid for a player, used in max flow algorithm when evaluating a state
    def graph(self, inner, boundlinks, colour, difficulty):
            data = self.player_data(colour)
            ownpegs = data[0]
            ownlinks = data[1]
            opplinks = data[3]

            # Initialise graph
            g = Graph()
            g.vertices = list(inner.keys())
            for vertex in g.vertices:
                g.adjlist[vertex] = {}
            g.adjlist[g.source] = {}
            g.adjlist[g.sink] = {}

            # Connect vertices to source and sink and to adjacent vertices
            for vertex in g.vertices:
                if vertex[direction(colour)] == 0:
                    g.adjlist[g.source][vertex] = float("inf")
                if vertex[direction(colour)] == BOARD_SIZE - 1:
                    g.adjlist[vertex][g.sink] = float("inf")
                for othervertex in inner:
                    if abs(vertex[0] - othervertex[0]) + abs(vertex[1] - othervertex[1]) == 1:
                        if othervertex[direction(colour)] >= vertex[direction(colour)]: # Only allow edges which move towards the goal line
                            g.adjlist[vertex][othervertex] = math.floor((1/inner[vertex] + 1/inner[othervertex])*30*2**(othervertex[direction(colour)] - vertex[direction(colour)]))
            
            # Add edges for links with infinite capacity
            for link in ownlinks:
                g.adjlist[link.pegs[0].position][link.pegs[1].position] = float("inf")
                g.adjlist[link.pegs[1].position][link.pegs[0].position] = float("inf")
            
            # Add edges for forward boundlinks with high capacity
            for link in boundlinks:
                if link.pegs[0].position[direction(colour)] < link.pegs[1].position[direction(colour)]:
                    g.adjlist[link.pegs[0].position][link.pegs[1].position] = 300
                else:
                    g.adjlist[link.pegs[1].position][link.pegs[0].position] = 300
            
            # Remove edges which cross opponent links
            for link in opplinks:
                midpoint = ((link.pegs[0].position[0] + link.pegs[1].position[0])/2, (link.pegs[0].position[1] + link.pegs[1].position[1])/2)
                point1 = (math.floor(midpoint[0]), math.floor(midpoint[1]))
                point2 = (math.ceil(midpoint[0]), math.ceil(midpoint[1]))
                if point1 in inner and point2 in inner:
                    g.adjlist[point1][point2] = 0
                    g.adjlist[point2][point1] = 0
            
            # If difficulty is Difficult, add edges for effective virtual links with high capacity
            if difficulty == "Difficult":
                for peg in ownpegs:
                    displacement = [(0, 4), (4, 0), (3, 3), (3, -3), (1, 3), (3, 1), (1, -3), (3, -1), (2, 0), (0, 2), (1, 1), (1, -1)]
                    for otherpeg in ownpegs:
                        if (otherpeg.position[0] - peg.position[0], otherpeg.position[1] - peg.position[1]) in displacement:
                            if self.safe(peg.position, otherpeg.position, colour):
                                g.adjlist[peg.position][otherpeg.position] = math.floor(1000*2**(otherpeg.position[direction(colour)] - peg.position[direction(colour)]))
                                g.adjlist[otherpeg.position][peg.position] = math.floor(1000*2**(peg.position[direction(colour)] - otherpeg.position[direction(colour)]))
            return g
    
    # Check if a virtual link between two points is safe from disruption by opponent pegs
    def safe(self, point1, point2, colour):
        data = self.player_data(colour)
        opppegs = data[2]
        threats, centre = threat_space(point1, point2)
        for point in threats + centre:
            if point[1 - direction(colour)] == 0 or point[1 - direction(colour)] == BOARD_SIZE - 1:
                return False
        for opppeg in opppegs:
            if opppeg.position in threats:
                return False
            if opppeg.links != []:
                if opppeg.position in centre:
                    return False
        return True

    # Evaluate a state
    def score(self, colour, difficulty):
        data = self.player_data(colour)
        ownpegs = data[0]
        ownlinks = data[1]
        opppegs = data[2]
        opplinks = data[3]
        oppcolour = data[4]

        # Return trivial evaluations if either player has won
        if self.win_check(colour):
            return float("inf")
        if self.win_check(oppcolour):
            return float("-inf")
        
        score = 0

        # Add scores for good attributes of own position and subtract scores for good attributes of opponent position

        # Add score for each link, rewarding vertical links more than horizontal links
        factor = 10
        if difficulty == "Easy":
            factor = 50 # If difficulty is Easy, reward links more
        for link in ownlinks:
            score += factor*abs(link.pegs[0].position[direction(colour)] - link.pegs[1].position[direction(colour)])
        for link in opplinks:
            score -= factor*abs(link.pegs[0].position[direction(oppcolour)] - link.pegs[1].position[direction(oppcolour)])
        
        # Add score for each component, rewarding components which have more pegs and with larger vertical and horizontal spans
        factor = 1
        if difficulty == "Easy":
            factor = 5 # If difficulty is Easy, reward components more
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
                if peg.position[direction(oppcolour)] > hmax:
                    hmax = peg.position[direction(oppcolour)]
                if peg.position[direction(oppcolour)] < hmin:
                    hmin = peg.position[direction(oppcolour)]
            score += factor*(5*(vmax - vmin)**2 + (hmax - hmin)**2 + 5*len(component)**2) # Reward vertical span more than horizontal span
            # The squared terms encourage merging components as the score of a merged component is greater than the sum of the scores of the separate components
        for component in self.components(oppcolour):
            vmax = 0
            vmin = BOARD_SIZE - 1
            hmax = 0
            hmin = BOARD_SIZE - 1
            for peg in component:
                if peg.position[direction(oppcolour)] > vmax:
                    vmax = peg.position[direction(oppcolour)]
                if peg.position[direction(oppcolour)] < vmin:
                    vmin = peg.position[direction(oppcolour)]
                if peg.position[direction(colour)] > hmax:
                    hmax = peg.position[direction(colour)]
                if peg.position[direction(colour)] < hmin:
                    hmin = peg.position[direction(colour)]
            score -= factor*(5*(vmax - vmin)**2 + (hmax - hmin)**2 + 5*len(component)**2)
        
        # Initialise territories
        innerown = {}
        outerown = {}
        inneropp = {}
        outeropp = {}
        own_boundlinks = []
        opp_boundlinks = []
        for peg in ownpegs:
            outerown[peg.position] = 1
        for peg in opppegs:
            outeropp[peg.position] = 1

        # Check if territory can spread from one point to another without being blocked by opponent links or boundlinks
        def crossing_check(point1, point2, links):
            for link in links:
                if opposite_check(point1, point2, link):
                    return True
            return False
        
        # Spread own territory by one step
        def ownspread():
            newterritory = []
            while outerown != {}:
                point = list(outerown.keys())[0]
                generation = outerown[point]
                innerown[point] = generation
                del outerown[point]

                # Territory can spread within a knight's move distance
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (-2, 0), (2, 0), (0, -2), (0, 2), (-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                    newpoint = (point[0] + dx, point[1] + dy)
                    if newpoint in board and newpoint not in innerown and newpoint not in outerown and newpoint[direction(oppcolour)] != 0 and newpoint[direction(oppcolour)] != BOARD_SIZE - 1:
                        if newpoint not in inneropp and newpoint not in outeropp and newpoint not in newterritory:
                            if not crossing_check(point, newpoint, opplinks + opp_boundlinks):
                                newterritory.append(newpoint)

                                # If newpoint is a knight's move away from point, check if any opponent territory is nearby and if so, add a boundlink to prevent opponent from crossing through
                                if {abs(newpoint[0] - point[0]), abs(newpoint[1] - point[1])} == {1, 2}:
                                    midpoint = ((newpoint[0] + point[0])/2, (newpoint[1] + point[1])/2)
                                    point1 = (math.floor(midpoint[0]), math.floor(midpoint[1]))
                                    point2 = (math.ceil(midpoint[0]), math.ceil(midpoint[1]))
                                    if abs(newpoint[0] - point[0]) == 1:
                                        point3 = (point[0], newpoint[1])
                                    else:
                                        point3 = (newpoint[0], point[1])
                                    if point1 in inneropp or point1 in outeropp or point2 in inneropp or point2 in outeropp or point3 in inneropp or point3 in outeropp:
                                        own_boundlinks.append(Link((Peg(point), Peg(newpoint))))
            
            for point in newterritory:
                outerown[point] = generation + 1
        
        # Spread opponent territory by one step
        def oppspread():
            newterritory = []
            while outeropp != {}:
                point = list(outeropp.keys())[0]
                generation = outeropp[point]
                inneropp[point] = generation
                del outeropp[point]
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (-2, 0), (2, 0), (0, -2), (0, 2), (-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                    newpoint = (point[0] + dx, point[1] + dy)
                    if newpoint in board and newpoint not in inneropp and newpoint not in outeropp and newpoint[direction(colour)] != 0 and newpoint[direction(colour)] != BOARD_SIZE - 1:
                        if newpoint not in innerown and newpoint not in outerown and newpoint not in newterritory:
                            if not crossing_check(point, newpoint, ownlinks + own_boundlinks):
                                newterritory.append(newpoint)
                                if {abs(newpoint[0] - point[0]), abs(newpoint[1] - point[1])} == {1, 2}:
                                    midpoint = ((newpoint[0] + point[0])/2, (newpoint[1] + point[1])/2)
                                    point1 = (math.floor(midpoint[0]), math.floor(midpoint[1]))
                                    point2 = (math.ceil(midpoint[0]), math.ceil(midpoint[1]))
                                    if abs(newpoint[0] - point[0]) == 1:
                                        point3 = (point[0], newpoint[1])
                                    else:
                                        point3 = (newpoint[0], point[1])
                                    if point1 in innerown or point1 in outerown or point2 in innerown or point2 in outerown or point3 in innerown or point3 in outerown:
                                        opp_boundlinks.append(Link((Peg(point), Peg(newpoint))))
            for point in newterritory:
                outeropp[point] = generation + 1
        
        # Spread territories alternatively until no more spreading is possible, with the player to move spreading first
        if self.turn == colour:
            for i in range(2*BOARD_SIZE):
                ownspread()
                oppspread()
                if outerown == {} and outeropp == {}:
                    break
        if self.turn == oppcolour:
            for i in range(2*BOARD_SIZE):
                oppspread()
                ownspread()
                if outerown == {} and outeropp == {}:
                    break
        
        # Add scores based on territories, rewarding territory with closer control
        for point in innerown:
            score += 30//innerown[point]
        for point in inneropp:
            score -= 30//inneropp[point]
        
        # Add scores based on max flow in the graph
        factor = 100
        if difficulty == "Easy":
            factor = 10 # If difficulty is Easy, reward max flow less
        owngraph = self.graph(innerown, own_boundlinks, colour, difficulty)
        score += factor*owngraph.max_flow()
        oppgraph = self.graph(inneropp, opp_boundlinks, oppcolour, difficulty)
        score -= factor*oppgraph.max_flow()

        return score
    
    # Return the move CPU makes given a state
    def move(self, difficulty):
        colour = self.turn
        max_score = float("-inf")
        best_move = None
        for move in state.possible_moves(difficulty):
            lastpeg = state.lastpeg
            state.play(move)
            score = self.score(colour, difficulty)
            state.undo(move)
            state.lastpeg = lastpeg
            if score > max_score:
                max_score = score
                best_move = move
        return best_move

# Implement GUI
import tkinter as tk
import json
import os

# Define colours for hover effects on buttons
HOVER_COLOURS = {"lime": "#99ff99", "yellow": "#ffff99", "red": "#ff9999", "cyan": "#99ffff"}

# Initialise global variables
state = None
game_in_play = False
user_colour = None
two_player = False

# Create the main window and frames
root = tk.Tk()
root.title("Twixt")
root.attributes("-fullscreen", True)
HEIGHT = root.winfo_screenheight()
canvas = tk.Canvas(root, width = HEIGHT, height = HEIGHT, bg = "gold")
canvas.pack(side = "left")
control_frame = tk.Frame(root, bg = "teal")
control_frame.pack(side = "right", fill = "both", expand = True)
title = tk.Label(control_frame, text = "Twixt", font = ("Times", 24, "italic"), bg = "teal", fg = "white")
title.pack(pady = 10)
middle_frame = tk.Frame(control_frame, bg="teal")
middle_frame.pack(pady=10, anchor = "w")
labels_frame = tk.Frame(middle_frame, bg="teal", width = 50)
labels_frame.pack(side="left", padx = (20, 0))
buttons_frame = tk.Frame(middle_frame, bg="teal")
buttons_frame.pack(side="right", padx = 100)

# Create labels and buttons
p1_label = tk.Label(control_frame, text = "", fg = "red", bg = "white")
p2_label = tk.Label(control_frame, text = "", fg = "blue", bg = "white")
turn_label = tk.Label(control_frame, text = "", bg = "white")
difficulty_label = tk.Label(control_frame, text = "", fg = "lime", bg = "white")
continue_game_button = tk.Button(buttons_frame, text = "Continue Game", bg = "cyan", width = 20, height = 2)
if os.path.exists("savegame.json"):
    if json.load(open("savegame.json", "r")) != {}:
        continue_game_button.pack(pady = 20)
restart_button = tk.Button(buttons_frame, text = "New Game", bg = "lime", width = 20, height = 2)
restart_button.pack(pady = 20)
rules_button = tk.Button(buttons_frame, text = "Rules", bg = "yellow", width = 20, height = 2)
rules_button.pack(pady = 20)
quit_button = tk.Button(buttons_frame, text = "Quit", bg = "red", fg = "white", width = 20, height = 2)
quit_button.pack(pady = 20)

# Constants
MARGIN = 70
SPACING = (HEIGHT - 2*MARGIN)/(BOARD_SIZE - 1)
TOP_LINE = MARGIN + SPACING/2
BOTTOM_LINE = HEIGHT - TOP_LINE
WIDTH = 2
WIDER = 4
WIDEST = 5
SENSITIVITY = 0.35

# Draw the grid
def draw_board(gamestate, canvas, turn_label, user_colour):
    global two_player
    redwinpath = gamestate.win_path("r")
    bluewinpath = gamestate.win_path("b")
    canvas.delete("all")

    # Draw start and goal lines
    canvas.create_line(TOP_LINE, TOP_LINE, BOTTOM_LINE, TOP_LINE, fill = "red", width = WIDTH)
    canvas.create_line(TOP_LINE, BOTTOM_LINE, BOTTOM_LINE, BOTTOM_LINE, fill = "red", width = WIDTH)
    canvas.create_line(TOP_LINE, TOP_LINE, TOP_LINE, BOTTOM_LINE, fill = "blue", width = WIDTH)
    canvas.create_line(BOTTOM_LINE, TOP_LINE, BOTTOM_LINE, BOTTOM_LINE, fill = "blue", width = WIDTH)
    
    # Draw empty holes
    for (i, j) in gamestate.emptyholes:
        x = MARGIN + i*SPACING
        y = MARGIN + j*SPACING
        canvas.create_oval(x - WIDTH, y - WIDTH, x + WIDTH, y + WIDTH, fill = "black")
    
    # Draw pegs
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
    
    # Draw links
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
        if two_player:
            turn_label.config(text = "Player 1 Won!", fg = "firebrick")
        else:
            if user_colour == "r":
                turn_label.config(text = "You Won!", fg = "firebrick")
            else:
                turn_label.config(text = "CPU Won", fg = "firebrick")
    elif gamestate.win_check("b"):
        if two_player:
            turn_label.config(text = "Player 2 Won!", fg = "mediumblue")
        else:
            if user_colour == "r":
                turn_label.config(text = "CPU Won", fg = "mediumblue")
            else:
                turn_label.config(text = "You Won!", fg = "mediumblue")
    elif gamestate.draw_check():
        turn_label.config(text = "Draw", fg = "magenta")
    else:
        if two_player:
            if gamestate.turn == "r":
                turn_label.config(text = "Player 1's Turn", fg = "darkred")
            else:
                turn_label.config(text = "Player 2's Turn", fg = "darkblue")
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

    # Start the game with selected options
    def start_game():
        global state
        global user_colour
        global game_in_play
        global two_player

        if (player.get() == "None" and difficulty.get() != "Two Player") or difficulty.get() == "None":
            return
        
        state = Gamestate()
        if player.get() == "P1":
            user_colour = "r"
        elif player.get() == "P2":
            user_colour = "b"
        elif player.get() == "Random":
            user_colour = random.choice(["r", "b"])
        elif difficulty.get() == "Two Player":
            user_colour = None
        
        difficulty_label.config(text = difficulty.get())
        
        two_player = False
        game_in_play = True

        json.dump({}, open("savegame.json", "w")) # Clear save file when starting a new game
        continue_game_button.pack_forget()
        
        if difficulty.get() == "Two Player":
            two_player = True
            p1_label.config(text = "Player 1")
            p2_label.config(text = "Player 2")
        else:
            if user_colour == "r":
                p1_label.config(text = "Player 1 (You)")
                p2_label.config(text = "Player 2 (CPU)")
            else:
                p1_label.config(text = "Player 1 (CPU)")
                p2_label.config(text = "Player 2 (You)")
        
        p1_label.pack(in_=labels_frame, pady = 5)
        p2_label.pack(in_=labels_frame, pady = 5)
        turn_label.pack(in_=labels_frame, pady = 10)
        difficulty_label.pack(in_=labels_frame, pady = 10)
        restart_button.config(text = "Restart") # Change text of New Game button to Restart when game is in play
        draw_board(state, canvas, turn_label, user_colour)
        popup.destroy()
        root.update()
        root.after(1000, CPU_move)
    
    tk.Label(popup, text = "Select Difficulty").pack(pady = 5)
    tk.Radiobutton(popup, text = "Easy", variable = difficulty, value = "Easy").pack()
    tk.Radiobutton(popup, text = "Medium", variable = difficulty, value = "Medium").pack()
    tk.Radiobutton(popup, text = "Difficult", variable = difficulty, value = "Difficult").pack()
    tk.Radiobutton(popup, text = "Two Player", variable = difficulty, value = "Two Player").pack()

    tk.Label(popup, text = "Select Player").pack(pady = 5)
    tk.Radiobutton(popup, text = "Player 1 (Red)", variable = player, value = "P1").pack()
    tk.Radiobutton(popup, text = "Player 2 (Blue)", variable = player, value = "P2").pack()
    tk.Radiobutton(popup, text = "Random", variable = player, value = "Random").pack()

    tk.Button(popup, text = "Start", command = start_game).pack(pady = 10)

restart_button.config(text = "New Game", command = new_game_popup)

# Respond to user clicking on a peg and play the move if click is valid
def click_board(event):
    global state
    global game_in_play
    global user_colour
    global two_player

    # Return if user is not allowed to play
    if not game_in_play:
        return
    if state.win_check("r") or state.win_check("b") or state.draw_check():
        return
    if not state.turn == user_colour and not two_player:
        return
    
    # Check if click is close enough to a hole and if so, round to the nearest hole
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
    
    # Play the move if it is valid and update the board
    if (i, j) in state.emptyholes:
        if state.valid((i, j)):
            state.play((i, j))
            draw_board(state, canvas, turn_label, user_colour)

canvas.bind("<Button-1>", click_board)

# Respond to user hovering over a peg and show a preview of the peg and links that would be formed if the user clicks
def hover_board(event):
    global state
    global game_in_play
    global user_colour
    global two_player

    canvas.delete("hover")

    # Return if user is not allowed to play
    if not game_in_play:
        return
    if state.win_check("r") or state.win_check("b") or state.draw_check():
        return
    if state.turn != user_colour and not two_player:
        return
    
    # Check if hover is close enough to a hole and if so, round to the nearest hole
    i = (event.x - MARGIN) / SPACING
    j = (event.y - MARGIN) / SPACING
    if abs(i - round(i)) < SENSITIVITY:
        i = round(i)
    else:
        i = BOARD_SIZE
    if abs(j - round(j)) < SENSITIVITY:
        j = round(j)
    else:
        j = BOARD_SIZE
    
    # Show preview of peg and links if hover is over a valid hole
    if (i, j) in state.emptyholes and state.valid((i, j)):
        x = MARGIN + i * SPACING
        y = MARGIN + j * SPACING
        if state.turn == "r":
            fill_colour = "#ff9999"
        else:
            fill_colour = "#9999ff"
        canvas.create_oval(x - WIDEST, y - WIDEST, x + WIDEST, y + WIDEST, fill = fill_colour, outline = "lime", width=2, tags="hover")
        data = state.player_data(state.turn)
        ghost = Peg((i, j))
        ownpegs = data[0]
        opplinks = data[3]
        for peg in ownpegs:
            if knight_check(peg, ghost):
                newlink = Link((peg, ghost))
                valid = True
                for opplink in opplinks:
                    if intersect_check(newlink, opplink):
                        valid = False
                        break
                if valid:
                    x1 = MARGIN + peg.position[0] * SPACING
                    y1 = MARGIN + peg.position[1] * SPACING
                    canvas.create_line(x1, y1, x, y, fill=fill_colour, width=WIDER, tags="hover")

canvas.bind("<Motion>", hover_board)
canvas.bind("<Leave>", lambda e: canvas.delete("hover"))

# CPU move
def CPU_move():
    global state
    global difficulty
    global user_colour
    global two_player

    if not state.win_check("r") and not state.win_check("b") and not state.draw_check():
        if state.turn != user_colour and not two_player:
            state.play(state.move(difficulty.get()))
            draw_board(state, canvas, turn_label, user_colour)
        root.after(1000, CPU_move)

# Configurate popup when pressing Rules button
rules_popup_window = None
def rules_popup():
    global rules_popup_window

    # If rules popup is already open, bring it to the front instead of opening a new one
    if rules_popup_window and rules_popup_window.winfo_exists():
        rules_popup_window.lift()
        rules_popup_window.focus_force()
        return
    
    popup = tk.Toplevel(root)
    rules_popup_window = popup
    popup.title("Game Rules")
    popup.geometry("300x350")
    popup.attributes("-topmost", True)
    root.update_idletasks()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    popup.geometry(f"+{root_x+900}+{root_y+400}")

    def close_popup():
        global rules_popup_window
        rules_popup_window = None
        popup.destroy()
    
    popup.protocol("WM_DELETE_WINDOW", close_popup)
    text = tk.Text(popup, wrap="word", bg="#ffff99", fg="black", font=("Arial", 11), height = 9)
    text.pack(side="top", fill="both", expand=True, padx=5, pady=5)

    rules_text = """Twixt Rules:
1. The board is a 24x24 grid with the four corners removed.
2. Players take turns placing pegs on empty holes.
3. Pegs are connected by links in a knight's move pattern (2 by 1).
4. Links cannot cross opponent links.
5. The goal is to create a continuous path from your start line to your goal line.
6. Red player connects top to bottom; Blue player connects left to right.
7. You cannot place pegs behind your opponent's start or goal lines.
8. The most recent peg is highlighted with a lime ring."""

    # Insert rules text and add colour and formatting to different parts of the text
    text.insert("1.0", rules_text)
    text.tag_add("header", "1.0", "1.11")
    text.tag_config("header", foreground="orange", font=("Arial", 12, "bold"))
    text.tag_add("Red", "7.3", "7.6")
    text.tag_config("Red", foreground="red", font=("Arial", 11, "bold"))
    text.tag_add("Blue", "7.38", "7.42")
    text.tag_config("Blue", foreground="blue", font=("Arial", 11, "bold"))
    text.tag_add("lime", "9.45", "9.49")
    text.tag_config("lime", foreground="lime", font=("Arial", 11, "bold"))
    for i in range(2, 10):
        text.tag_add(f"point{i}", f"{i}.0", f"{i}.1")
        text.tag_config(f"point{i}", foreground="magenta", font=("Arial", 11, "bold"))
    text.config(state="disabled")

    tk.Button(popup, text="Close", command=close_popup).pack(side="bottom", pady=5)

rules_button.config(command = rules_popup)

# Configurate popup when pressing Quit button
def quit_popup():
    global game_in_play
    if not game_in_play:
        root.quit()
        return
    
    popup = tk.Toplevel(root)
    popup.title("Quit Game")
    popup.geometry("300x200")
    popup.transient(root)
    popup.grab_set()
    popup.focus_set()
    root.update_idletasks()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    popup.geometry(f"+{root_x+620}+{root_y+300}")

    tk.Label(popup, text = "Do you want to save the current game?", bg = "white").pack(pady = 20)
    tk.Button(popup, text = "Save", command = save_game, bg = "green", fg = "white").pack(padx = 20, pady = 10)
    tk.Button(popup, text = "Don't Save", command = root.quit, bg = "red", fg = "white").pack(padx = 20, pady = 10)
    tk.Button(popup, text = "Cancel", command = popup.destroy, bg = "grey", fg = "white").pack(padx = 20, pady = 10)
quit_button.config(command = quit_popup)

# Save game state to a JSON file
def save_game():
    data = {"redpegs": [peg.position for peg in state.redpegs], "bluepegs": [peg.position for peg in state.bluepegs], "redlinks": [(link.pegs[0].position, link.pegs[1].position) for link in state.redlinks], "bluelinks": [(link.pegs[0].position, link.pegs[1].position) for link in state.bluelinks], "turn": state.turn, "difficulty": difficulty.get(), "user_colour": user_colour, "lastpeg": state.lastpeg.position if state.lastpeg is not None else None}
    with open("savegame.json", "w") as f:
        json.dump(data, f)
    root.quit()

# Load game state from a JSON file and continue the game
def continue_game():
    global state
    global user_colour
    global difficulty
    global game_in_play
    global two_player
    game_in_play = True

    with open("savegame.json", "r") as f:
        data = json.load(f)
        json.dump({}, open("savegame.json", "w"))
    
    state = Gamestate()
    peg_lookup = {}
    for pos in data["redpegs"]:
        peg = Peg(tuple(pos))
        state.redpegs.append(peg)
        peg_lookup[tuple(pos)] = peg
    for pos in data["bluepegs"]:
        peg = Peg(tuple(pos))
        state.bluepegs.append(peg)
        peg_lookup[tuple(pos)] = peg
    for p1, p2 in data["redlinks"]:
        link = Link((peg_lookup[tuple(p1)], peg_lookup[tuple(p2)]))
        state.redlinks.append(link)
    for p1, p2 in data["bluelinks"]:
        link = Link((peg_lookup[tuple(p1)], peg_lookup[tuple(p2)]))
        state.bluelinks.append(link)
    for peg in state.redpegs + state.bluepegs:
        if peg.position in state.emptyholes:
            state.emptyholes.remove(peg.position)
    state.turn = data["turn"]
    if data["lastpeg"] is not None:
        state.lastpeg = peg_lookup[tuple(data["lastpeg"])]
    difficulty = tk.StringVar()
    difficulty.set(data["difficulty"])
    if data["difficulty"] == "Two Player":
        two_player = True
    user_colour = data["user_colour"]
    if two_player:
        p1_label.config(text = "Player 1")
        p2_label.config(text = "Player 2")
    else:
        if user_colour == "r":
            p1_label.config(text = "Player 1 (You)")
            p2_label.config(text = "Player 2 (CPU)")
        else:
            p1_label.config(text = "Player 1 (CPU)")
            p2_label.config(text = "Player 2 (You)")
    p1_label.pack(in_=labels_frame, pady = 5)
    p2_label.pack(in_=labels_frame, pady = 5)
    turn_label.pack(in_=labels_frame, pady = 10)
    difficulty_label.pack(in_=labels_frame, pady = 10)
    difficulty_label.config(text = difficulty.get())
    restart_button.config(text = "Restart")
    draw_board(state, canvas, turn_label, user_colour)
    continue_game_button.pack_forget()
    CPU_move()

continue_game_button.config(command = continue_game)

# Add hover effects to buttons
def button_hover(event):
    bg = event.widget["bg"]
    event.widget.config(bg=HOVER_COLOURS[bg])

# Reset button colour when mouse leaves
def button_leave(event):
    bg = event.widget["bg"]
    for original, hover in HOVER_COLOURS.items():
        if bg == hover:
            event.widget.config(bg=original)

# Bind hover effects to buttons
for button in [continue_game_button, restart_button, rules_button, quit_button]:
    button.bind("<Enter>", button_hover)
    button.bind("<Leave>", button_leave)

# Start the main event loop
tk.mainloop()
