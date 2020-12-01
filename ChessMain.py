# This is the main driver file, Will do user input and display GameState object

import pygame as p
from Engine import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8 #number of boards, chess is 8x8
SQ_Size = HEIGHT // DIMENSION #Size of the chess squares
MAX_FPS = 15
IMAGES = {}
 #3 fits in a 3 minute game, 4 in 10, 5 in an hour. more efficient engine and ai would make depth be able to go higher


'''
Initialize a global dictionary of images. Only call once
'''
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Chess/" + piece + ".png"), (SQ_Size, SQ_Size))
    #Note: Image can be accessed by saying 'IMAGES['wp']' or equivalent


'''
Main driver, will handle user input and graphics updates
'''
def main():
    DEPTH = 4
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made
    loadImages() #One time thing, before the while loop
    running = True
    sqSelected = () #initally, no sqaare selected, keeps track of last click,(row, col)
    playerClicks = [] #keep track of player clicks (two tuples: [(6,4), (4,4)]
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse stuff
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #(X Y) location of mouse
                col = location[0]//SQ_Size
                row = location[1]//SQ_Size
                if sqSelected == (row, col):
                    sqSelected = () #deslect
                    playerClicks = [] #clear clicks
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2: #after the second click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            sqSelected = () #reset the clicks
                            playerClicks = []
                            print(move.getChessNotation())
                            print(gs.evaluatePosition())
                    if not moveMade:
                        playerClicks = [sqSelected]
                #key stuff
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when z is pressed
                    gs.undoMove()
                    moveMade = True
                elif e.key == p.K_c: #eval and move when key pressed
                    move = gs.computerMove(DEPTH)
                    gs.makeMove(move)
                    moveMade = True
                    print(move.getChessNotation())
                elif e.key == p.K_KP0:
                    DEPTH = 0
                elif e.key == p.K_KP1:
                    DEPTH = 1
                elif e.key == p.K_KP2:
                    DEPTH = 2
                elif e.key == p.K_KP3:
                    DEPTH = 3
                elif e.key == p.K_KP4:
                    DEPTH = 4
                elif e.key == p.K_KP5:
                    DEPTH = 5

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()
'''
Responsible for all graphics in gamestate
'''
def drawGameState(screen, gs):
    drawBoard(screen) #draw squares on the board
    #add in piece highlighting/move suggestions later
    drawPieces(screen, gs.board) #draw pieces on top of squares

''' Draw the squares on the board, top left is always light'''
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c) % 2]
            p.draw.rect(screen, color, p.Rect(c*SQ_Size, r*SQ_Size, SQ_Size, SQ_Size))

'''draws the pieces using the gamestate'''
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #not an empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_Size, r*SQ_Size, SQ_Size, SQ_Size))

if __name__ == "__main__":
    main()
