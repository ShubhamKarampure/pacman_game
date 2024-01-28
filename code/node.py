from settings import *

class Node(object):
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x, y)
        self.neighbours = {UP: None, DOWN: None, LEFT: None, RIGHT: None, PORTAL: None}

    def render(self, window):
        for n in self.neighbours.keys():
            if self.neighbours[n] is not None:
                line_start = self.position
                line_end = self.neighbours[n].position
                pygame.draw.circle(window, "RED", self.position, 4)
                pygame.draw.line(window, "WHITE", line_start, line_end, 1)


# creating node groups and aligning its neighbours
class NodeGroup(object):
    def __init__(self,name):
        # path setup
        self.nodesLUT = {}
        self.homeLUT = {}
        self.createNode()
        self.joinNeighbour()

        if(name != "player"):
            self.home = homedata

            self.createHomeNode()
            self.joinHomeNeighbour()
            self.joinHomeMap()

    def createNode(self):
        for i in range(len(map)):
            for j in range(len(map[i])):
                if map[i][j] == "n" or map[i][j] == "P" or map[i][j] == "N":
                    x, y = self.constructKey(j, i)
                    self.nodesLUT[(x, y)] = Node(x, y)

    def joinNeighbour(self):
        # connecting horizontally
        for row in range(len(map)):
            key = None
            for col in range(len(map[row])):
                if map[row][col] == "n" or map[row][col] == "P" or map[row][col] == "N":
                    if key is None:
                        key = self.constructKey(col, row)
                    else:
                        otherkey = self.constructKey(col, row)
                        self.nodesLUT[key].neighbours[RIGHT] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbours[LEFT] = self.nodesLUT[key]
                        key = otherkey
                elif map[row][col] != "." and map[row][col] != "0":
                    key = None

        # connecting vertically
        mapT = map.transpose()
        for row in range(len(mapT)):
            key = None
            for col in range(len(mapT[row])):
                if (
                    mapT[row][col] == "n"
                    or mapT[row][col] == "P"
                    or mapT[row][col] == "N"
                ):
                    if key is None:
                        key = self.constructKey(row, col)
                    else:
                        otherkey = self.constructKey(row, col)
                        self.nodesLUT[key].neighbours[DOWN] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbours[UP] = self.nodesLUT[key]
                        key = otherkey
                elif (
                    mapT[row][col] != "."
                    and mapT[row][col] != "p"
                    and mapT[row][col] != "0"
                ):
                    key = None

    def createHomeNode(self):
        for i in range(len(self.home)):
            for j in range(len(self.home[i])):
                if (
                    self.home[i][j] == "n"
                ):
                    x, y = self.constructHomeKey(j, i)
                    self.homeLUT[(x, y)] = Node(x, y)

    def joinHomeNeighbour(self):
        # connecting horizontally
        for row in range(len(self.home)):
            key = None
            for col in range(len(self.home[row])):
                if (
                    self.home[row][col] == "n"
                ):
                    if key is None:
                        key = self.constructHomeKey(col, row)
                    else:
                        otherkey = self.constructHomeKey(col, row)
                        self.homeLUT[key].neighbours[RIGHT] = self.homeLUT[otherkey]
                        self.homeLUT[otherkey].neighbours[LEFT] = self.homeLUT[key]
                        key = otherkey
                elif self.home[row][col] != "0":
                    key = None

        # connecting vertically
        homeT = self.home.transpose()
        for row in range(len(homeT)):
            key = None
            for col in range(len(homeT[row])):
                if (
                    homeT[row][col] == "n"
                ):
                    if key is None:
                        key = self.constructHomeKey(row, col)
                    else:
                        otherkey = self.constructHomeKey(row, col)
                        self.homeLUT[key].neighbours[DOWN] = self.homeLUT[otherkey]
                        self.homeLUT[otherkey].neighbours[UP] = self.homeLUT[key]
                        key = otherkey
                elif (
                    homeT[row][col] != "0"
                ):
                    key = None

    def constructKey(self, x, y):
        return (x * TWID) + TWOFST, (y * THGT) + WOFST + THOFST

    def constructHomeKey(self, x, y):
        return (x * TWID) + TWOFST + WWID/2-40, (y * THGT) + WOFST + THOFST+WWID/2-48

    def setPortalPair(self, pair1, pair2):
        key1 = self.constructKey(*pair1)
        key2 = self.constructKey(*pair2)
        if key1 in self.nodesLUT.keys() and key2 in self.nodesLUT.keys():
            self.nodesLUT[key1].neighbours[PORTAL] = self.nodesLUT[key2]
            self.nodesLUT[key2].neighbours[PORTAL] = self.nodesLUT[key1]

    def getNodeFromPixels(self, xpixel, ypixel):
        if (xpixel, ypixel) in self.nodesLUT.keys():
            return self.nodesLUT[(xpixel, ypixel)]
        return None

    def getNodeFromTiles(self, col, row):
        x, y = self.constructKey(col, row)
        if (x, y) in self.nodesLUT.keys():
            return self.nodesLUT[(x, y)]
        return None

    def getHomeNodeFromPixels(self, xpixel, ypixel):
        if (xpixel, ypixel) in self.homeLUT.keys():
            return self.homeLUT[(xpixel, ypixel)]
        return None

    def getHomeNodeFromTiles(self, col, row):
        x, y = self.constructHomeKey(col, row)
        if (x, y) in self.homeLUT.keys():
            return self.homeLUT[(x, y)]
        return None

    def joinHomeMap(self):
        center = self.getHomeNodeFromTiles(2, 0)
        left = self.getNodeFromTiles(13, 12)
        right = self.getNodeFromTiles(16, 12)
        center.neighbours[RIGHT] = right
        center.neighbours[LEFT] = left

        left.neighbours[RIGHT] = center
        right.neighbours[LEFT] = center

    def close_gate(self):
        center = self.getHomeNodeFromTiles(2, 0)
        down = self.getHomeNodeFromTiles(2, 2)
        center.neighbours[DOWN] = None
        down.neighbours[UP] = None

    def open_gate(self):
        center = self.getHomeNodeFromTiles(2, 0)
        down = self.getHomeNodeFromTiles(2, 2)
        center.neighbours[DOWN] = down
        down.neighbours[UP] = center

    def render(self, window):
        for node in self.homeLUT.values():
            node.render(window)
        for node in self.nodesLUT.values():
            node.render(window)
