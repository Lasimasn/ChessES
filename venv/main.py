from venv import ChessEngine,ChessAI
import pygame as p
import sys
from multiprocessing import Process,Queue

WIDTH = HEIGHT = 512
DIMENSION = 8
LOG_WIDTH=250
LOG_HEIGHT=HEIGHT
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES ={}


'''images are loaded here'''
def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR", "bp", "bR", "bN", "bB", "bQ", "bK", "bB", "bN",
              "bR"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

'''main driver '''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH+LOG_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    #print(gs.board)
    validMoves= gs.get_valid_moves()
    moveMode = False #when the user makes a valid move and the game state changes, then we should regenerate valid moves
    animate = False
    load_images()  # only operated once
    running = True
    sqSelected = ()
    playerClicks = []  # two tuples [(5,3),(3,2)]
    gameOver=False
    AIthinking=False
    moveLogFont = p.font.SysFont("Calibri", 12, False, False)
    moveUndone=False
    moveFinderProcess=None
    player1=True
    player2=False


    while running:
        humanTurn=(gs.whiteToMove and player1) or (not gs.whiteToMove and player2)
        for e in p.event.get():
            if e.type == p.QUIT:
                #running = False
                p.quit()
                sys.exit()

            #mouse handlers for the game
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()  # (x,y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col>=8:  # undo / deselect on clicking twice
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2 and humanTurn:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        #print(move.get_chess_notation())
                        for i in range (len(validMoves)):
                            if move == validMoves[i]:
                                gs.make_move(validMoves[i])
                                moveMode=True
                                animate=True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMode:
                            playerClicks=[sqSelected]
            #key handlers
            elif e.type==p.KEYDOWN:
                if e.key==p.K_z: #on key press z
                    gs.undo_move()
                    moveMode=True
                    gameOver=False
                    animate=False
                    if AIthinking:
                        moveFinderProcess.terminate()
                        AIthinking=False
                    moveUndone=True
                if e.key==p.K_r:
                    gs=ChessEngine.GameState()
                    validMoves=gs.get_valid_moves()
                    sqSelected=()
                    playerClicks=[]
                    moveMode=False
                    animate=False
                    gameOver=False
                    #validMoves=gs.get_valid_moves()
                    if AIthinking:
                        moveFinderProcess.terminate()
                        AIthinking=False
                    moveUndone=True

        #find AI move
        if not gameOver and not humanTurn and not moveUndone:
            if not AIthinking:
                AIthinking=True
                return_queue=Queue()
                moveFinderProcess=Process(target=ChessAI.find_best_move,args=(gs,validMoves,return_queue))
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():
                AIMove=return_queue.get()
                if AIMove is None:
                    AIMove=ChessAI.find_random_move(validMoves)
                gs.make_move(AIMove)
                moveMode=True
                animate=True
                AIthinking=False

        if moveMode:
            if animate:
                animateMove(gs.moveLog[-1],screen,gs.board,clock)
            validMoves=gs.get_valid_moves()
            moveMode=False
            animate=False
            moveUndone=False

        draw_game_state(screen,gs,validMoves,sqSelected)#,moveLogFont)

        if not gameOver:
            draw_moveLog(screen,gs,moveLogFont)

        if gs.checkMate or gs.staleMate:
            gameOver=True
            text="Stalemate" if gs.staleMate else "Black wins" if gs.whiteToMove else "White wins"
            draw_endgame_text(screen,text)

        clock.tick(MAX_FPS)
        p.display.flip()


def draw_game_state(screen,gs,validMoves,sqSelected):
    #to draw squares on the board
    draw_board(screen)
    #puts images of pieces on board
    highlight_squares(screen,gs,validMoves,sqSelected)
    draw_pieces(screen,gs.board)
    #draw_moveLog(screen,gs,moveLogFont)

def draw_board(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlight_squares(screen,gs,validMoves,sqSelected):
    if (len(gs.moveLog)) > 0:
        lastMove = gs.moveLog[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('green'))
        screen.blit(s, (lastMove.endCol * SQ_SIZE, lastMove.endRow * SQ_SIZE))
    if sqSelected!=():
        r,c=sqSelected
        if gs.board[r][c][0]==('w'if gs.whiteToMove else 'b'):
            s=p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            s.fill(p.Color('green'))
            for move in validMoves:
                if move.startRow==r and move.startCol==c:
                    screen.blit(s,(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_moveLog(screen,gs,font):
    moveLogRect=p.Rect(WIDTH,0,LOG_WIDTH,LOG_HEIGHT)
    p.draw.rect(screen,p.Color("black"),moveLogRect)
    moveLog=gs.moveLog
    moveTexts=[]
    for i in range(0,len(moveLog),2):
        moveString=str(i//2+1)+". "+str(moveLog[i])+" "
        if i+1<len(moveLog):
            moveString+=str(moveLog[i+1])+" "
        moveTexts.append(moveString)
    padding=5
    movesPerRow=3
    lineSpacing=2
    textY=padding
    for i in range(0,len(moveTexts),movesPerRow):
        text=""
        for j in range(movesPerRow):
            if i+j<len(moveTexts):
                text+=(moveTexts[i+j])
        textObject = font.render(text, True, p.Color('white'))
        textLocation = moveLogRect.move(padding,textY)
        screen.blit(textObject, textLocation)
        textY+=textObject.get_height()+lineSpacing

def animateMove(move,screen,board,clock):
    colors = [p.Color(235, 235, 208), p.Color(119, 148, 85)]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        row, col = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        draw_board(screen)
        draw_pieces(screen, board)
        #self.chessView.drawPieces(self.chessModel.board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == "b" else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #if move.pieceMoved != '--':
        screen.blit(IMAGES[move.pieceMoved], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def draw_endgame_text(screen,text):
    font=p.font.SysFont("Calibri",32,True,False)
    textObject=font.render(text,False,p.Color('Black'))
    textLocation=p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH/2 - (textObject.get_width())/2 , HEIGHT/2-(textObject.get_height())/2)
    screen.blit(textObject,textLocation)
    textObject=font.render(text,False,p.Color("Red"))
    screen.blit(textObject,textLocation.move(2,2))

if __name__ == "__main__":
    main()

