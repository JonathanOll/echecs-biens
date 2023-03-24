from options import *
import pygame
from ai import *
from copy import deepcopy, copy
from random import randint

class Position:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
    
    @property
    def algebraic(self):
        return "abcdefgh"[self.x] + str(8 - self.y)

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)
    
    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"


class Game:
    def __init__(self):
        
        self.reset()

        self.win = ""
    
    def next_turn(self):

        self.turn = not self.turn
        self.turn_count += 1
        self.update_moves(True)
        
        if self.check_stalemate():
            self.text = "Pat"
            self.running = False
            checkmate_sound.play()
        elif self.check_checkmate():
            self.text = "Checkmate" + ((" " + self.win) if self.win != "" else "")
            self.running = False
            checkmate_sound.play()

    def add_pawn(self, pos, typ, color):
        p = typ(pos[0], pos[1], color)
        if typ == King:
            self.kings[color] = p
        self.pawns.append(p)
        self.sprites.add(p)

    def get_pawn(self, pos):
        for p in self.pawns:
            if p.pos == pos: return p
        return None
    
    def is_valid(self, pos):
        return (0 <= pos.x < 8) and (0 <= pos.y < 8)
    
    def draw(self, screen):
        for x in range(8):
            for y in range(8):
                color = last_move_color[(y + x) % 2] if self.last_move and Position(x, y) == self.last_move else target_color[(y + x) % 2] if self.selected and Position(x, y) in self.selected.get_moves() else highlight_color[(y + x) % 2] if Position(x, y) in self.hightlights else grid_colors[(y + x) % 2]
                pygame.draw.rect(screen, color, (screen_width / 2 - grid_size / 2 + x / 8 * grid_size, screen_height / 2 - grid_size // 2 + y / 8 * grid_size, grid_size / 8, grid_size / 8))

        self.sprites.draw(screen)
        
        if pygame.mouse.get_pressed()[0] == 1 and self.selected:
            x, y = pygame.mouse.get_pos()
            color = last_move_color[(self.selected.pos.y + self.selected.pos.x) % 2] if self.last_move and Position(self.selected.pos.x, self.selected.pos.y) == self.last_move else target_color[(self.selected.pos.y + self.selected.pos.x) % 2] if self.selected and Position(self.selected.pos.x, self.selected.pos.y) in self.selected.get_moves() else highlight_color[(self.selected.pos.y + self.selected.pos.x) % 2] if Position(self.selected.pos.x, self.selected.pos.y) in self.hightlights else grid_colors[(self.selected.pos.y + self.selected.pos.x) % 2]
            pygame.draw.rect(screen, color, (screen_width / 2 - grid_size / 2 + self.selected.pos.x / 8 * grid_size, screen_height / 2 - grid_size // 2 + self.selected.pos.y / 8 * grid_size, grid_size / 8, grid_size / 8))
            screen.blit(self.selected.get_image(), (x - grid_size // 16, y - grid_size // 16))
        
        if self.promote:
            screen.blit(pygame.transform.scale(pygame.image.load("res/promote.png"), (grid_size // 8, int(grid_size / 8 / 113 * 509))), (self.promote.rect.x, self.promote.rect.y))

        font = pygame.font.SysFont(None, 85)
        img = font.render(self.text, True, (0, 0, 0))
        screen.blit(img, (screen_width // 2 - img.get_width() // 2, screen_height // 2 - img.get_height() // 2))

    def tick(self):
        if not self.running : return

        if self.ai[self.turn]:
            """if self.promote:
                self.change(self, Queen)"""
            self.ai[self.turn].play(self)

    def click(self, pos):
        x, y = pos
        if self.promote:
            if self.promote.rect.x <= x <= self.promote.rect.x + grid_size // 8:
                yy = (y - self.promote.rect.y) // 87
                if yy > 3:
                    self.promote = None
                    self.next_turn()
                else:
                    self.promote.change(self, [Queen, Knight, Rook, Bishop][yy])
                    self.promote = None
                    self.next_turn()
            else:
                self.promote = None
                self.next_turn()
        else:
            xx = (x - (screen_width//2-grid_size//2)) // (grid_size // 8)
            yy = (y - (screen_height//2-grid_size//2)) // (grid_size // 8)
            pos = Position(xx, yy)
            if self.selected and pos in self.selected.get_moves():
                self.selected.move(pos, self)
                self.selected = None
            else:
                self.selected = self.get_pawn(pos) if (self.get_pawn(pos) and self.get_pawn(pos).color) == self.turn else None
            self.pressed = (xx, yy)
    
    def release(self, pos):
        x, y = pos
        xx = (x - (screen_width//2-grid_size//2)) // (grid_size // 8)
        yy = (y - (screen_height//2-grid_size//2)) // (grid_size // 8)
        pos = Position(xx, yy)
        if (xx, yy) != self.pressed:
            if self.selected and pos in self.selected.get_moves():
                self.selected.move(pos, self)
                self.selected = None
        self.pressed = (-1, -1)
    
    def right_click(self, pos):
        x, y = pos
        xx = (x - (screen_width//2-grid_size//2)) // (grid_size // 8)
        yy = (y - (screen_height//2-grid_size//2)) // (grid_size // 8)
        pos = Position(xx, yy)
        if pos in self.hightlights:
            self.hightlights.remove(pos)
        else:
            self.hightlights.append(pos)
    
    def check_stalemate(self):
        for pawn in self.pawns:
            if pawn.color != self.turn: continue
            if pawn.get_moves(): return False
        return not self.check(self.kings[self.turn].pos)
    
    def check_checkmate(self):
        for pawn in self.pawns:
            if pawn.color != self.turn: continue
            if pawn.get_moves(): return False
        if self.win != "":
            return True
        return self.check(self.kings[self.turn].pos)

    def update_moves(self, check=True):
        for pawn in self.pawns:
            pawn.update_moves(self, check)

    def reset(self):
        self.pawns = []
        self.selected = None
        self.pressed = (-1, -1)
        self.kings = {True: None, False: None}
        self.turn = False
        self.sprites = pygame.sprite.Group()
        self.hightlights = []
        self.ai = { False: None, True: Random_Bot(True) }
        self.running = True
        self.text = ""
        self.last_move = None
        self.turn_count = 0
        self.castling = {True: [True, True], False: [True, True]}  # [Grand Roc, Petit Roc]
        self.halfplay = 0
        self.promote = None
        self.history = ""
        self.sound = False

    def load(self, string):
        
        pawns_list = {"p": Pawn, "r": Rook, "n": Knight, "q": Queen, "k": King, "b": Bishop}

        self.pawns.clear()
        self.sprites.empty()

        x, y = 0, 0

        for line in string.split(" ")[0].split("/")[:8]:
            for char in line:
                if char.lower() in pawns_list.keys():
                    self.add_pawn((x, y), pawns_list[char.lower()], char in "kqrbnp")
                x += int(char) if char in "123456789" else 1
            x = 0
            y += 1
        
        self.turn = string.split(" ")[1] == "b"

        self.castling[False] = ["Q" in string.split(" ")[2], "K" in string.split(" ")[2]]
        self.castling[False] = ["q" in string.split(" ")[2], "k" in string.split(" ")[2]]

        self.halfplay = int(string.split(" ")[4])
        
        self.turn_count = int(string.split(" ")[5])

        self.update_moves()
    
    def get_fen(self):

        pawns_list = {"pawn": "p", "rook": "r", "knight": "n", "queen": "q", "king": "k", "bishop": "b"}

        res = ""

        grid = [[None] * 8 for i in range(8)]

        for pawn in self.pawns:
            grid[pawn.pos.y][pawn.pos.x] = pawns_list[pawn.name] if pawn.color else pawns_list[pawn.name].upper()
        
        for y in grid:
            count = 0
            for x in y:
                if x != None:
                    if count == 0:
                        res += x
                    else:
                        res += str(count)
                        count = 0
                else:
                    count += 1
            if count != 0:
                res += str(count)
                count = 0
            res += "/"
        
        res = res[::-1].replace("/", "", 1)[::-1]

        res += " " + ("b" if self.turn else "w")

        res += " " + "K" * self.castling[False][1] + "Q" * self.castling[False][0] + "k" * self.castling[True][1] + "q" * self.castling[True][0]

        res += " - " + str(self.halfplay) + " " + str(self.turn_count)

        return res

    def get_network_inputs(self):
        
        values = {"pawn": 1, "knight": 2, "bishop": 3, "rook": 5, "queen": 9, "king": 500}
        
        res = [0] * 64

        for y in range(8):
            for x in range(8):
                pawn = self.get_pawn(Position(x, y))
                if pawn != None:
                    res[8 * y + x] = (-1 if pawn.color else 1) * values[pawn.name]
        
        return res


    def check(self, pos, ignore=[]):

        if self.get_pawn(pos) == None : return

        color = self.get_pawn(pos).color

        for pawn in self.pawns:

            if pawn in ignore: continue
            
            if pos != pawn.pos and pawn.color != color and pos in pawn.instant_moves(self):

                return True
        
        return False
    
    def get_algebraic(self):

        return self.history

    def load_algebraic(self, history):
        turn = self.turn
        for move in history.split(" "):
            typ = [Knight, Bishop, Rook, Queen, King, Pawn][-1 if move[0] not in "NBRQK" else "NBRQK".index(move[0])]
            
            m = Position("abcdefgh".index(move[-2]), 8 - int(move[-1]))
            
            for pawn in self.pawns:

                if pawn.color == turn and isinstance(pawn, typ) and m in pawn.get_moves():

                    pawn.move(m, self)
                    break

            turn = not turn

    def copy(self):
        res = Game()
        res.pawns = [copy(self.pawns[i]) for i in range(len(self.pawns))]
        res.selected = self.selected
        res.pressed  = self.pressed 
        res.kings = self.kings
        res.turn = self.turn
        res.sprites  = self.sprites 
        res.hightlights = self.hightlights
        res.ai = self.ai
        res.running  = self.running 
        res.text = self.text
        res.last_move = self.last_move
        res.turn_count = self.turn_count
        res.castling = self.castling
        res.halfplay = self.halfplay
        res.promote  = self.promote 
        res.history  = self.history 
        return res



class Piece(pygame.sprite.Sprite):
    def __init__(self):

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(pygame.image.load("res/" + ("black" if self.color else "white") + "/" + self.name + ".png"), (grid_size // 8, grid_size // 8))

        self.moves = []
        
        self.algebraic = ""

    @property
    def rect(self):
        return pygame.Rect(screen_width // 2 - grid_size // 2 + self.pos.x * grid_size // 8, screen_height // 2 - grid_size // 2 + self.pos.y * grid_size // 8, grid_size // 8, grid_size // 8)

    def update_moves(self, grid):
        return []
    
    def get_moves(self):
        return self.moves
    
    def move(self, pos, grid, next_turn=True):
        
        last_pos = self.pos.algebraic

        castling = False

        # gérer les grands et petits rocs
        if isinstance(self, King):
            if grid.castling[self.color][1] and pos.x == 6:
                grid.get_pawn(Position(7, pos.y)).move(Position(5, pos.y), grid, False)
                castling = True
            elif grid.castling[self.color][0] and pos.x == 2:
                grid.get_pawn(Position(0, pos.y)).move(Position(3, pos.y), grid, False)
                castling = True
            grid.castling[self.color] = [False, False]
        elif isinstance(self, Rook):
            if self.pos == Position(0, 0) and self.color:
                grid.castling[True][1] = False
            elif self.pos == Position(7, 0) and self.color:
                grid.castling[True][0] = False
            elif self.pos == Position(0, 7) and not self.color:
                grid.castling[False][0] = False
            elif self.pos == Position(7, 7) and not self.color:
                grid.castling[False][1] = False
        
        grid.halfplay += 1
        self.pos = pos

        promote = False

         # gérer les promote
        if isinstance(self, Pawn) and ((self.color and pos.y == 7) or (not self.color and pos.y == 0)):
            self.promote(grid)
            promote = True

        capture = False
        self.update_moves(grid)

        for pawn in grid.pawns:
            if self.pos == pawn.pos and self != pawn:
                if isinstance(pawn, King):
                    grid.win = "blanc" if self.color else "noir"
                capture = True
                pawn.move(Position(randint(0, 7), randint(0, 7)), grid, next_turn=False)
                if grid.sound and next_turn : capture_sound.play()
                grid.halfplay = 0
                grid.history += self.algebraic + "x" + self.pos.algebraic + " "
        if not capture:
            if castling:
                if grid.sound : castling_sound.play()
            elif grid.check(grid.kings[not self.color].pos):
                if grid.sound : check_sound.play()
            else:
                if grid.sound : move_sound.play()
                grid.history += self.algebraic + self.pos.algebraic + " "


        grid.last_move = self.pos
        if next_turn and not promote:
            grid.next_turn()

        if isinstance(self, Pawn): grid.halfplay = 0

    def get_image(self):
        return self.image
    
    def remove_check(self, res, grid):
        
        last_pos = Position(self.pos.x, self.pos.y)

        to_remove = []

        for move in res:

            ignore = [] if not grid.get_pawn(move) else [ grid.get_pawn(move) ]

            self.pos = move

            if grid.check(grid.kings[self.color].pos, ignore=ignore):
                to_remove.append(move)
            
        for a in to_remove:
            res.remove(a)

        self.pos = last_pos

    def instant_moves(self, grid):

        last_moves = deepcopy(self.moves)

        self.update_moves(grid, False)

        res = deepcopy(self.moves)

        self.moves = last_moves

        return res
    
    def promote(self, grid):
        grid.promote = self
    
    def change(self, grid, typ):
        print(typ)
        grid.pawns.remove(self)
        grid.sprites.remove(self)
        grid.add_pawn((self.pos.x, self.pos.y), typ, self.color)


class Pawn(Piece):
    def __init__(self, x, y, color):
        self.pos = Position(x, y)
        self.color = color
        self.name = "pawn"
        super().__init__()
        self.algebraic = ""
    
    def update_moves(self, grid, check=True):
        res = []

        move = Position(0, 1 if self.color else -1)
        if grid.is_valid(self.pos + move) and grid.get_pawn(self.pos + move) == None:
            res.append(self.pos + move)
            if self.pos.y == (1 if self.color else 6):
                move = Position(0, 2 if self.color else -2)
                if grid.is_valid(self.pos + move) and grid.get_pawn(self.pos + move) == None:
                    res.append(self.pos + move)

        move = Position(1, 1 if self.color else -1)
        if grid.is_valid(self.pos + move) and grid.get_pawn(self.pos + move) and grid.get_pawn(self.pos + move).color != self.color:
            res.append(self.pos + move)

        move = Position(-1, 1 if self.color else -1)
        if grid.is_valid(self.pos + move) and grid.get_pawn(self.pos + move) and grid.get_pawn(self.pos + move).color != self.color:
            res.append(self.pos + move)
        
        if check:
            self.remove_check(res, grid)

        self.moves = res


class Knight(Piece):
    def __init__(self, x, y, color):
        self.pos = Position(x, y)
        self.color = color
        self.name = "knight"
        super().__init__()
        self.algebraic = "N"

    
    def update_moves(self, grid, check=True):
        res = []
        moves = [(-2, -1), (-2, 1), (-1, -2), (1, -2), (2, -1), (2, 1), (-1, 2), (1, 2)]

        for m in moves:
            move = Position(m[0], m[1])
            if grid.is_valid(self.pos + move) and (grid.get_pawn(self.pos + move) == None or grid.get_pawn(self.pos + move).color != self.color):
                res.append(self.pos + move)
        
        if check:
            self.remove_check(res, grid)

        self.moves = res


class Bishop(Piece):
    def __init__(self, x, y, color):
        self.pos = Position(x, y)
        self.color = color
        self.name = "bishop"
        super().__init__()
        self.algebraic = "B"

    
    def update_moves(self, grid, check=True):
        res = []
        
        for m in [Position(1, 1), Position(-1, 1), Position(-1, -1), Position(1, -1)]:
            move = Position(0, 0)
            while True:
                move += m
                if grid.is_valid(self.pos + move):
                    if grid.get_pawn(self.pos + move) != None:
                        if  grid.get_pawn(self.pos + move).color != self.color:
                            res.append(self.pos + move)
                        break
                    else:
                        res.append(self.pos + move)
                else:
                    break
        
        if check:
            self.remove_check(res, grid)
        
        self.moves = res

class Rook(Piece):
    def __init__(self, x, y, color):
        self.pos = Position(x, y)
        self.color = color
        self.name = "rook"
        super().__init__()
        self.algebraic = "R"

    
    def update_moves(self, grid, check=True):
        res = []
        
        for m in [Position(0, 1), Position(0, -1), Position(1, 0), Position(-1, 0)]:
            move = Position(0, 0)
            while True:
                move += m
                if grid.is_valid(self.pos + move):
                    if grid.get_pawn(self.pos + move) != None:
                        if grid.get_pawn(self.pos + move).color != self.color:
                            res.append(self.pos + move)
                        break
                    else:
                        res.append(self.pos + move)
                else:
                    break
        
        if check:
            self.remove_check(res, grid)

        self.moves = res


class Queen(Piece):
    def __init__(self, x, y, color):
        self.pos = Position(x, y)
        self.color = color
        self.name = "queen"
        super().__init__()
        self.algebraic = "Q"

    
    def update_moves(self, grid, check=True):
        res = []
        
        for m in [Position(1, 1), Position(-1, 1), Position(-1, -1), Position(1, -1), Position(0, 1), Position(0, -1), Position(1, 0), Position(-1, 0)]:
            move = Position(0, 0)
            while True:
                move += m
                if grid.is_valid(self.pos + move):
                    if grid.get_pawn(self.pos + move) != None:
                        if grid.get_pawn(self.pos + move).color != self.color:
                            res.append(self.pos + move)
                        break
                    else:
                        res.append(self.pos + move)
                else:
                    break
        if check:
            self.remove_check(res, grid)

        self.moves = res


class King(Piece):
    def __init__(self, x, y, color):
        self.pos = Position(x, y)
        self.color = color
        self.name = "king"
        super().__init__()
        self.algebraic = "K"

    
    def update_moves(self, grid, check=True):
        
        res = []
        
        for y in range(-1, 2):
            for x in range(-1, 2):
                if x == y == 0 : continue
                move = Position(x, y)
                if grid.is_valid(self.pos + move) and (grid.get_pawn(self.pos + move) == None or grid.get_pawn(self.pos + move).color != self.color):
                    res.append(self.pos + move)
        
        if check:
            # Petit Roc
            if self.color:
                if grid.castling[self.color][1] and grid.get_pawn(Position(5, 0)) == grid.get_pawn(Position(6, 0)) == None \
                    and not grid.check(Position(4, 0)) and not grid.check(Position(5, 0)) and not grid.check(Position(6, 0)) and not grid.check(Position(7, 0)):
                    res.append(Position(6, 0))
            else:
                if grid.castling[self.color][1] and grid.get_pawn(Position(5, 7)) == grid.get_pawn(Position(6, 7)) == None \
                    and not grid.check(Position(4, 7)) and not grid.check(Position(5, 7)) and not grid.check(Position(6, 7)) and not grid.check(Position(7, 7)):
                    res.append(Position(6, 7))
            # Grand Roc
            if self.color:
                if grid.castling[self.color][0] and grid.get_pawn(Position(1, 0)) == grid.get_pawn(Position(2, 0)) == grid.get_pawn(Position(3, 0)) == None \
                    and not grid.check(Position(0, 0)) and not grid.check(Position(1, 0)) and not grid.check(Position(2, 0)) and not grid.check(Position(3, 0)) and not grid.check(Position(4, 0)):
                    res.append(Position(2, 0))
            else:
                if grid.castling[self.color][0] and grid.get_pawn(Position(1, 7)) == grid.get_pawn(Position(2, 7)) == grid.get_pawn(Position(3, 7)) == None \
                    and not grid.check(Position(0, 7)) and not grid.check(Position(1, 7)) and not grid.check(Position(2, 7)) and not grid.check(Position(3, 7)) and not grid.check(Position(4, 7)):
                    res.append(Position(2, 7))
        
            self.remove_check(res, grid)

        self.moves = res

