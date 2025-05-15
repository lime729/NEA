import copy
board = []
for i in range(24):
    for j in range(24):
        if not ((i == 0 or i == 23) and (j == 0 or j == 23)):
            board.append((i, j))
def direction(colour):
    if colour == "r":
        return 1
    else:
        return 0
class Peg:
    def __init__(self, position):
        self.position = position
        self.links = []
def knight_check(peg1, peg2):
    return ({abs(peg1.position[0] - peg2.position[0]), abs(peg1.position[1] - peg2.position[1])} == {1, 2})
class Link:
    def __init__(self, pegs):
        self.pegs = pegs
def intersect_check(link1, link2):
    def anticlockwise_check(peg1, peg2, peg3):
        return peg1.position[0]*peg2.position[1] + peg2.position[0]*peg3.position[1] + peg3.position[0]*peg1.position[1] - peg1.position[1]*peg2.position[0] - peg2.position[1]*peg3.position[0] - peg3.position[1]*peg1.position[0] > 0
    link1peg1 = link1.pegs[0]
    link1peg2 = link1.pegs[1]
    link2peg1 = link2.pegs[0]
    link2peg2 = link2.pegs[1]
    return (anticlockwise_check(link1peg1, link1peg2, link2peg1) != anticlockwise_check(link1peg1, link1peg2, link2peg2)) and (anticlockwise_check(link2peg1, link2peg2, link1peg1) != anticlockwise_check(link2peg1, link2peg2, link1peg2))
class Gamestate:
    def __init__(self):
        self.emptyholes = board[:]
        self.redpegs = []
        self.bluepegs = []
        self.redlinks = []
        self.bluelinks = []
        self.turn = "r"
    def player_data(self, colour):
        if colour == "r":
            return (self.redpegs, self.redlinks, self.bluepegs, self.bluelinks, "b")
        else:
            return (self.bluepegs, self.bluelinks, self.redpegs, self.redlinks, "r")
    def play(self, move):
        newstate = copy.deepcopy(self)
        newstate.emptyholes.remove(move)
        newpeg = Peg(move)
        data = newstate.player_data(newstate.turn)
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
        newstate.turn = opponentcolour
        return newstate
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
    def win_check(self, colour):
        for component in self.components(colour):
            startcheck = False
            endcheck = False
            for peg in component:
                if peg.position[direction(colour)] == 0:
                    startcheck = True
                if peg.position[direction(colour)] == 23:
                    endcheck = True
                if startcheck and endcheck:
                    return True
        return False
    def score(self, colour, mode):
        data = self.player_data(colour)
        ownpegs = data[0]
        ownlinks = data[1]
        opponentpegs = data[2]
        opponentlinks = data[3]
        opponentcolour = data[4]
        if self.win_check(colour):
            return 1000000
        if self.win_check(opponentcolour):
            return -1000000
        score = 0
        for link in ownlinks:
            score += abs(link.pegs[0].position[direction(colour)] - link.pegs[1].position[direction(colour)])
        for link in opponentlinks:
            score -= abs(link.pegs[0].position[direction(opponentcolour)] - link.pegs[1].position[direction(opponentcolour)])
        