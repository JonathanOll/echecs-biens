import pygame.image, pygame.transform, pygame.mixer

grid_colors = [(119, 149, 86), (235, 236, 224)]
target_color = [(230, 119, 86), (230, 150, 120)]
highlight_color = [(230, 190, 68), (230, 217, 119)]
last_move_color = [(186, 202, 43), (246, 246, 105)]

screen_width, screen_height = 1280, 720
grid_size = 696

ai_play_time = (0.5, 0.80)

sprites = []


pygame.mixer.init()

capture_sound = pygame.mixer.Sound('res/sounds/capture.mp3')
move_sound = pygame.mixer.Sound('res/sounds/move.mp3')
check_sound = pygame.mixer.Sound('res/sounds/check.mp3')
castling_sound = pygame.mixer.Sound('res/sounds/castling.mp3')
checkmate_sound = pygame.mixer.Sound('res/sounds/checkmate.mp3')












for a in ["white", "black"]:
    for b in ["king", "queen", "rook", "bishop", "knight", "pawn"]:
        sprites.append(pygame.transform.scale(pygame.image.load("res/" + a + "/" + b + ".png"), (grid_size // 8, grid_size // 8)))

sprites.insert(6, None)
sprites.insert(6, None)

