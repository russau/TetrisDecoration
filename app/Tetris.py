import time
import random
from copy import copy
try:
    from neopixel import *
except ImportError:
    print "non-neopixel"

BOARD_HEIGHT = 16
BOARD_WIDTH = 8

def unshared_copy(inList):
    if isinstance(inList, list):
        return list( map(unshared_copy, inList) )
    return inList

# tetrisbuster code

pieces = {
		'i':[ [ [True, False, False, False],[True, False, False, False],[True, False, False, False],[True, False, False, False] ], [  [True, True, True, True],[False, False, False, False],[False, False, False, False],[False, False, False, False] ], [ [True, False, False, False],[True, False, False, False],[True, False, False, False],[True, False, False, False] ], [ [True, True, True, True],[False, False, False, False],[False, False, False, False],[False, False, False, False] ] ],
		'j':[ [ [False, True, False, False],[False, True, False, False],[True, True, False, False],[False, False, False, False] ], [ [True, False, False, False],[True, True, True, False],[False, False, False, False],[False, False, False, False] ], [ [True, True, False, False],[True, False, False, False],[True, False, False, False],[False, False, False, False] ], [ [True, True, True, False],[False, False, True, False],[False, False, False, False],[False, False, False, False] ] ],
		'l':[ [ [True, False, False, False],[True, False, False, False],[True, True, False, False],[False, False, False, False] ], [ [True, True, True, False],[True, False, False, False],[False, False, False, False],[False, False, False, False] ], [ [True, True, False, False],[False, True, False, False],[False, True, False, False],[False, False, False, False] ], [ [False, False, True, False],[True, True, True, False],[False, False, False, False],[False, False, False, False] ] ],
		'o':[ [ [True, True, False, False],[True, True, False, False],[False, False, False, False],[False, False, False, False] ], [  [True, True, False, False],[True, True, False, False],[False, False, False, False],[False, False, False, False] ], [  [True, True, False, False],[True, True, False, False],[False, False, False, False],[False, False, False, False] ], [  [True, True, False, False],[True, True, False, False],[False, False, False, False],[False, False, False, False] ] ],
		's':[ [ [False, True, True, False],[True, True, False, False],[False, False, False, False],[False, False, False, False] ], [  [True, False, False, False],[True, True, False, False],[False, True, False, False],[False, False, False, False] ], [ [False, True, True, False],[True, True, False, False],[False, False, False, False],[False, False, False, False] ], [ [True, False, False, False],[True, True, False, False],[False, True, False, False],[False, False, False, False] ] ],
		't':[ [ [True, True, True, False],[False, True, False, False],[False, False, False, False],[False, False, False, False] ], [ [False, True, False, False],[True, True, False, False],[False, True, False, False],[False, False, False, False] ], [ [False, True, False, False],[True, True, True, False],[False, False, False, False],[False, False, False, False] ], [ [True, False, False, False],[True, True, False, False],[True, False, False, False],[False, False, False, False] ], ],
		'z':[ [ [True, True, False, False],[False, True, True, False],[False, False, False, False],[False, False, False, False] ], [ [False, True, False, False],[True, True, False, False],[True, False, False, False],[False, False, False, False] ], [ [True, True, False, False],[False, True, True, False],[False, False, False, False],[False, False, False, False] ], [ [False, True, False, False],[True, True, False, False],[True, False, False, False],[False, False, False, False] ], ],
	}

board_height = 16
board_width = 8

def getPositionAndDegrees(board, piece):
	board = board.split()

	outstr = ""

	# try every combination and compute a score for that combo.
	combos = {}
	for x in range(board_width):
		for rot in range(4):
			new_board, legal = doMove(board, piece, x, rot)
			if legal:
				# determine how many points this board is worth
				pts = 0
				for by in range(board_height):
					# negative score for each block, blocks toward the bottom
					# don't hurt as much
					pts += sum(-10*(board_height-by) for char in new_board[by] if char != ".")
					# find holes and give them a penalty
					for bx in range(board_width):
						if new_board[by][bx] == '.':
							# see if there is a block anywhere above it
							for check_y in range(by):
								if new_board[check_y][bx] != ".":
									pts -= 50 * (board_height-check_y)
									break

				combos[pts] = [x, rot]

	# best combo is lowest key
	keys = combos.keys()
	keys.sort(reverse=True)

	# log
	if len(keys) > 0:
		new_board, legal = doMove(board, piece, combos[keys[0]][0],  combos[keys[0]][1])
		outstr += "\nexpected board:\n%s" % '\n'.join(new_board)
#	open('lastrun.txt', 'a').write("\n---------------------\nboard:\n%s\npiece: %s\n combos: %s\noutstr: %s\n" % ('\n'.join(board), piece, combos, outstr))

	if len(keys) == 0:
		# random, we're about to lose
		position = 0
		degrees = 0
	else:
		position = combos[keys[0]][0]
		degrees = combos[keys[0]][1] * 90
	return position, degrees

def canPutPiece(board, piece, left, top, rot):
	new_board = board[:]

	for y in range(4):
		for x in range(4):
			bx = left+x
			by = top+y


			if pieces[piece][rot][y][x]:
				if by >= board_height or bx >= board_width or \
				bx < 0 or by < 0 or board[by][bx] != '.':
					return (board, False,) # illegal move
				else:
					row = list(new_board[by])
					row[bx] = piece
					new_board[by] = ''.join(row)

	return (new_board, True,) # legal move

def doMove(board, piece, position, rot):
	# put piece at top of board
	y = 0

	# move piece down until we can't anymore
	new_board = board[:]
	while True:
		ret_board = new_board[:]
		new_board, legal = canPutPiece(board, piece, position, y, rot)
		if not legal:
			break

		y += 1

	# delete complete rows
	ret_board = filter(lambda row: any(item == '.' for item in row), ret_board)
	for i in range(board_height-len(ret_board)):
		ret_board.insert(0, '.' * board_width)


	if y == 0:
		# cannot place piece; return illegal move
		return (board, False,)
	else:
		# put the changes into board
		return (ret_board, True,) # 'True' - move is legal


class Tetris:

    def __init__(self, emitter):
        self.board = [['.' for _ in range(BOARD_WIDTH)] for x in range(BOARD_HEIGHT)]
        self.gameResults = []
        self.emitter = emitter

    def dropRandom(self):
        piece = random.choice(['i','j','l','o','s','t','z'])
        position, degrees = getPositionAndDegrees(self.boardToPOSTString(), piece)
        return self.dropPiece(position, piece, degrees)

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
            #self.emitter.emit('my response', squares, namespace='/test')
            self.emitter(squares)
            time.sleep(0.5)

        # copy the rotated piece to its dest on the board
        for y in range(len(rotated)):
            for x in range(len(rotated[y])):
                if rotated[y][x]==1:
                    self.board[desty-y][destx+x] = piecech
        squares = self.boardToLights(self.board)
        #self.emitter.emit('my response', squares, namespace='/test')
        self.emitter(squares)
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
                #self.emitter.emit('my response', squares, namespace='/test')
                self.emitter(squares)
                time.sleep(0.25)
                self.board[row] = ['f2' for _ in range(BOARD_WIDTH)]
                squares = self.boardToLights(self.board)
                #self.emitter.emit('my response', squares, namespace='/test')
                self.emitter(squares)
                time.sleep(0.25)

                del self.board[row]
                self.board.append(['.' for _ in range(BOARD_WIDTH)])
                rowsremoved += 1
            else:
                row -= 1

        squares = self.boardToLights(self.board)
        #self.emitter.emit('my response', squares, namespace='/test')
        self.emitter(squares)

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
        array_pos = -1;
        squares = [{'r':0, 'g':0, 'b':0}] * BOARD_WIDTH * BOARD_HEIGHT
        direction = -1
        y = BOARD_HEIGHT - 1;
        for x in range(BOARD_WIDTH):
            for _ in range(BOARD_HEIGHT):
                spot = board[y][x]

                # lots of hacky hardcoding to get the light postions
                if y > 7:
                    array_pos = (x * 8) + 15-y
                else:
                    array_pos = (x * 8) + 15-(y+8) + 64

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
                    squares[array_pos] = colors[spot]


                y -= 1
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

def squaresEmitter(squares):
    for i in range(strip.numPixels()):
        color = squares[i]
        strip.setPixelColorRGB(i, color['r'], color['g'], color['b']);
    strip.show()

if __name__ == '__main__':
    # LED strip configuration:
    LED_COUNT      = 128      # Number of LED pixels.
    LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
    LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
    LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
    LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
    strip.begin()
    strip.setBrightness(30)

    while True:
        print "New Tetris class"
        t = Tetris(squaresEmitter)
        result = True

        while result:
            result = t.dropRandom()
