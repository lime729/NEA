import copy
board = []
for i in range(24):
    for j in range(24):
        if not ((i == 0 or i == 23) and (j == 0 or j == 23)):
            board.append((i, j))
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
    def play(self, move):
        newstate = copy.deepcopy(self)
        newstate.emptyholes.remove(move)
        newpeg = Peg(move)
        if newstate.turn == "r":
            for redpeg in newstate.redpegs:
                if knight_check(redpeg, newpeg):
                    newlink = Link((redpeg, newpeg))
                    check = True
                    for bluelink in newstate.bluelinks:
                        if intersect_check(newlink, bluelink):
                            check = False
                    if check:
                        newstate.redlinks.append(newlink)
                        redpeg.links.append(newlink)
                        newpeg.links.append(newlink)
            newstate.redpegs.append(newpeg)
            newstate.turn = "b"
        else:
            for bluepeg in newstate.bluepegs:
                if knight_check(bluepeg, newpeg):
                    newlink = Link((bluepeg, newpeg))
                    check = True
                    for redlink in newstate.redlinks:
                        if intersect_check(newlink, redlink):
                            check = False
                    if check:
                        newstate.bluelinks.append(newlink)
                        bluepeg.links.append(newlink)
                        newpeg.links.append(newlink)
            newstate.bluepegs.append(newpeg)
            newstate.turn = "r"
        return newstate
    def red_components(self):
        red = []
        for peg in self.redpegs:
            red.append([peg])
        for link in self.redlinks:
            peg1 = link.pegs[0]
            peg2 = link.pegs[1]
            for component in red:
                if peg1 in component:
                    component1 = component
                if peg2 in component:
                    component2 = component
            if component1 != component2:
                red.remove(component1)
                red.remove(component2)
                red.append(component1 + component2)
        return red
    def red_win_check(self):
        for component in self.red_components():
            topcheck = False
            bottomcheck = False
            for peg in component:
                if peg.position[1] == 23:
                    topcheck = True
                if peg.position[1] == 0:
                    bottomcheck = True
                if topcheck and bottomcheck:
                    return True
        return False
    def blue_components(self):
        blue = []
        for peg in self.bluepegs:
            blue.append([peg])
        for link in self.bluelinks:
            peg1 = link.pegs[0]
            peg2 = link.pegs[1]
            for component in blue:
                if peg1 in component:
                    component1 = component
                if peg2 in component:
                    component2 = component
            if component1 != component2:
                blue.remove(component1)
                blue.remove(component2)
                blue.append(component1 + component2)
        return blue
    def blue_win_check(self):
        for component in self.blue_components():
            leftcheck = False
            rightcheck = False
            for peg in component:
                if peg.position[0] == 0:
                    leftcheck = True
                if peg.position[0] == 23:
                    rightcheck = True
                if leftcheck and rightcheck:
                    return True
        return False
    def redscore(self, mode):
        if self.red_win_check():
            return 1000000
        if self.blue_win_check():
            return -1000000
        score = 0
        score = score + len(self.redlinks)
        score = score - len(self.bluelinks)
        