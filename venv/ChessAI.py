import random

pieceScores={"K":0,"Q":10,"B":3,"N":3,"R":5,"p":1}
CHECKMATE=1000
STALEMATE=0
DEPTH=2
piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

knightScores = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                 [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishopScores = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rookScores = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queenScores = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawnScores = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piecePositionScores = {"wN": knightScores,
                         "bN": knightScores[::-1],
                         "wB": bishopScores,
                         "bB": bishopScores[::-1],
                         "wQ": queenScores,
                         "bQ": queenScores[::-1],
                         "wR": rookScores,
                         "bR": rookScores[::-1],
                         "wp": pawnScores,
                         "bp": pawnScores[::-1]}

def find_random_move(validMoves):
    return random.choice(validMoves)

# def find_best_move(gs,validMoves):
#     turnDetector= 1 if gs.whiteToMove else -1
#     opponentMinMaxScore=CHECKMATE
#     bestPlayerMove=None
#     random.shuffle(validMoves)
#     for playerMove in validMoves:
#         gs.make_move(playerMove)
#         opponentMoves=gs.get_valid_moves()
#         #opponentMaxScore = -CHECKMATE
#         if gs.checkMate:
#             opponentMaxScore=-CHECKMATE
#         elif gs.staleMate:
#             opponentMaxScore=STALEMATE
#         else:
#             opponentMaxScore=-CHECKMATE
#             for opponentMove in opponentMoves:
#                 gs.make_move(opponentMove)
#                 gs.get_valid_moves()
#                 if gs.checkMate:
#                     score=CHECKMATE
#                 elif gs.staleMate:
#                     score=STALEMATE
#                 else:
#                     score=-turnDetector* score_material(gs.board)
#                 if (score>opponentMaxScore):
#                     maxScore=score
#                     bestPlayerMove=playerMove
#                 gs.undo_move()
#         if opponentMaxScore<opponentMinMaxScore:
#             opponentMinMaxScore=opponentMaxScore
#             bestPlayerMove=playerMove
#         gs.undo_move()
#     return bestPlayerMove
def find_best_move(gs,validMoves,return_queue):
    global nextMove, counter
    nextMove=None
    random.shuffle(validMoves)
    counter=0
    find_move_negamaxalphabeta(gs,validMoves,DEPTH,-CHECKMATE,CHECKMATE,1 if gs.whiteToMove else -1)
    return_queue.put(nextMove)


def min_max_algo(gs,validMoves,depth,whiteToMove):
    global nextMove
    if depth==0:
        return score_material(gs.board)

    if whiteToMove:
        maxScore=-CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            nextMoves=gs.get_valid_moves()
            score=min_max_algo(gs,nextMoves,depth-1,False)
            if score>maxScore:
                maxScore=score
                if depth==DEPTH:
                    nextMove=move
            gs.undo_move()
        return maxScore

    else:
        minScore=CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            nextMoves=gs.get_valid_moves()
            score=min_max_algo(gs,nextMoves,depth-1,True)
            if score<minScore:
                minScore=score
                if depth==DEPTH:
                    nextMove=move
            gs.undo_move()
        return minScore

def find_move_negamax(gs,validMoves,depth,turnDetector):
    global nextMove,counter
    counter += 1
    if depth==0:
        return turnDetector*score_board(gs)
    maxScore=-CHECKMATE
    for move in validMoves:
        gs.make_move(move)
        nextMove=gs.get_valid_moves()
        score=-find_move_negamax(gs,nextMove,depth-1,-turnDetector)
        if score>maxScore:
            maxScore=score
            if depth==DEPTH:
                nextMove=move
        gs.undo_move()
    return maxScore

def find_move_negamaxalphabeta(gs,validMoves,depth,alpha,beta,turnDetector):
    global nextMove,counter
    counter+=1
    if depth==0:
        return turnDetector*score_board(gs)
    #move ordering for ab pruning
    maxScore=-CHECKMATE
    for move in validMoves:
        gs.make_move(move)
        nextMove=gs.get_valid_moves()
        score=-find_move_negamaxalphabeta(gs,nextMove,depth-1,-beta,-alpha,-turnDetector)
        if score>maxScore:
            maxScore=score
            if depth==DEPTH:
                nextMove=move
        gs.undo_move()
        #pruning
        if maxScore>alpha:
            alpha=maxScore
        if alpha>=beta:
            break
    return maxScore

def score_board(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.staleMate:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            piece=gs.board[row][col]
            if piece!="--":
                piecePositionScore=0
                if piece[0] == 'w':
                    score += pieceScores[piece[1]] + piecePositionScore
                if piece[0] == 'b':
                    score -= pieceScores[piece[1]] + piecePositionScore
                if piece[1] !='K':
                    piecePositionScore=piecePositionScores[piece][row][col]
    return score

def score_material(board):
    score=0
    for row in board:
        for square in row:
            if square[0]=='w':
                score+=pieceScores[square[1]]
            elif square[0]=='b':
                score-=pieceScores[square[1]]
    return score