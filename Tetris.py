import time
from copy import copy

BOARD_HEIGHT = 8
BOARD_WIDTH = 8

def unshared_copy(inList):
    if isinstance(inList, list):
        return list( map(unshared_copy, inList) )
    return inList


class Tetris:

    def __init__(self, emitter):
        self.board = [['.' for _ in range(BOARD_WIDTH)] for x in range(BOARD_HEIGHT)]
        self.gameResults = []
        self.emitter = emitter

    def dropPiece(self, pos, piecech, degrees):
        if piecech == 'i':
            piece = [[1],[1],[1],[1]]
        elif piecech == 'j':
            piece = [[0,1],[0,1],[1,1]]
        elif piecech == 'l':
            piece = [[1,0],[1,0],[1,1]]
        elif piecech == 'o':
            piece = [[1,1],[1,1]]
        elif piecech == 's':
            piece = [[0,1,1],[1,1,0]]
        elif piecech == 't':
            piece = [[1,1,1],[0,1,0]]
        elif piecech == 'z':
            piece = [[1,1,0],[0,1,1]]

        rotated = self.rotatePiece(piece, degrees)

        height = len(rotated)
        width = len(rotated[0])
        maxpos = BOARD_WIDTH - width         #what's the furthest along this piece could go
        pos = min([pos, maxpos])    # bring in a piece that's too far right

        # array of heights of every column
        boardheight = [0  for i in range(width)]
        for x in range(width):
            for y in range(BOARD_HEIGHT):
                if self.board[y][pos + x] != '.':
                    boardheight[x] = y+1


        # array of heights of the piece
        pieceheight = [0 for i in range(width)]
        for x in range(width):
            for y in range(height):
                if rotated[y][x] == 1:
                    pieceheight[x] = y+1

        # work out the max heights, this is where the piece will fall to
        sum = [boardheight[i]+pieceheight[i] for i in range(width)]
        if max(sum) > BOARD_HEIGHT:
            return False  # full board

        destx, desty = pos, max(sum)-1

        for n in range(BOARD_HEIGHT-1, desty, -1):
            frame = unshared_copy(self.board)
            for y in range(len(rotated)):
                for x in range(len(rotated[y])):
                    if rotated[y][x]==1:
                        frame[n-y][destx+x] = piecech
            squares = self.boardToLights(frame)
            self.emitter.emit('my response', squares, namespace='/test')
            time.sleep(0.5)

        # copy the rotated piece to its dest on the board
        for y in range(len(rotated)):
            for x in range(len(rotated[y])):
                if rotated[y][x]==1:
                    self.board[desty-y][destx+x] = piecech
        squares = self.boardToLights(self.board)
        self.emitter.emit('my response', squares, namespace='/test')
        time.sleep(0.5)

        # test for rows to remove - could be a bit more efficient: break out when u hit a blank row
        row = BOARD_HEIGHT - 1
        rowsremoved = 0
        while (row >= 0 ):
            allfull = True
            for x in self.board[row]:
                if (x == '.'):
                    allfull = False
                    break
            if allfull:
                self.board[row] = ['f1' for _ in range(BOARD_WIDTH)]
                squares = self.boardToLights(self.board)
                self.emitter.emit('my response', squares, namespace='/test')
                time.sleep(0.25)
                self.board[row] = ['f2' for _ in range(BOARD_WIDTH)]
                squares = self.boardToLights(self.board)
                self.emitter.emit('my response', squares, namespace='/test')
                time.sleep(0.25)

                del self.board[row]
                self.board.append(['.' for _ in range(BOARD_WIDTH)])
                rowsremoved += 1
            else:
                row -= 1

        squares = self.boardToLights(self.board)

        self.emitter.emit('my response', squares, namespace='/test')

        return True

    def rotatePiece(self, piece, degrees):
        if degrees == 0:
            piecen = copy(piece)

        for i in range(degrees / 90): #
            piecen = []
            # initialize piecen list to be the rotation of piece
            for y in range(len(piece[0])):
                piecen.append([0 for x in range(len(piece))])

            for y in range(len(piece)):
                for x in range(len(piece[y])):
                        piecen[x][len(piece)-1-y] = piece[y][x]

            piece = copy(piecen)
        return piecen

    def boardToLights(self, board):
        squares = []
        direction = -1
        y = BOARD_HEIGHT - 1;
        for x in range(BOARD_WIDTH):
            for _ in range(BOARD_HEIGHT):
                spot = board[y][x]
                if (spot != '.'):
                    colors = { 'i' : {'r':0x00, 'g':0xe4, 'b':0xe4}, # '#00E4E4',  // line piece
                    'o' : {'r':0xe4, 'g':0xde, 'b':0x00}, # '#E4DE00',  // square piece
                    'j' : {'r':0x00, 'g':0x4e, 'b':0xe4}, # '#004EE4',  // J piece
                    'l' : {'r':0xe4, 'g':0x62, 'b':0x00}, # '#E46200',  // L piece
                    's' : {'r':0x00, 'g':0xe4, 'b':0x27}, # '#00E427',  // S piece
                    'z' : {'r':0xe4, 'g':0x00, 'b':0x27}, # '#E40027',  // Z piece
                    't' : {'r':0x9c, 'g':0x13, 'b':0xe4}, # '#9C13E4'   // T piece
                    'f1' : {'r':0xff, 'g':0xff, 'b':0xff}, #    // flash one
                    'f2' : {'r':0x00, 'g':0x00, 'b':0x00}} #    // flash two
                    squares.append(colors[spot])
                else:
                    squares.append({'r':0, 'g':0, 'b':0})

                #y += direction
                y -= 1
            #y -= direction
            y = BOARD_HEIGHT - 1
            direction = -direction
        return squares;

    def boardToPOSTString(self):
        str = ""
        rows =  ["".join(self.board[y]) for y in range(len(self.board)-1, -1, -1)]
        return " ".join(rows)

    def printBoard(self):
        #print range(len(self.board)-1, -1, -1)
        for y in range(len(self.board)-1, -1, -1):
            for x in range(len(self.board[y])):
                print self.board[y][x],
            print ""
        print " ".join("=" for _ in range(BOARD_WIDTH))
