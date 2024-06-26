"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

cached_states = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    dark_score, light_score = get_score(board)
    if color == 1:
        return dark_score - light_score
    elif color == 2:
        return light_score - dark_score
    else:
        eprint("Invalid color")
        return 0

# Better heuristic value of board
# The implementation of this heuristic is based on the following website: 
# https://kartikkukreja.wordpress.com/2013/03/30/heuristic-function-for-reversiothello/
def compute_heuristic(board, color):
    n = len(board)
    
    # Coin parity
    # Difference in the number of current scores
    dark_score, light_score = get_score(board)
    coin_parity = dark_score - light_score
    
    # Stability
    # Placements are classified into 3 categories: stable, semi-stable, and unstable
    # Stable: A disc that cannot be flipped (corners are always stable)
    # Semi-stable: A disc that can be flipped, but will not be flipped in the next move
    # Unstable: A disc that can be flipped in the next move
    dark_stable = 0
    light_stable = 0
    for i in range(n):
        for j in range(n):
            # Corners are always stable
            if [i, j] in [[0, 0], [0, n-1], [n-1, 0], [n-1, n-1]]:
                if board[i][j] == 1:
                    dark_stable += 5
                elif board[i][j] == 2:
                    light_stable += 5
            # Edges are semi-stable
            elif i == 0 or i == n-1 or j == 0 or j == n-1:
                if board[i][j] == 1:
                    dark_stable += 2
                elif board[i][j] == 2:
                    light_stable += 2
            # Other placements are considered unstable
            else:
                if board[i][j] == 1:
                    dark_stable += 1
                elif board[i][j] == 2:
                    light_stable += 1
    stable = dark_stable - light_stable
    
    # Weighted sum of the four components
    utility = 0.3 * coin_parity + 0.7 * stable
    
    if color == 1:
        return utility
    elif color == 2:
        return -utility

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    
    if caching == 1 and (board, color) in cached_states:
        return cached_states[(board, color)]
        
    possible_moves = get_possible_moves(board, color)
    if not possible_moves or limit == 0:
        return (None, compute_utility(board, color))
    
    best_move, best_utility = None, float('inf')
    for move in possible_moves:
        new_board = play_move(board, color, move[0], move[1])
        _, utility = minimax_max_node(new_board, 3-color, limit-1, caching)
        if not best_move or utility < best_utility:
            best_move, best_utility = move, utility
    
    if caching == 1:
        cached_states[(board, color)] = (best_move, best_utility)
               
    return best_move, best_utility

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    
    if caching == 1 and (board, color) in cached_states:
        return cached_states[(board, color)]
    
    possible_moves = get_possible_moves(board, color)
    if not possible_moves or limit == 0:
        return (None, compute_utility(board, color))
    
    best_move, best_utility = None, float('-inf')
    for move in possible_moves:
        new_board = play_move(board, color, move[0], move[1])
        _, utility = minimax_min_node(new_board, 3-color, limit-1, caching)
        if not best_move or utility > best_utility:
            best_move, best_utility = move, utility
    
    if caching == 1:
        cached_states[(board, color)] = (best_move, best_utility)
    
    return best_move, best_utility
    
def select_move_minimax(board, color, limit, caching = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    """
    move, _ = minimax_max_node(board, color, limit, caching)
    return move

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    
    if caching == 1 and (board, color, alpha, beta) in cached_states:
        return cached_states[(board, color, alpha, beta)]
    
    possible_moves = get_possible_moves(board, color)
    if not possible_moves or limit == 0:
        return (None, compute_utility(board, color))
        
    if ordering == 1:
        possible_moves = sorted(possible_moves, key = lambda x: compute_utility(play_move(board, color, x[0], x[1]), color))
    
    best_move, best_utility = None, float('inf')
    for move in possible_moves:
        new_board = play_move(board, color, move[0], move[1])
        _, utility = alphabeta_max_node(new_board, 3-color, alpha, beta, limit-1, caching, ordering)
        if not best_move or utility < best_utility:
            best_move, best_utility = move, utility
        
        if beta > best_utility:
            beta = best_utility
            if beta <= alpha:
                break
                
    if caching == 1:
        cached_states[(board, color, alpha, beta)] = (best_move, best_utility)
        
    return best_move, best_utility

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    
    if caching == 1 and (board, color, alpha, beta) in cached_states:
        return cached_states[(board, color, alpha, beta)]
    
    possible_moves = get_possible_moves(board, color)
    if not possible_moves or limit == 0:
        return (None, compute_utility(board, color))
    
    if ordering == 1:
        possible_moves = sorted(possible_moves, key = lambda x: -compute_utility(play_move(board, color, x[0], x[1]), color))
    
    best_move, best_utility = None, float('-inf')
    for move in possible_moves:
        new_board = play_move(board, color, move[0], move[1])
        _, utility = alphabeta_min_node(new_board, 3-color, alpha, beta, limit-1, caching, ordering)
        if not best_move or utility > best_utility:
            best_move, best_utility = move, utility
        
        if alpha < best_utility:
            alpha = best_utility
            if beta <= alpha:
                break
    
    if caching == 1:
        cached_states[(board, color, alpha, beta)] = (best_move, best_utility)
         
    return best_move, best_utility

def select_move_alphabeta(board, color, limit, caching = 0, ordering = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations. 
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations. 
    """
    move, _ = alphabeta_max_node(board, color, float('-inf'), float('inf'), limit, caching, ordering)
    return move

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI") # First line is the name of this AI
    arguments = input().split(",")
    
    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light. 
    limit = int(arguments[1]) #Depth limit
    minimax = int(arguments[2]) #Minimax or alpha beta
    caching = int(arguments[3]) #Caching 
    ordering = int(arguments[4]) #Node-ordering (for alpha-beta only)

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (ordering == 1): eprint("Node Ordering is ON")
    else: eprint("Node Ordering is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True: # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over.
            print
        else:
            board = eval(input()) # Read in the input and turn it into a Python
                                  # object. The format is a list of rows. The
                                  # squares in each row are represented by
                                  # 0 : empty square
                                  # 1 : dark disk (player 1)
                                  # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1): #run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: #else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)
            
            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()
