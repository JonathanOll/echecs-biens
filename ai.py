from random import choice
from random import uniform
from time import time
from options import *
from neural_network import NeuralNetwork


class Random_Bot:
    def __init__(self, color):
        self.color = color
        self.wait = -1

    def play(self, grid):
        if self.wait == -1:
            self.wait = time() + uniform(ai_play_time[0], ai_play_time[1])
        if self.wait > time():
            return
        while True:
            pawn = choice(grid.pawns)
            if pawn.color == self.color:
                moves = pawn.get_moves()
                if moves:
                    move = choice(moves)
                    pawn.move(move, grid)
                    self.wait = -1
                    return

class Max_Gain_Bot:
    score = { "pawn": 1, "bishop": 3, "knight": 3, "rook": 5, "queen": 9, "king": 9 }

    def __init__(self, color):
        self.color = color
        self.wait = -1

    def play(self, grid):
        if self.wait == -1:
            self.wait = time() + uniform(ai_play_time[0], ai_play_time[1])
        if self.wait > time():
            return
        
        best_pawn = None
        best_pawn_score = -1
        best_move_pos = None

        for pawn in grid.pawns:
            if pawn.color != self.color : continue
            for move in pawn.get_moves():
                if grid.get_pawn(move) == None:
                    score = 0
                else:
                    score = Max_Gain_Bot.score[grid.get_pawn(move).name]
                if score > best_pawn_score:
                    best_pawn_score = score
                    best_pawn = pawn
                    best_move_pos = move

        best_pawn.move(best_move_pos, grid)
        self.wait = -1
        return

class Network_Bot:
    score = { "pawn": 1, "bishop": 3, "knight": 3, "rook": 5, "queen": 9, "king": 9 }

    def __init__(self, color):
        self.color = color
        self.wait = -1
        self.network = NeuralNetwork([64, 72, 32, 1])

    def play(self, grid):
        if self.wait == -1:
            self.wait = time() + uniform(ai_play_time[0], ai_play_time[1])
        if self.wait > time():
            return
        
        best_pawn = None
        best_pawn_score = -1
        best_move_pos = None

        for pawn in grid.pawns:
            if pawn.color != self.color : continue
            for move in pawn.get_moves():
                score = self.network.forward(grid.get_network_inputs())
                if score > best_pawn_score:
                    best_pawn_score = score
                    best_pawn = pawn
                    best_move_pos = move

        best_pawn.move(best_move_pos, grid)
        self.wait = -1
        return

class Max_Gain_Bot_Depth:

    max_depth = 1
    score = { "pawn": 1, "bishop": 3, "knight": 3, "rook": 5, "queen": 9, "king": 9 }

    def __init__(self, color):
        self.color = color
        self.wait = -1

    def play(self, base_grid, turn=None, depth=0):

        print(depth)

        grid = base_grid.copy()

        if turn == None:
            turn = self.color

        if self.wait == -1:
            self.wait = time() + uniform(ai_play_time[0], ai_play_time[1])
        if self.wait > time():
            return
        
        if depth == 0:
            best_move = None
            best_pawn = None
            best_score = -1

            for pawn in grid.pawns:
                if pawn.color != turn: continue
                for move in pawn.get_moves():
                    grid = base_grid.copy()
                    pawn.move
                    score = self.play(grid, not turn, depth+1)
                    print(score)
                    if score > best_score:
                        best_pawn = pawn
                        best_score = score
                        best_move = move
            
            best_pawn.move(best_move, base_grid)
            self.wait = -1
            print(best_score)
            return
            
        elif depth >= Max_Gain_Bot_Depth.max_depth:
            
            score = 0
            count = 0

            for pawn in grid.pawns:
                if pawn.color != turn: continue
                score += len(pawn.get_moves())
                for move in pawn.get_moves():
                    p = grid.get_pawn(move)
                    if p != None:
                        score += 10 * Max_Gain_Bot_Depth.score[p.name]
                count += 1

            return score / (count if count != 0 else 1)
            
        else:

            score = 0
            count = 0

            for pawn in grid.pawns:
                if pawn.color != turn: continue
                for move in pawn.get_moves():
                    pawn.move(move, grid)
                    score += self.play(grid, not turn, depth+1)
                    count += 1
            
            return (count if count != 0 else 1)

            
        





