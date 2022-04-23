#from venv import PawnMoves

class GameState():
    def __init__(self):
        self.board= [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        #dictionary
        self.moveFunction ={'p':self.get_pawn_moves,'R':self.get_rook_moves,'B':self.get_bishop_moves,
                            'N':self.get_knight_moves,'Q':self.get_queen_moves,'K':self.get_king_moves}
        self.whiteToMove = True
        self.moveLog = []
        #tracking kings location
        self.whiteKingLocation=(7,4)
        self.blackKingLocation=(0,4)
        self.checkMate=False
        self.staleMate=False
        self.isepPossible=()
        self.epLog=[self.isepPossible]
        self.pins=[]
        self.checks=[]
        self.currentCastleRights=CastleRights(True,True,True,True)
        self.casleRightsLog=[CastleRights(self.currentCastleRights.wks,self.currentCastleRights.bks,
                                          self.currentCastleRights.wqs,self.currentCastleRights.bqs)]

        #pawn=PawnMoves.pawn()

    def make_move(self,move):
        self.board[move.endRow][move.endCol]=move.pieceMoved
        self.board[move.startRow][move.startCol]="--"
        self.moveLog.append(move)
        self.whiteToMove= not self.whiteToMove
        #change kings position
        if move.pieceMoved=="wK":
            self.whiteKingLocation=(move.endRow,move.endCol)
        elif move.pieceMoved=="bK":
            self.blackKingLocation=(move.endRow,move.endCol)
        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol]=move.pieceMoved[0]+'Q'
        #enpassant
        # If its an enpassant move,we capture the pawn and update
        if move.isEnpassantMove:
            self.board[move.startRow][move.startCol]="--"

        if move.pieceMoved[1]=='p' and abs(move.startRow-move.endRow)==2:
            self.isepPossible=((move.startRow+move.endRow)//2,move.startCol)
        else:
            self.isepPossible=()


        #When does castle rights change? Rook and King
        if move.isCastleMove:
            if move.endCol-move.startCol==2:
                self.board[move.endRow][move.endCol-1]=self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1]="--"
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'

        self.epLog.append(self.isepPossible)
        self.update_castle_rights(move)
        self.casleRightsLog.append(CastleRights(self.currentCastleRights.wks, self.currentCastleRights.bks,
                                            self.currentCastleRights.wqs, self.currentCastleRights.bqs))

    '''undo the last move if the player wants to choose again'''

    def checkForPinsAndChecks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
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
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow + direction[0] * i
                endCol = startCol + direction[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():  # first allied piece could be pinned
                            possiblePin = (endRow, endCol, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif endPiece[0] == enemyColor:
                        enemyType = endPiece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemyType == "R") or (4 <= j <= 7 and enemyType == "B") or (
                                i == 1 and enemyType == "p" and (
                                (enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or (
                                enemyType == "Q") or (i == 1 and enemyType == "K"):
                            if possiblePin == ():  # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knightMoves:
            endRow = startRow + move[0]
            endCol = startCol + move[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":  # enemy knight attacking a king
                    inCheck = True
                    checks.append((endRow, endCol, move[0], move[1]))
        return inCheck, pins, checks

    def undo_move(self):

        if len(self.moveLog)!=0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol]=move.pieceMoved
            self.board[move.endRow][move.endCol]=move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol]='--'
                #self.isepPossible = (move.endRow, move.endCol)
                self.board[move.startRow][move.startCol]=move.pieceCaptured

            self.epLog.pop()
            self.isepPossible=self.epLog[-1]

            # if move.pieceMoved[1]=='p' and abs(move.startRow-move.endRow)==2:
            #     self.isepPossible=()
            #castling
            self.casleRightsLog.pop()
            newRights=self.casleRightsLog[-1]
            self.currentCastleRights=CastleRights(newRights.wks,newRights.bks,newRights.wqs,newRights.bqs)
            if move.isCastleMove:
                if move.endCol-move.startCol==2:
                    self.board[move.endRow][move.endCol+1]=self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1]='--'
                else:
                    self.board[move.endRow][move.endCol-2]=self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1]='--'
            self.checkMate=False
            self.staleMate=False

    def update_castle_rights(self,move):
        if move.pieceMoved=='wK':
            self.currentCastleRights.wks=False
            self.currentCastleRights.wqs=False
        elif move.pieceMoved=='bK':
            self.currentCastleRights.bks=False
            self.currentCastleRights.bqs=False
        elif move.pieceMoved=='wR':
            if move.startRow==7:
                if move.startCol==0:
                    self.currentCastleRights.wqs=False
                elif move.startCol==7:
                    self.currentCastleRights.wks=False
        elif move.pieceMoved=='bR':
            if move.startRow==0:
                if move.startCol==0:
                    self.currentCastleRights.bqs=False
                elif move.startCol==7:
                    self.currentCastleRights.bks=False
        #Case: Rook is captured
        if move.pieceCaptured=='wR':
            if move.startRow==7:
                if move.startCol==0:
                    self.currentCastleRights.wqs=False
                elif move.startCol==7:
                    self.currentCastleRights.wks=False
        elif move.pieceCaptured=='bR':
            if move.startRow==0:
                if move.startCol==0:
                    self.currentCastleRights.bqs=False
                elif move.startCol==7:
                    self.currentCastleRights.bks=False


    '''all moves that are valid'''
    def get_valid_moves(self):
        tempep=self.isepPossible

        tempCastleRights=CastleRights(self.currentCastleRights.wks,self.currentCastleRights.bks,
                                        self.currentCastleRights.wqs,self.currentCastleRights.bqs)
        #moves = self.get_possible_moves()
        moves=[]
        self.inCheck,self.pins,self.checks=self.checkForPinsAndChecks()

        if self.whiteToMove:
            kingRow=self.whiteKingLocation[0]
            kingCol=self.whiteKingLocation[1]
        else:
            kingRow=self.blackKingLocation[0]
            kingCol=self.blackKingLocation[1]

        if self.inCheck:
            if len(self.checks)==1:
                moves=self.get_possible_moves()
                check=self.checks[0]
                checkRow=check[0]
                checkCol=check[1]
                pieceChecking=self.board[checkRow][checkCol]
                validSq=[]

                if pieceChecking[1]=="N":
                    validSq=[(checkRow,checkCol)]
                else:
                    for i in range (1,8):
                        validSq=(kingRow+check[2]*i,kingCol+check[3]*i)
                        validSq.append(validSq)
                        if validSq[0]==checkRow and validSq[1]==checkCol:
                            break
                for i in range(len(moves)-1,-1,-1):
                    if moves[i].pieceMoved[1]!='K':
                        if not (moves[i].endRow,moves[i].endCol) in validSq:
                            moves.remove(moves[i])
            else:
                self.get_king_moves(kingRow,kingCol,moves)
        else:
            moves=self.get_possible_moves()
            if self.whiteToMove:
                self.get_castle_moves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
            else:
                self.get_castle_moves(self.blackKingLocation[0],self.blackKingLocation[1],moves)

        # for i in range(len(moves)-1,-1,-1):
        #     self.make_move(moves[i])
        #     self.whiteToMove=not self.whiteToMove
        #     if self.in_check():
        #         moves.remove(moves[i])
        #     self.whiteToMove=not self.whiteToMove
        #     self.undo_move()
            #oppMoves=self.get_possible_moves()
        if len(moves)==0:
            if self.in_check():
                self.checkMate=True
            else:
                self.staleMate=True
        else:
            self.checkMate=False
            self.staleMate=False

        #self.isepPossible=tempep
        self.currentCastleRights=tempCastleRights
        # else:
        #     self.checkMate=False
        #     self.staleMate=False
        return moves

    def in_check(self):
        if self.whiteToMove:
            return self.square_under_attack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.square_under_attack(self.blackKingLocation[0],self.blackKingLocation[1])

    def square_under_attack(self,r,c):
        self.whiteToMove=not self.whiteToMove
        oppMoves=self.get_possible_moves()
        self.whiteToMove=not self.whiteToMove
        for move in oppMoves:
            if move.endRow==r and move.endCol==c:
                return True
        return False

     #all moves that are possible'''
    def get_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                #print(turn)
                if (turn=='w' and self.whiteToMove) or (turn=='b'and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r,c,moves)
        return moves

    def get_pawn_moves(self, r, c, moves):
        piecePinned=False
        pinDir=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDir=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmt=-1
            startRow=6
            enemyColor="b"
            kingRow=kingCol=self.whiteKingLocation
        else:
            moveAmt=1
            startRow=1
            enemyColor="w"
            kingRow,kingCol=self.blackKingLocation

        if self.board[r + moveAmt][c] == "--":  # one square advance
            if not piecePinned or pinDir==(moveAmt,0):
                moves.append(Move((r, c), (r + moveAmt, c), self.board))
                if self.board[r + 2*moveAmt][c] == "--" and r == startRow:
                    moves.append(Move((r, c), (r + 2*moveAmt, c), self.board))

        if c - 1 >= 0:
            if not piecePinned or pinDir ==(moveAmt,-1):
                if self.board[r + moveAmt][c - 1][0] == enemyColor:
                    moves.append(Move((r, c), (r + moveAmt, c - 1), self.board))
                if (r + moveAmt, c - 1) == self.isepPossible:
                    attackingPiece=blockingPiece= False
                    if kingRow==r:
                        if kingRow<c:
                            insideRange=range(kingCol+1,c-1)
                            outsideRange=range(c+1,8)
                        else:
                            insideRange=range(kingCol-1,c,-1)
                            outsideRange=range(c-2,-1,-1)
                        for i in insideRange:
                            if self.board[r][i]!="--":
                                blockingPiece=True
                        for i in outsideRange:
                            square= self.board[r][i]
                            if square[0]==enemyColor and (square[1]=="R" or square[1]=="Q"):
                                attackingPiece=True
                            elif square!="--":
                                blockingPiece=True
                    if not attackingPiece or blockingPiece:
                       moves.append(Move((r, c), (r +moveAmt, c - 1), self.board, isEnpassantMove=True))

        if c + 1 <= 7:
            if not piecePinned or pinDir == (moveAmt, +1):
                if self.board[r + moveAmt][c + 1][0] == enemyColor:
                    moves.append(Move((r, c), (r + moveAmt, c + 1), self.board))
                if (r + moveAmt, c + 1) == self.isepPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingRow < c:
                            insideRange = range(kingCol + 1, c)
                            outsideRange = range(c + 2, 8)
                        else:
                            insideRange = range(kingCol - 1, c+1, -1)
                            outsideRange = range(c - 1, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r + moveAmt, c + 1), self.board, isEnpassantMove=True))

    def get_rook_moves(self,r,c,moves):
        directions = ((-1,0),(0,-1),(1,0),(0,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range (1,8):
                endRow=r+d[0]*i
                endCol=c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece=self.board[endRow][endCol]
                    if endPiece=="--":
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0]==enemyColor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:
                        break
                else:
                    break



    def get_knight_moves(self,r,c,moves):
        directions = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        allyColor="w" if self.whiteToMove else "b"
        for m in directions:
            endRow=r+m[0]
            endCol=c+m[1]
            if 0<=endRow<=7 and 0<=endCol<=7:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]!=allyColor:
                    moves.append(Move((r,c),(endRow,endCol),self.board))


    def get_bishop_moves(self,r,c,moves):
        directions = ((-1,-1),(-1,1),(1,-1),(1,1))
        enemyColor= "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range (1,8):
                endRow=r+d[0]*i
                endCol=c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece=self.board[endRow][endCol]
                    if endPiece=="--":
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0]==enemyColor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:
                        break
                else:
                    break


    def get_queen_moves(self,r,c,moves):
        self.get_rook_moves(r,c,moves)
        self.get_bishop_moves(r,c,moves)


    def get_king_moves(self,r,c,moves):
        directions= ((-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,1),(0,-1))
        allyColor= "w" if self.whiteToMove else "b"
        for i in range (8):
            endRow=r+directions[i][0]
            endCol=c+directions[i][1]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]!=allyColor:
                    moves.append(Move((r,c),(endRow,endCol),self.board))
        # self.get_castle_moves(r,c,moves,allyColor)


    def get_castle_moves(self,r,c,moves):
        if self.square_under_attack(r,c):
            return
        if (self.whiteToMove and self.currentCastleRights.wks) or (not self.whiteToMove and self.currentCastleRights.bks):
            self.get_kingside_castle(r,c,moves)
        if (self.whiteToMove and self.currentCastleRights.wqs) or (not self.whiteToMove and self.currentCastleRights.bqs):
            self.get_queenside_castle(r,c,moves)

    def get_kingside_castle(self,r,c,moves):
        if self.board[r][c+1]=='--' and self.board[r][c+2]=='--':
            if not self.square_under_attack(r,c+1) and not self.square_under_attack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,isCastleMove=True))
    def get_queenside_castle(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c-3]=='--':
            if not self.square_under_attack(r,c-1) and not self.square_under_attack(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board,isCastleMove=True))




class CastleRights():
    def __init__(self,wks,bks,wqs,bqs):
        self.wks=wks
        self.bks=bks
        self.wqs=wqs
        self.bqs=bqs



class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filestoCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filestoCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion=(self.pieceMoved=='wp' and self.endRow==0) or (self.pieceMoved=='bp' and self.endRow==7)


        #self.isEnpassantMove= (self.pieceMoved[1]=='p' and (self.endRow,self.endCol)== isEnpassantMove)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured='wp' if self.pieceMoved=='bp' else 'bp'

        self.isCastleMove = isCastleMove
        self.isCapture=self.pieceCaptured!='--'
        self.moveID=self.startRow*1000+self.startCol*100+self.endRow*10+self.endCol

    '''overriding the equals method'''
    def __eq__(self, other):
        if isinstance(other,Move):
            return self.moveID==other.moveID
        return False

    def get_chess_notation(self):
        if self.isPawnPromotion:
            return self.get_rank_file(self.endRow, self.endCol) + "Q"

        if self.isCastleMove:
            if self.endCol==1:
                return "0-0-0"
            else:
                return "0-0"

        if self.isEnpassantMove:
            return self.get_rank_file(self.startRow,self.startCol)[0] + "x" +self.get_rank_file(self.endRow, self.endCol) + "e.p."

        if self.pieceCaptured!= "--":
            if self.pieceMoved[1]=="p":
                return self.get_rank_file(self.startRow,self.startCol)[0] + "x" +self.get_rank_file(self.endRow, self.endCol)
            else:
                return self.pieceMoved[1] + "x" +self.get_rank_file(self.endRow, self.endCol)
        else:
            if self.pieceMoved[1]=="p":
                return self.get_rank_file(self.endRow, self.endCol)
            else:
                return self.pieceMoved[1] +self.get_rank_file(self.endRow, self.endCol)

    def get_rank_file(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def __str__(self):
        if self.isCastleMove:
            return "0-0" if self.end_col == 6 else "0-0-0"

        endSquare = self.get_rank_file(self.endRow, self.endCol)

        if self.pieceMoved[1] == "p":
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare+ "Q" if self.isPawnPromotion else endSquare

        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare