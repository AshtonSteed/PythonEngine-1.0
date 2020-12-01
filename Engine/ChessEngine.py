# This class is responsible for storing all the info about the current state of a chess game. It will also handle determining valid moves and keep a move log.
import operator
import random
class GameState():
    def __init__(self):
        #board is 8x8 2d list, each element has 2 characters.
        #The first character is the color, b or w,
        #The second character represents the type, k q r b n or p
        #"--" represents an empty space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.boardBackup = []
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.whiteMate = False
        self.blackMate = False
        self.staleMate = False
        self.enpassantPossible = () #coordinates for the square where an en passant can capture
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
        self.whiteKingCastle = False
        self.blackKingCastle = False



    ''' Takes a move as a parameter and executes, doesnt work for castling, en passant, or promotion'''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.whiteToMove = not self.whiteToMove #swap players
        #update kings location
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        #enpassant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' #capturing pawn
        #update of enpassant variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: #2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.endCol)
        else:
            self.enpassantPossible = ()
        #castling move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #copies rook to new square
                self.board[move.endRow][move.endCol+1] = '--' #erase old rook
            else: #queenside
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # copies rook to new square
                self.board[move.endRow][move.endCol - 2] = '--'  # erase old rook
            if not self.whiteToMove:
                self.whiteKingCastle = True
            else:
                self.blackKingCastle = True
        #castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

        #draw by triplication
        if move in self.moveLog:
            for i in range(len(self.boardBackup)):
                if self.boardBackup[i] == self.board:
                    self.staleMate = True
                    #print("Draw by repetition")
            self.boardBackup.append(self.board)

        #print(move.moveID)
        self.moveLog.append(move)  # log the move





    ''' Undo the last move made'''
    def undoMove(self):
        if len(self.moveLog) != 0: #make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            #update kings locaton
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            #undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' #leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            #undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            #undoing castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRight = self.castleRightsLog[-1] #sets the current castle rights to last in list after the pop+
            #undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #kingside
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else: #queenside
                    self.board[move.endRow][move.endCol -2] = self.board[move.endRow][move.endCol +1]
                    self.board[move.endRow][move.endCol +1] = '--'
                if self.whiteToMove:
                    self.whiteKingCastle = False
                else:
                    self.blackKingCastle = False

            #undo triplication and boardBackup
            if move in self.moveLog:
                self.boardBackup.pop()
                self.staleMate = False



    def updateCastleRights(self, move): #updates castling rights
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 7: #left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 0:
                    self.currentCastlingRight.wks = False
        elif move. pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 7:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 0:
                    self.currentCastlingRight.bks = False




    '''
    All moves that are playable
    '''
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: #only one check, block or move
                moves = self.getAllPossibleMoves()
                check = self.checks[0] #checks info
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] #piece causing check
                validSquares = [] #squares that pieces can move to
                # if knight, capture knight or move king
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) #check 2 and 3 are the directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: #piece end checks
                            break
                #get rid of any moves that dont work
                for i in range(len(moves) - 1, -1, -1): #go through list backwards
                    if moves[i].pieceMoved[1] != 'K': #doesnt move king
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: #move doest block check or capture
                            moves.remove(moves[i])
            else: #double check, has to move
                self.getKingMoves(kingRow, kingCol, moves)

            if moves == []: #checkmate detection, if in check with no valid moves, thats game
                if self.whiteToMove == True:
                    self.whiteMate = True
                    #print("Black Wins!")
                else:
                    self.blackMate = True
                    #print("White Wins!")
        else: #not in check
            moves = self.getAllPossibleMoves()
            if moves == []: #stalemate detection, no moves but not in check
                self.staleMate = True
                print("Stalemate")
        return moves


    ''' 
    All moves that can be played, ignoring check 
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): # number of rows
            for c in range(len(self.board[r])): #number of columns in row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves
    '''
    Get all the pawn moves for the pawn at row and col, add to list
    '''
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove: #white pawn moves
            if self.board[r-1][c] == "--": #single square advancement
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--": #double square starting move
                        moves.append(Move((r, c), (r - 2, c), self.board))
            if c-1 >= 0:
                if not piecePinned or pinDirection == (-1, -1):
                    if self.board[r-1][c-1][0] == 'b': #enemy piece to capture to the left
                        moves.append(Move((r, c), (r - 1, c -1), self.board))
                    elif (r-1, c-1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            if c+1 <= 7:
                if not piecePinned or pinDirection == (-1, 1):
                    if self.board[r-1][c+1][0] == 'b': #enemy piece to capture to the right
                        moves.append(Move((r, c), (r - 1, c +1), self.board))
                    elif (r-1, c+1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))
        else: #Black pawn moves
            if self.board[r + 1][c] == "--":  # single square advancement
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":  # double square starting move
                        moves.append(Move((r, c), (r + 2, c), self.board))
            if c-1 >= 0:      #black diagonal captures
                if not piecePinned or pinDirection == (1, -1):
                    if self.board[r+1][c-1][0] == 'w': #enemy piece to capture to the left
                        moves.append(Move((r, c), (r + 1, c -1), self.board))
                    elif (r + 1, c - 1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c+1 <= 7:
                if not piecePinned or pinDirection == (1, 1):
                    if self.board[r+1][c+1][0] == 'w': #enemy piece to capture to the right
                        moves.append(Move((r, c), (r + 1, c +1), self.board))
                    elif (r + 1, c + 1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))
        #get pawn premotions later, also en-passant

    '''
    Get all the rook moves for rook at row and col, add to list
    '''
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #directions of movement
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #checks if on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": #empty square
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: #enemy square
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: #if same color piece break
                            break
                else:
                    break






    '''
    Get all the knight moves for rook at row and col, add to list
    '''
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, 2), (1, -2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    '''
    Get all the bishop moves for rook at row and col, add to list
    '''
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    '''
    Get all the Queen moves for rook at row and col, add to list
    '''
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    '''
    Get all the King moves for rook at row and col, add to list
    '''
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1,-1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        mateCounter = 8
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # not an ally piece
                    # check for checks on square
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        self.getCastleMoves(r, c, moves)

    '''
    Generate all valid castle moves for king at (r, c)
    '''
    def getCastleMoves(self, r, c, moves):
        if self.inCheck:
            return #can't caslte when in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] =='--':
            if not self.SquareUnderAttack(r, c+1) and not self.SquareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))



    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] =='--' and self.board[r][c-3] == '--':
            if not self.SquareUnderAttack(r, c-1) and not self.SquareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))



    '''
    Returns if the player is in check, list of pins and checks
    '''
    def checkForPinsAndChecks(self):
        pins = [] #squares where allied piece is pinned
        checks = [] #squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        #check outward for pins and checks
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () #reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == (): #1st blocking piece, could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: #2nd piece, cant be pinned
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        #5 possibilities, big ol conditional
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == (): #no piece blocking, check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: #piece blocked, pin
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break #off board
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, 2), (1, -2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    def SquareUnderAttack(self, r, c):   #checks to see if any piece is attacking the square at r, c
        threat = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = r
            startCol = c
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = r
            startCol = c
        # check outward for pins and checks
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # 1st blocking piece, could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # 2nd piece, cant be pinned
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possibilities, big ol conditional
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (
                                        enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():  # no piece blocking, threat
                                threat = True
                            else:  # piece blocked, pin
                                threat = False
                        else:
                            break
                else:
                    break  # off board
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, 2), (1, -2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    threat = True
        return threat


    #chess computer moment
    def minMax(self, depth, alpha, beta):  # takes in the state being minmaxed, the player of evaluation, and the depth, as well as alpha and beta for minmax pruning
        if depth == 0 or self.whiteMate or self.blackMate or self.staleMate:  # bottom line eval
              # evaluates the board
            Value = self.evaluatePosition()
            self.whiteMate = False
            self.blackMate = False
            self.staleMate = False
            return Value

        if self.whiteToMove:
            maxEval = -100000
            #moves = self.getValidMoves() #old move gen
            moves = sorted(self.getValidMoves(), key=operator.attrgetter('moveValue'), reverse=True) #new move gen, sorts list based on potential move value, helps alpha beta
            for i in range(len(moves)):
                self.makeMove(moves[i])
                eval = self.minMax(depth - 1, alpha, beta) #recursion with 1 less depth, heart of minimax alg
                self.undoMove()
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return maxEval

        else:
            minEval = 100000
            moves = sorted(self.getValidMoves(), key=operator.attrgetter('moveValue'), reverse=True)
            for i in range(len(moves)):
                self.makeMove(moves[i])
                eval = self.minMax(depth - 1, alpha, beta)
                self.undoMove()
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return minEval

    def evaluatePosition1(self):
        return 0
    def evaluatePosition(self): #Placeholder for the positional evaluation
        materialEvals = {'wK': 10000, 'wQ': 1000, 'wR': 525, 'wB': 350, 'wN': 350, 'wp': 100,
                         'bK': -10000, 'bQ': -1000, 'bR': -525, 'bB': -350, 'bN': -350, 'bp': -100,
                         '--': 0}  # used for material evaluation
        value = 0
        mobilityValue = 5
        castleValue = 85
        if self.staleMate or self.whiteMate or self.blackMate: #gives the end game positions a value, should discourage repetiton
            value = 10000*(self.blackMate) -10000*(self.whiteMate)
        else:
            for r in range(0, 8): #evaluates each piece on the board with the weights in the dictionary way above
                for c in range(0, 8):
                    value = value + materialEvals[self.board[r][c]]
                    #print(value)
            if not self.whiteToMove:
                value = value - len(self.getValidMoves()) * mobilityValue
                self.whiteToMove = not self.whiteToMove
                value = value + len(self.getValidMoves()) * mobilityValue
                self.whiteToMove = not self.whiteToMove
                #print(value)
            else:
                value = value + len(self.getValidMoves()) * mobilityValue
                self.whiteToMove = not self.whiteToMove
                value = value - len(self.getValidMoves()) * mobilityValue
                self.whiteToMove = not self.whiteToMove
                #print(value)
            #(self.whiteKingCastle)
            #print(self.blackKingCastle)
            value = value + castleValue * (self.whiteKingCastle) - castleValue * (self.blackKingCastle)
            #print(value)

        return value

    def computerMove(self, depth): #looks at all possible moves, minimax's each one with depth-1(so depth makes sense), returns best move for each color
        if len(self.moveLog) <= 7:
            return self.openingTree(depth)
        else:
            return self.generateMove(depth)

    '''
    Opening tree below, could use alot of work, format so is easier to expand
    '''


    def betterOpeningTree(self, depth): #will be a revised version of the opening tree, might work better, maybe not.
        moveIDs = []
        for i in len(self.moveLog): #makes the moveIDs list into a group
            moveIDs.append(self.moveLog[i].moveID)
        pass

    def openingTree(self, depth): #no clue how I'd use a dict here, using a big ol if tree. Should be fine, only one use per click, only in early game
        if self.whiteToMove:
            if self.moveLog == []:
                moves = [Move((6, 4), (4, 4), self.board), Move((6, 3), (4, 3), self.board)] #king and queen pawn openings
                return random.choice(moves)
            elif self.moveLog[0].moveID == 6444: #White Kings pawn
                if len(self.moveLog) == 2: #3rd move responses
                    if self.moveLog[1].moveID == 1232: #Kings pawn game
                        return Move((7, 6), (5, 5), self.board) #Kings knight opening
                    elif self.moveLog[1].moveID == 1434:  # Sicilian
                        moves = [Move((7, 6), (5, 5), self.board), Move((7, 1), (5, 2), self.board)]  # Main sicilian line and closed sicilian
                        return random.choice(moves)
                    elif self.moveLog[1].moveID == 1222:  # Caro-Kahn
                        return Move((6, 3), (4, 3), self.board) # Main Caro Kahn line
                    else:
                        return self.generateMove(depth)
                elif len(self.moveLog) == 4: #5th move responses
                    if self.moveLog[2].moveID == 7655 and self.moveLog[1].moveID == 1232:
                        return Move((7, 5), (4, 2), self.board) #kings pawn to Italian, tree end
                    elif self.moveLog[2].moveID == 7655:
                        return Move((6, 3), (4, 3), self.board) #Open Sicilian End
                    else:
                        return self.generateMove(depth)
                else:
                    return self.generateMove(depth)
            elif self.moveLog[0].moveID == 6343: #queens pawn responses
                if len(self.moveLog) == 2: #3rd move
                    if self.moveLog[1].moveID == 1333 or self.moveLog[1].moveID == 625:
                        return  Move((6, 2), (4, 2), self.board) #Queens gambit/Indian
                    else:
                        return self.generateMove(depth)
                else:
                    return self.generateMove(depth)

            else:
                return self.generateMove(depth)

        else:
            if self.moveLog[0].moveID == 6444: #kings pawn response tree
                if len(self.moveLog) == 1: #second move responses
                    moves = [Move((1, 2), (3, 2), self.board), Move((1, 4), (3, 4), self.board), Move((1, 2), (2, 2), self.board)] #Kings pawn, sicilian, and Caro-Kahn
                    return random.choice(moves)
                elif len(self.moveLog) == 3: #4th move responses
                    if self.moveLog[2].moveID == 7655 and self.moveLog[1].moveID == 1232:
                        return Move((0, 1), (2, 2), self.board) #kings pawn cont
                    elif self.moveLog[2].moveID == 7655:
                        return Move((1, 3), (2, 3), self.board) #Open Sicilian
                    elif self.moveLog[2].moveID == 7152:
                        return Move((0, 1), (2, 2), self.board) #Closed Sicilian end
                    elif self.moveLog[2].moveID == 6343:
                        return Move((1, 3), (3, 3), self.board) #Caro Kahn end
                    else:
                        return self.generateMove(depth)
                else:
                    return self.generateMove(depth)

            elif self.moveLog[0].moveID == 6343: #Queen pawns response tree
                if len(self.moveLog) == 1:
                    moves = [Move((0, 6), (2, 5), self.board), Move((1, 3), (3, 3), self.board)]  # Indians and queens' pawn
                    return random.choice(moves)
                else:
                    return self.generateMove(depth)
            else:
                return self.generateMove(depth)




    def generateMove(self, depth):
        #self.evaluations = 0  # variable that keeps track of each evaluation, mostly so I can debug alpha beta
        moveMax = -100000
        moveMin = 100000
        moves = self.getValidMoves()
        #print(moves)
        bestWhite = (random.choice(moves))
        bestBlack = (random.choice(moves))
        for i in range(len(moves)):
            self.makeMove(moves[i])
            moveValue = self.minMax(depth - 1, -100000, 100000)
            if moveValue >= moveMax:
                moveMax = moveValue
                bestWhite = moves[i]
            elif moveValue <= moveMin:
                moveMin = moveValue
                bestBlack = moves[i]
            self.undoMove()
        if not self.whiteMate and not self.blackMate and not self.staleMate:
            if self.whiteToMove:
                print(moveMax)
                return bestWhite
            else:
                print(moveMin)
                return bestBlack





class Move():
    # maps keys to values, key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
    moveEvals = {'p': 7, 'N': 5, 'B': 5, 'Q': 6, 'R': 4,
                      'K': 6, '-': 0}  # sorting values, should help with efficiency, focused on midgame, might figure out how to switch these values for endgame later
    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveValue = self.moveEvals[self.pieceMoved[1]] + 4*(self.pieceCaptured != '--') #sets move value to the evals above, and if a piece is captured, value goes up
        #pawn promotion
        self.isPawnPromotion = ((self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7))
        #enpassant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        #castling
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        #pseudo chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

'''
Castling stuff 
'''

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


#psuedo code for computer






